"""Stage 07 pilot: the gate on a real ICM workspace (workspace-builder), three arms per stage task.

  python -m hces.pilot --judge --yes            JEV judges reference sections for every task (cents)
  python -m hces.pilot --estimate               token counts and projected Claude cost, no calls
  python -m hces.pilot --run --yes --cap 10     Opus 5.5 runs every stage, whole first, then gate and hand
  python -m hces.pilot --grade --yes            blind grading against each stage's audit
  python -m hces.pilot --report                 output/pilot.md

Arms differ only in reference material (layer 3). whole: every reference file whole. hand: the Inputs table's
Section/Scope as written. gate: HCES picks sections (frozen cutoffs, 2000 tokens). Layers 0 to 2, templates and
upstream outputs load whole in every arm; upstream is always the whole arm's output, so stage N+1 compares
only the references. An arm whose reference set equals whole's reuses whole's output and grade.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import time
from pathlib import Path

from hces import gate as G
from hces import sections as S
from hces.endtoend import PRICES, cost, usage

MODEL = "claude-opus-5-5"
ARMS = ("whole", "gate", "hand", "gate-open")  # gate-open: frozen cutoffs, no token budget (added after the first run)
MAX_TOKENS = 32000
TOKEN_RATIO = 1.3  # Claude tokens per bge token, from stage 05 bills
OUT_GUESS = {"01-discovery": 3000, "02-mapping": 4000, "03-scaffolding": 15000, "04-questionnaire-design": 2500,
             "05-validation": 3000}
FILE_BLOCK = re.compile(r'<file path="([^"]+)">\n?(.*?)</file>', re.S)
PLACEHOLDER = re.compile(r"\{\{([^{}\n`]*)\}\}")  # one line, no braces or backticks: prose like "scan for `{{` patterns" is not a placeholder
GOOD_PLACEHOLDER = re.compile(r"^[?/]?[A-Z0-9_]+$")
DASHES = ("\u2014", "\u2013")
INSTRUCTIONS = (
    "You are the agent running one stage of an ICM workspace. The stage's CONTEXT.md is your contract: follow its "
    "Process, meet its Audit, and write its Outputs. You cannot run tools, search, open other files or talk to the "
    "user. The user's workflow description is everything the user will say. Where a step asks the user something or "
    "a checkpoint waits for approval, decide as the description suggests and record each decision in an "
    "'Assumptions' section of the main output file. Use only the material given to you. Write every output file as "
    '<file path="path relative to this stage\'s output folder">content</file>, and write nothing outside file blocks.'
)
GRADER = (
    "You grade the output of one stage of an ICM workspace. You get the stage contract (CONTEXT.md), the user's "
    "workflow description, every input the stage had, all reference files in full, and the output. Judge each "
    "listed check strictly against its pass condition and the reference rules: pass is true only if the output "
    "fully meets it. Then give an overall score from 1 (unusable) to 5 (ready to use as is), and one reason."
)
STAGE05_CHECKS = [("Check coverage", "The report covers every numbered check in the stage Process"),
                  ("Call accuracy", "Each pass or fail call is right for the workspace given; no real violation is "
                                    "missed and none is invented")]
REFERENCE_CHECK = ("Reference rules", "The output follows every rule in the reference files that applies to this "
                                      "stage's work")


def wb() -> Path:
    return S.root() / "workspaces" / "workspace-builder"


def stage_dirs() -> list[Path]:
    out = sorted(p for p in (wb() / "stages").iterdir() if p.is_dir())
    if len(out) != 5:
        raise RuntimeError(f"Expected 5 workspace-builder stages, found {len(out)}")
    return out


def home() -> Path:
    return S.root() / "workspaces" / "hces-lab" / "stages" / "07-pilot"


def out_dir() -> Path:
    return home() / "output"


def domains() -> dict[str, str]:
    """## slug headings in references/domains.md, body = the user's workflow description."""
    text = (home() / "references" / "domains.md").read_text(encoding="utf-8")
    out = {}
    for block in text.split("\n## ")[1:]:
        slug, _, body = block.partition("\n")
        out[slug.strip()] = body.strip()
    if len(out) != 2:
        raise ValueError(f"domains.md should hold 2 domains, has {len(out)}")
    return out


def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def audit_checks(stage: Path) -> list[tuple[str, str]]:
    """(check, pass condition) from the stage's Audit table, plus the reference-rules check."""
    body = section((stage / "CONTEXT.md").read_text(encoding="utf-8"), "Audit")
    rows = []
    for line in body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] != "Check" and not set(cells[0]) <= set("-: "):
            rows.append((cells[0], cells[1]))
    if not rows:
        if stage.name != "05-validation":
            raise ValueError(f"{stage.name}: no Audit table")
        rows = list(STAGE05_CHECKS)
    return rows + [REFERENCE_CHECK]


def task_text(stage: Path, domain_desc: str) -> str:
    ctx = (stage / "CONTEXT.md").read_text(encoding="utf-8")
    first = next(l for l in ctx.splitlines()[1:] if l.strip())
    return f"{first} Domain: {domain_desc.split('.')[0]}. Steps: {' '.join(section(ctx, 'Process').split())}"


def qid(domain: str, stage: Path) -> str:
    return f"pilot/{domain}/{stage.name}"


def layers() -> str:
    files = [S.root() / "CLAUDE.md", wb() / "CLAUDE.md", wb() / "CONTEXT.md"]
    return "\n\n".join(f'<file path="{f.relative_to(S.root()).as_posix()}">\n{f.read_text(encoding="utf-8")}\n</file>'
                       for f in files)


def templates(stage: Path) -> str:
    out = []
    for r in G.inputs_table(stage / "CONTEXT.md"):
        p = G.resolve(r["location"], stage, S.root())
        if G.kind(p) == "template":
            out.append(f'<file path="{p.relative_to(S.root()).as_posix()}">\n{p.read_text(encoding="utf-8")}\n</file>')
    return "\n\n".join(out)


def run_path(domain: str, stage: str, arm: str) -> Path:
    return out_dir() / "runs" / domain / stage / f"{arm}.md"


def upstream(domain: str, stage: Path) -> str:
    """Whole-arm outputs of the stages this one reads, as written. Fails if one has not run."""
    names = []
    for r in G.inputs_table(stage / "CONTEXT.md"):
        p = G.resolve(r["location"], stage, S.root())
        if G.kind(p) == "upstream" and G.upstream_stage(p) not in names:
            names.append(G.upstream_stage(p))
    parts = []
    for n in names:
        f = run_path(domain, n, "whole")
        if not f.exists():
            raise FileNotFoundError(f"{domain}: {stage.name} needs {n} output; run stages in order")
        parts.append(f'<stage-output stage="{n}">\n{f.read_text(encoding="utf-8")}\n</stage-output>')
    return "\n\n".join(parts)


def reference_sets(store, cfg, count) -> dict[str, dict[str, list[dict]]]:
    """{qid: {arm: units}} for every task. gate needs stored judgments (run --judge first)."""
    cut, out = G.frozen(), {}
    for d, desc in domains().items():
        for st in stage_dirs():
            allu, hand = G.stage_units(st, S.root(), count)
            rub = G.task_rubric(qid(d, st), st.name, task_text(st, desc))
            j = G.judgments(store, rub.rubric_id)
            if j is None:
                raise SystemExit(f"{rub.rubric_id} not judged; run --judge first")
            out[qid(d, st)] = {"whole": allu, "hand": hand, "gate": G.keep(allu, j, rub, G.BUDGET, cut),
                               "gate-open": G.keep(allu, j, rub, 10**9, cut)}
    return out


def judge_all(store, cfg, count) -> int:
    spent = 0.0
    for d, desc in domains().items():
        for st in stage_dirs():
            allu, _ = G.stage_units(st, S.root(), count)
            rub = G.task_rubric(qid(d, st), st.name, task_text(st, desc))
            _, c = G.judge_units(store, cfg, rub, allu)
            spent += c
            print(json.dumps({"task": rub.rubric_id, "sections": len(allu), "cost": round(c, 4)}), flush=True)
    for q, arms in reference_sets(store, cfg, count).items():
        print(q, {a: (len(u), sum(x["tokens"] for x in u)) for a, u in arms.items()}, [u["id"] for u in arms["gate"]])
    print(json.dumps({"jev_spent": round(spent, 4)}))
    return 0


def refs_text(units: list[dict]) -> str:
    return "\n\n".join(f'<section id="{u["id"]}">\n{u["text"]}\n</section>' for u in units) or "(none)"


def prompt(domain: str, desc: str, stage: Path, units: list[dict]) -> tuple[list[dict], str]:
    system = [{"type": "text", "text": INSTRUCTIONS},
              {"type": "text", "text": f"Routing files (layers 0 to 2):\n\n{layers()}\n\n"
                                       f'<file path="{(stage / "CONTEXT.md").relative_to(S.root()).as_posix()}">\n'
                                       f'{(stage / "CONTEXT.md").read_text(encoding="utf-8")}\n</file>'}]
    content = (f"<user-workflow-description>\n{desc}\n</user-workflow-description>\n\n"
               f"<upstream>\n{upstream(domain, stage) or '(none)'}\n</upstream>\n\n"
               f"<templates>\n{templates(stage) or '(none)'}\n</templates>\n\n"
               f"<references>\n{refs_text(units)}\n</references>\n\n"
               f"Run stage {stage.name} now and write its outputs.")
    return system, content


def estimate(store, cfg, count) -> int:
    sets = reference_sets(store, cfg, count)
    i, o, _, _ = PRICES[MODEL]
    base = count(INSTRUCTIONS + layers())
    total, lines = 0.0, []
    for d, desc in domains().items():
        for n, st in enumerate(stage_dirs()):
            ctx = count((st / "CONTEXT.md").read_text(encoding="utf-8")) + count(templates(st)) + count(desc)
            up = sum(OUT_GUESS[p.name] for p in stage_dirs()[:n]
                     if p.name in (st / "CONTEXT.md").read_text(encoding="utf-8")) / TOKEN_RATIO
            arms = sets[qid(d, st)]
            seen, calls = [], []
            for a in ARMS:
                ids = [u["id"] for u in arms[a]]
                if ids not in seen:
                    seen.append(ids)
                    calls.append(a)
            for a in calls:
                inp = (base + ctx + up + sum(u["tokens"] for u in arms[a])) * TOKEN_RATIO
                answer = (inp * i + OUT_GUESS[st.name] * o) / 1e6
                g_in = (base + ctx + up + sum(u["tokens"] for u in arms["whole"])) * TOKEN_RATIO + OUT_GUESS[st.name]
                grade = (g_in * i + 1500 * o) / 1e6
                total += answer + grade
                lines.append(f"{d} {st.name} {a}: input ~{inp:,.0f}, refs {sum(u['tokens'] for u in arms[a]):,}, "
                             f"answer ${answer:.2f}, grade ${grade:.2f}")
    print("\n".join(lines) + f"\nestimated total ${total:.2f} (output guesses {OUT_GUESS})")
    return 0


def answers() -> list[dict]:
    f = out_dir() / "answers.jsonl"
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()] if f.exists() else []


def run(client, store, cfg, count, cap: float) -> int:
    sets = reference_sets(store, cfg, count)
    done = {(r["domain"], r["stage"], r["arm"]) for r in answers()}
    spent = sum(r["cost"] for r in answers())
    for d, desc in domains().items():
        for st in stage_dirs():
            arms = sets[qid(d, st)]
            for arm in ARMS:
                if (d, st.name, arm) in done:
                    continue
                ids = [u["id"] for u in arms[arm]]
                row = {"domain": d, "stage": st.name, "arm": arm, "refs": ids,
                       "ref_tokens": sum(u["tokens"] for u in arms[arm])}
                twin = next((a for a in ARMS[:ARMS.index(arm)] if [u["id"] for u in arms[a]] == ids), None)
                if twin:
                    row.update(same_as=twin, cost=0.0, ms=0.0, usage=None)
                else:
                    system, content = prompt(d, desc, st, arms[arm])
                    t0 = time.perf_counter()
                    with client.messages.stream(model=MODEL, max_tokens=MAX_TOKENS, output_config={"effort": "low"},
                                                system=system, messages=[{"role": "user", "content": content}]) as s:
                        resp = s.get_final_message()
                    if resp.stop_reason in ("max_tokens", "refusal"):
                        raise SystemExit(f"{d} {st.name} {arm}: stopped with {resp.stop_reason}")
                    text = "".join(b.text for b in resp.content if b.type == "text").strip()
                    if not FILE_BLOCK.search(text):
                        raise SystemExit(f"{d} {st.name} {arm}: no file blocks in the output")
                    run_path(d, st.name, arm).parent.mkdir(parents=True, exist_ok=True)
                    run_path(d, st.name, arm).write_text(text, encoding="utf-8", newline="\n")
                    u = usage(resp)
                    row.update(same_as=None, cost=cost(MODEL, u), ms=(time.perf_counter() - t0) * 1000, usage=u)
                spent += row["cost"]
                with open(out_dir() / "answers.jsonl", "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(row) + "\n")
                print(d, st.name, arm, row["same_as"] or f"{row['ms'] / 1000:.0f} s", f"total ${spent:.2f}", flush=True)
                if spent > cap:
                    raise SystemExit(f"Spend ${spent:.2f} passed the cap ${cap:.2f}; stopped")
    return 0


def code_checks(text: str) -> dict:
    """Mechanical checks on one output: dashes, line caps, placeholder format."""
    files = FILE_BLOCK.findall(text)
    over = [p for p, body in files if p.endswith("CONTEXT.md") and len(body.strip().splitlines()) > 80]
    over += [p for p, body in files if "references/" in p and p.endswith(".md") and len(body.strip().splitlines()) > 200]
    bad = sorted({m for _, body in files for m in PLACEHOLDER.findall(body) if not GOOD_PLACEHOLDER.match(m.strip())})
    return {"files": len(files), "dashes": sum(text.count(c) for c in DASHES), "over_cap": over, "bad_placeholders": bad}


def verdict_schema(n: int) -> dict:
    check = {"type": "object", "properties": {"name": {"type": "string"}, "pass": {"type": "boolean"},
                                              "note": {"type": "string"}},
             "required": ["name", "pass", "note"], "additionalProperties": False}
    return {"type": "object", "properties": {"checks": {"type": "array", "items": check}, "overall": {"type": "integer"},
                                             "reason": {"type": "string"}},
            "required": ["checks", "overall", "reason"], "additionalProperties": False}


def grade(client, count, cap: float) -> int:
    """cap covers the whole pilot: answering already spent plus grading."""
    rows = [r for r in answers() if r["same_as"] is None]
    out = out_dir() / "grades.jsonl"
    prior = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()] if out.exists() else []
    done = {r["uid"] for r in prior}
    spent = sum(r["cost"] for r in answers()) + sum(r["cost"] for r in prior)
    descs, stages = domains(), {s.name: s for s in stage_dirs()}
    random.Random(7).shuffle(rows)
    for r in rows:
        uid = f"{r['domain']}/{r['stage']}/{r['arm']}"
        if uid in done:
            continue
        st = stages[r["stage"]]
        checks = audit_checks(st)
        refs = "\n\n".join(f'<file path="{p.relative_to(S.root()).as_posix()}">\n{p.read_text(encoding="utf-8")}\n</file>'
                           for p, _ in G.reference_files(G.inputs_table(st / "CONTEXT.md"), st, S.root()))
        listed = "\n".join(f"{n + 1}. {c}: {cond}" for n, (c, cond) in enumerate(checks))
        text = (f"<stage-contract>\n{(st / 'CONTEXT.md').read_text(encoding='utf-8')}\n</stage-contract>\n\n"
                f"<user-workflow-description>\n{descs[r['domain']]}\n</user-workflow-description>\n\n"
                f"<upstream>\n{upstream(r['domain'], st) or '(none)'}\n</upstream>\n\n"
                f"<templates>\n{templates(st) or '(none)'}\n</templates>\n\n<reference-files>\n{refs}\n</reference-files>\n\n"
                f"<output-to-grade>\n{run_path(r['domain'], r['stage'], r['arm']).read_text(encoding='utf-8')}\n"
                f"</output-to-grade>\n\nChecks, in this order:\n{listed}")
        if uid in text or f'arm="{r["arm"]}"' in text:
            raise RuntimeError(f"{uid}: grader prompt carries the arm")
        resp = client.messages.create(model=MODEL, max_tokens=4000, system=GRADER,
                                      output_config={"effort": "low", "format": {"type": "json_schema",
                                                                                 "schema": verdict_schema(len(checks))}},
                                      messages=[{"role": "user", "content": text}])
        if resp.stop_reason != "end_turn":
            raise RuntimeError(f"{uid}: grader stopped with {resp.stop_reason}")
        v = json.loads(next(b.text for b in resp.content if b.type == "text"))
        if len(v["checks"]) != len(checks) or not 1 <= v["overall"] <= 5:
            raise RuntimeError(f"{uid}: grader returned {len(v['checks'])} checks (want {len(checks)}), overall {v['overall']}")
        c_ = cost(MODEL, usage(resp))
        spent += c_
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"uid": uid, **v, "check_names": [c for c, _ in checks], "cost": c_}) + "\n")
        print(uid, sum(c["pass"] for c in v["checks"]), "of", len(checks), "overall", v["overall"],
              f"pilot total ${spent:.2f}", flush=True)
        if spent > cap:
            raise SystemExit(f"Pilot spend ${spent:.2f} passed the cap ${cap:.2f}; stopped")
    return 0


def report() -> int:
    rows = {(r["domain"], r["stage"], r["arm"]): r for r in answers()}
    grades = {g["uid"]: g for g in map(json.loads, (out_dir() / "grades.jsonl").read_text(encoding="utf-8").splitlines())}

    def g_of(k):
        src = (k[0], k[1], rows[k]["same_as"]) if rows[k]["same_as"] else k
        return grades["/".join(src)], code_checks(run_path(*src).read_text(encoding="utf-8")), src

    missing = [k for k in rows if "/".join(k if not rows[k]["same_as"] else (k[0], k[1], rows[k]["same_as"])) not in grades]
    if missing:
        raise SystemExit(f"{len(missing)} outputs have no grade")
    lines = ["# Pilot: The Gate on Workspace-Builder", "",
             f"Opus 5.5 runs each workspace-builder stage for two made-up domains. Arms differ only in reference files. "
             f"Blind grading against each stage's audit plus a reference-rules check; the grader sees every reference "
             f"file in full.", "",
             "| Arm | Checks passed | Overall (mean of 5) | Median reference tokens | Median input tokens | Code-check fails "
             "| Dashes | Own calls | Cost |",
             "|-----|---------------|---------------------|-------------------------|---------------------|------------------"
             "|--------|-----------|------|"]
    for arm in ARMS:
        ks = [k for k in rows if k[2] == arm]
        gs = [g_of(k) for k in ks]
        passed = sum(sum(c["pass"] for c in g["checks"]) for g, _, _ in gs)
        total = sum(len(g["checks"]) for g, _, _ in gs)
        own = [rows[k] for k in ks if not rows[k]["same_as"]]
        inp = [sum(r["usage"][x] for x in ("input", "cache_write", "cache_read")) for r in own]
        fails = sum(bool(c["over_cap"] or c["bad_placeholders"]) for _, c, _ in gs)
        lines.append(f"| {arm} | {passed} of {total} | {statistics.mean(g['overall'] for g, _, _ in gs):.1f} | "
                     f"{statistics.median(rows[k]['ref_tokens'] for k in ks):,.0f} | "
                     f"{statistics.median(inp) if inp else 0:,.0f} | {fails} | {sum(c['dashes'] for _, c, _ in gs)} | "
                     f"{len(own)} of {len(ks)} | ${sum(r['cost'] for r in own):.2f} |")
    lines += ["", "## Per task", "", "| Domain | Stage | Arm | Reference tokens | Checks | Overall | Failed checks | Same as |",
              "|--------|-------|-----|------------------|--------|---------|---------------|---------|"]
    for k in sorted(rows, key=lambda k: (k[0], k[1], ARMS.index(k[2]))):
        g, _, _ = g_of(k)
        failed = ", ".join(n for n, c in zip(g["check_names"], g["checks"]) if not c["pass"]) or "none"
        lines.append(f"| {k[0]} | {k[1]} | {k[2]} | {rows[k]['ref_tokens']:,} | {sum(c['pass'] for c in g['checks'])} of "
                     f"{len(g['checks'])} | {g['overall']} | {failed} | {rows[k]['same_as'] or ''} |")
    lines += ["", f"Answering ${sum(r['cost'] for r in rows.values()):.2f}, grading ${sum(g['cost'] for g in grades.values()):.2f}."]
    (out_dir() / "pilot.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.pilot")
    mode = ap.add_mutually_exclusive_group(required=True)
    for m in ("judge", "estimate", "run", "grade", "report"):
        mode.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--cap", type=float, default=10.0)
    a = ap.parse_args(argv)
    if a.report:
        return report()
    if (a.judge or a.run or a.grade) and not a.yes:
        raise SystemExit("This spends credit; pass --yes")
    from hces.config import load
    from hces.passages import TokenCounter
    from hces.store import Store

    cfg, count = load(), TokenCounter()
    out_dir().mkdir(parents=True, exist_ok=True)
    store = Store(cfg.results_store)
    if a.judge:
        return judge_all(store, cfg, count)
    if a.estimate:
        return estimate(store, cfg, count)
    import anthropic

    client = anthropic.Anthropic()
    return run(client, store, cfg, count, a.cap) if a.run else grade(client, count, a.cap)


if __name__ == "__main__":
    raise SystemExit(main())
