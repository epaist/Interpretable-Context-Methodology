"""The HCES gate for one ICM stage (layer 3): pick the reference sections a stage task needs.

  python -m hces.gate <stage folder> --task "what the agent is about to do" --yes [--out kept.md] [--budget N]

Reads the stage's Inputs table. Rows whose file sits under an output folder are upstream work and load
whole; rows under a templates folder are copied, so they load whole; a row with no file path is the user.
Every other row is reference material: its files are cut into heading sections, JEV judges every section
against a task rubric, and code keeps what passes the frozen stage 04 cutoffs. There is no token budget by default:
the stage 07 pilot lost critical rule sections to a 2000-token budget, and cutoffs alone matched hand scope. --out
writes the kept sections, in file order, for the agent to read instead of the whole references. An empty kept set
means the references hold nothing for this task.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

from hces import sections as S
from hces.rollup import Cutoffs, fill
from hces.rubric import for_question

ARM = "gate"
VARIANT = "sections"
BUDGET = 2000  # the pilot's budgeted arm; kept for reruns
OPEN = 10**9  # no budget: the v1 default (pilot gate-open arm)
ROW = re.compile(r"^\|(.+)\|$")
PATH = re.compile(r"`([^`]+)`")
QUOTED = re.compile(r'"([^"]+)"')


def inputs_table(context_md: Path) -> list[dict]:
    """Rows of the '## Inputs' table: source, location, scope, why. Fails on a missing or malformed table."""
    lines = context_md.read_text(encoding="utf-8").splitlines()
    starts = [i for i, l in enumerate(lines) if l.strip() == "## Inputs"]
    if len(starts) != 1:
        raise ValueError(f"{context_md}: expected one '## Inputs' heading, found {len(starts)}")
    rows = []
    for line in lines[starts[0] + 1:]:
        if line.startswith("## "):
            break
        m = ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if cells[0] == "Source" or set(cells[0]) <= set("-: "):
            continue
        if len(cells) != 4:
            raise ValueError(f"{context_md}: Inputs row needs 4 cells, has {len(cells)}: {line}")
        rows.append(dict(zip(("source", "location", "scope", "why"), cells)))
    if not rows:
        raise ValueError(f"{context_md}: Inputs table has no rows")
    return rows


def resolve(location: str, stage_dir: Path, root: Path) -> Path | None:
    """The file or folder a row names. A leading slash means the repo root. None for a row with no path."""
    m = PATH.search(location)
    if not m:
        return None
    p = m.group(1)
    return (root / p.lstrip("/")) if p.startswith("/") else (stage_dir / p).resolve()


def kind(path: Path | None) -> str:
    if path is None:
        return "user"
    parts = set(path.parts)
    if "output" in parts:
        return "upstream"
    if "templates" in parts:
        return "template"
    return "reference"


def upstream_stage(path: Path) -> str:
    """The stage folder an upstream row reads from, e.g. 01-discovery."""
    parts = path.parts
    return parts[parts.index("output") - 1]


def reference_files(rows: list[dict], stage_dir: Path, root: Path) -> list[tuple[Path, str]]:
    """(file, scope) for each reference row. Fails if a named file does not exist."""
    out = []
    for r in rows:
        p = resolve(r["location"], stage_dir, root)
        if kind(p) != "reference":
            continue
        if not p.is_file():
            raise FileNotFoundError(f"Inputs row names a missing reference file: {p}")
        out.append((p, r["scope"]))
    return out


def hand_scope(units: list[dict], scope: str) -> list[dict]:
    """What the stage author asked for: quoted section names, or the whole file."""
    names = QUOTED.findall(scope)
    if not names:
        return units
    kept = [u for u in units if any(n in u["trail"] for n in names)]
    missing = [n for n in names if not any(n in u["trail"] for u in units)]
    if missing:
        raise ValueError(f"Section/Scope names headings that do not exist: {missing}")
    return kept


def task_rubric(qid: str, stage_title: str, task: str):
    question = f"What rules, patterns, formats or examples must an agent follow to do this: {stage_title}. {task}"
    return for_question(qid, question, "a rule, pattern, format or example this work must follow",
                        "building an ICM workspace stage")


def frozen() -> Cutoffs:
    from hces.exam import output_dir as exam_dir

    return Cutoffs(**json.loads((exam_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])


def judgments(store, qid: str) -> dict | None:
    """Stored judgments for this task, or None if it was never judged."""
    from hces.arms import judged

    if store.db.execute("SELECT 1 FROM runs WHERE arm=? AND question_id=? AND variant=?", (ARM, qid, VARIANT)).fetchone():
        return judged(store, qid, VARIANT, ARM)[0]
    return None


def judge_units(store, cfg, rub, units: list[dict]) -> tuple[dict, float]:
    """JEV judges every section once per task; stored insert-only, reused on rerun. Returns (judgments, cost)."""
    from hces.judge import JevJudge
    from hces.judge_all import billed_tokens
    from hces.store import new_run_id
    from hces.timing import RunClock
    from hces.units import Unit

    have = judgments(store, rub.rubric_id)
    if have is not None:
        return have, 0.0
    batch = [Unit(u["id"], u["text"], source="reference", tokens=u["tokens"]) for u in units]
    store.add_rubric(rub)
    run_id, started = new_run_id(), time.time()
    judge_ = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    with RunClock() as clock:
        with clock.span("access"):
            pass
        with clock.span("analysis"):
            js = judge_.judge(rub.task, rub, batch)
        with clock.span("response"):
            store.add_judgments(run_id, rub, js)
    failed = len({j.unit_id for j in js if j.failed})
    if failed > len(batch) // 10:
        raise RuntimeError(f"{failed} of {len(batch)} JEV requests failed on {rub.rubric_id}")
    tokens = billed_tokens(js)
    c = tokens * cfg.price_per_million / 1e6
    store.add_run({"run_id": run_id, "arm": ARM, "variant": VARIANT, "k": len(batch), "question_id": rub.rubric_id,
                   "budget": BUDGET, "judge_model": cfg.jev_model, "rubric_id": rub.rubric_id,
                   "rubric_version": rub.version, "access_ms": clock.ms["access"], "analysis_ms": clock.ms["analysis"],
                   "response_ms": clock.ms["response"], "peak_rss_mb": clock.peak_rss_mb, "tokens_in": tokens,
                   "cost_usd": c, "started_at": started, "notes": {"requests": len(batch), "failed_units": failed}})
    return judgments(store, rub.rubric_id), c


def keep(units: list[dict], j: dict, rub, budget: int, cut: Cutoffs) -> list[dict]:
    """Fill the budget from judged sections, then return them in file order (how a reader expects them)."""
    from hces.arms import scored
    from hces.units import Unit

    by_id = {u["id"]: Unit(u["id"], "", tokens=u["tokens"]) for u in units}
    kept = {s.unit_id for s, _ in fill(scored(by_id, j, rub, [u["id"] for u in units]), budget, cut)[0]}
    return [u for u in units if u["id"] in kept]


def stage_units(stage_dir: Path, root: Path, count) -> tuple[list[dict], list[dict]]:
    """(all reference sections, the hand-scoped subset) for one stage."""
    rows = inputs_table(stage_dir / "CONTEXT.md")
    allu, hand = [], []
    for path, scope in reference_files(rows, stage_dir, root):
        us = S.build(count, root, [path])
        allu += us
        hand += hand_scope(us, scope)
    return allu, hand


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.gate")
    ap.add_argument("stage", type=Path)
    ap.add_argument("--task", required=True)
    ap.add_argument("--budget", type=int, default=OPEN, help="token budget (default: none, cutoffs only)")
    ap.add_argument("--out", type=Path, help="write the kept sections here as markdown")
    ap.add_argument("--yes", action="store_true", help="required: JEV judging spends credit")
    a = ap.parse_args(argv)
    if not a.yes:
        raise SystemExit("This spends JEV credit; pass --yes")
    from hces.config import load
    from hces.passages import TokenCounter
    from hces.store import Store

    cfg = load()
    stage = a.stage.resolve()
    units, _ = stage_units(stage, S.root(), TokenCounter())
    rub = task_rubric(f"gate/{stage.name}/{hashlib.sha256(a.task.encode()).hexdigest()[:10]}", stage.name, a.task)
    j, c = judge_units(Store(cfg.results_store), cfg, rub, units)
    kept = keep(units, j, rub, a.budget, frozen())
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        head = [f"<!-- HCES gate for {stage.name}: {len(kept)} of {len(units)} sections kept for the task below. -->",
                f"<!-- Task: {' '.join(a.task.split())} -->", ""]
        body = [f"## {u['id']}\n\n{u['text'].strip()}\n" for u in kept] or ["Nothing in the references is needed for this task.\n"]
        a.out.write_text("\n".join(head + body), encoding="utf-8", newline="\n")
    print(json.dumps({"sections": len(units), "tokens": sum(u["tokens"] for u in units), "kept": [u["id"] for u in kept],
                      "kept_tokens": sum(u["tokens"] for u in kept), "jev_cost": round(c, 4)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
