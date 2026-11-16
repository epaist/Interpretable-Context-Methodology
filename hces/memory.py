"""Stage 06: self-learning memory over a dated stream. One store per workspace (Bee, 2026-11-02).

  python -m hces.memory --estimate --phase a
  python -m hces.memory --replay --phase a --yes --cap 3     replay records in date order, ask each question at its date
  python -m hces.memory --report --phase a                   scorecard against the ledger

Per record: Claude extracts the facts it states (subject, attribute, value, effective date, quote). Per new fact:
the nearest stored facts by embedding are judged by JEV, pair by pair: same attribute of the same thing, and
same value. Code links facts judged the same attribute into groups and decides what is current:

  - A group's current value at a date is the value of its latest fact dated on or before that date. A fact is
    dated by its stated effective date, or by its record's date when none is stated.
  - Reversion guard: a value that was already superseded in the group only becomes current again once two
    records after the supersession state it. One stale quote cannot roll a fact back.

Nothing is overwritten: facts and links are insert-only, so any answer can be traced to the records behind it.
Each question is asked when the replay reaches its date, so memory never sees a later record.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sqlite3
import time
from pathlib import Path

from hces import stream as T
from hces.endtoend import PRICES, cost, usage
from hces.rubric import Question, Rubric

MODEL = "claude-opus-5-5"
K = 20
SAME_AT = 0.5  # same_attribute probability that links two facts
REVERT_AFTER = 2
CONTEXT_GROUPS = 8  # 4 left the Q-Box fact out of a router question (phase A run 1)
NOT_KNOWN = "Not in memory."
GRADE_TAG = ""  # "-local" when a local model grades, so Claude grades are never overwritten

LINK_RUBRIC = Rubric(
    rubric_id="memory-link", version=1,
    task="Compare a new statement about Quillmere Broadband with a stored statement.",
    questions=(
        Question("related", "score", "How closely is the stored statement about the same thing as the new statement in the task?",
                 ["About something else.", "Same general topic, different attribute.", "The same attribute of the same thing."]),
        Question("same_attribute", "noul", "Do the stored statement and the new statement describe the same attribute of the "
                 "same plan, fee, rule, product or service (whatever its value)? Two different fees, two different plans, or a "
                 "fee and a time limit are not the same attribute.", critical=True),
        Question("same_value", "noul", "Do the two statements give the same value for that attribute (same amount, length, "
                 "version, name or rule), even if worded differently?"),
    ),
    answerability=Question("answerable", "noul", "Not used."),
)

EXTRACT_SCHEMA = {"type": "object", "properties": {"facts": {"type": "array", "items": {
    "type": "object", "properties": {k: {"type": "string"} for k in ("key", "subject", "attribute", "value", "effective_date", "quote")},
    "required": ["key", "subject", "attribute", "value", "effective_date", "quote"], "additionalProperties": False}}},
    "required": ["facts"], "additionalProperties": False}
EXTRACT = (
    "You read one dated Quillmere Broadband support record and list the company facts it states as true: prices, fees, "
    "limits, rules, policies, versions, contact details, coverage, products. Skip anything about the individual customer "
    "(their name, their bill, their problem) unless it states a company-wide fact. One fact per item: subject (the plan, "
    "fee, rule or product), attribute (what about it), value (as stated, short), effective_date (YYYY-MM-DD only if the "
    "record says when the value starts, else empty), quote (the exact sentence it comes from). Return an empty list if "
    "the record states no company fact. Skip ideas or proposals the record says were not decided. When the record says a "
    "value starts on a later date, give that date as effective_date."
)
KEYED = (
    " Offers, discounts and terms an agent gives a customer (a retention deal, a waived fee) are company facts too. "
    "Also give each fact a key: a short snake_case name for the attribute of the thing, the same whatever its value "
    "(spark_100_monthly_price, not spark_price_42). You get the keys memory already holds: reuse one when the fact is "
    "the same attribute of the same thing, even if the value changed; name a new key only for a new attribute. Two "
    "different fees, plans, limits or versions never share a key."
)
LOCAL_HINT = (  # a small local model returns [] for most records without this nudge (9B: 61 of 122 records empty)
    " Most records state one to four company facts: a price, fee, limit, policy, plan detail, version, phone number, "
    "hours or rule the agent tells the customer. Return an empty list only if there is truly none. Copy each value "
    "exactly as the record writes it (digits, symbols, product names); never spell numbers out. If the record is a "
    "numbered version of a document (an SOP or a policy), also list the version itself as a fact: subject the document "
    "code (for example SOP-02), attribute 'version in force', value the version (for example v6). In a numbered list "
    "of rules, every line is one fact: the label before the colon is the attribute, and the text after it is the value."
)
LOCAL_MISSED = (  # second pass for a local model: found 10 of 13 facts the first pass missed, vs 5 of 13 without it
    "Facts already listed from this record:\n{found}\n\nRead the record again and list only company facts it states "
    "that are not in that list (prices, fees, limits, time windows, contact details, payment methods, models, rules). "
    "Return an empty list if none are missing."
)
LOCAL_KEYING = (  # a local model lists half as many facts when the held keys are in the extraction prompt, so it keys after
    "You give each fact from a Quillmere Broadband record a key: a short snake_case name for the attribute of the thing, "
    "the same whatever its value (spark_100_monthly_price, not spark_price_42). Reuse a held key when the fact is the same "
    "attribute of the same thing, even if the value changed; name a new key only for a new attribute. Two different fees, "
    "plans, limits or versions never share a key, and two facts from one record never share a key. Return one key per "
    "fact, in the order given."
)
KEYING_SCHEMA = {"type": "object", "properties": {"keys": {"type": "array", "items": {"type": "string"}}},
                 "required": ["keys"], "additionalProperties": False}
ANSWER = (
    "You answer a question about Quillmere Broadband using only the memory notes given. Each note gives a fact's value as "
    f"of the question date and its history. Answer in one sentence with the value as of that date. If the notes do not "
    f"cover it, reply exactly: {NOT_KNOWN}"
)
GRADE_SCHEMA = {"type": "object", "properties": {"verdict": {"type": "string", "enum": ["correct", "stale", "wrong", "abstained"]},
                                                 "reason": {"type": "string"}},
                "required": ["verdict", "reason"], "additionalProperties": False}
GRADER = (
    "You grade one answer about a company fact as of a date. You get the question, the expected value, and other values "
    "the fact had at other times. Verdicts: correct (gives the expected value in substance), stale (gives one of the other "
    "values instead), wrong (gives some other value), abstained (says it does not know)."
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS facts (fact_id TEXT PRIMARY KEY, record_id TEXT NOT NULL, record_date TEXT NOT NULL,
  effective TEXT, dated TEXT NOT NULL, subject TEXT, attribute TEXT, value TEXT, quote TEXT, statement TEXT NOT NULL,
  vector TEXT NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS links (fact_id TEXT NOT NULL, other_id TEXT NOT NULL, related REAL, same_attribute REAL,
  same_value REAL, failed INTEGER NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS answers (question_id TEXT PRIMARY KEY, as_of TEXT NOT NULL, notes TEXT NOT NULL,
  answer TEXT NOT NULL, cost REAL NOT NULL, ms REAL NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS fact_keys (fact_id TEXT PRIMARY KEY, key TEXT NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS spend (what TEXT NOT NULL, record_id TEXT, cost REAL NOT NULL, created_at REAL NOT NULL);
"""


def guards() -> str:
    return "\n".join(f"CREATE TRIGGER IF NOT EXISTS {t}_no_{op.lower()} BEFORE {op} ON {t} BEGIN SELECT "
                     f"RAISE(ABORT, 'insert-only: {op} on {t}'); END;"
                     for t in ("facts", "links", "answers", "spend", "fact_keys") for op in ("UPDATE", "DELETE"))


class Memory:
    """One workspace's memory: facts, the JEV links between them, and the code that reads them as of a date."""

    def __init__(self, path: Path | str):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA + guards())

    def facts(self, upto: str | None = None) -> list[sqlite3.Row]:
        q = "SELECT * FROM facts" + (" WHERE record_date <= ?" if upto else "") + " ORDER BY rowid"
        return self.db.execute(q, (upto,) if upto else ()).fetchall()

    def add_fact(self, f: dict) -> None:
        with self.db:
            self.db.execute("INSERT INTO facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (f["fact_id"], f["record_id"], f["record_date"], f["effective"], f["dated"], f["subject"],
                             f["attribute"], f["value"], f["quote"], f["statement"], json.dumps(f["vector"]), time.time()))

    def add_links(self, rows: list[tuple]) -> None:
        with self.db:
            self.db.executemany("INSERT INTO links VALUES (?,?,?,?,?,?,?)", [(*r, time.time()) for r in rows])

    def add_key(self, fact_id: str, key: str) -> None:
        with self.db:
            self.db.execute("INSERT INTO fact_keys VALUES (?,?,?)", (fact_id, key, time.time()))

    def keys(self) -> dict[str, str]:
        return {r[0]: r[1] for r in self.db.execute("SELECT fact_id, key FROM fact_keys")}

    def spent(self) -> float:
        return self.db.execute("SELECT COALESCE(SUM(cost), 0) FROM spend").fetchone()[0]

    def add_spend(self, what: str, record_id: str | None, c: float) -> None:
        with self.db:
            self.db.execute("INSERT INTO spend VALUES (?,?,?,?)", (what, record_id, c, time.time()))

    def done_records(self) -> set[str]:
        return {r[0] for r in self.db.execute("SELECT DISTINCT record_id FROM spend WHERE what='extract'")}

    def best_links(self, upto: str | None, need_value: bool) -> tuple[list[str], list[tuple[str, str]]]:
        """Each fact joins only its single best earlier match (highest same_attribute, then related), never every
        link: joining every link chained different facts into one group (phase A run 1: 4 wrong merges)."""
        ids = [r["fact_id"] for r in self.facts(upto)]
        idset, best = set(ids), {}
        q = "SELECT * FROM links WHERE failed=0 AND same_attribute >= ?" + (" AND same_value >= ?" if need_value else "")
        for r in self.db.execute(q, (SAME_AT, SAME_AT) if need_value else (SAME_AT,)):
            if r["fact_id"] in idset and r["other_id"] in idset:
                k = (r["same_attribute"], r["related"] or 0.0)
                if r["fact_id"] not in best or k > best[r["fact_id"]][0]:
                    best[r["fact_id"]] = (k, r["other_id"])
        return ids, [(f, o) for f, (_, o) in best.items()]

    def groups(self, upto: str | None = None) -> dict[str, str]:
        """fact_id -> group id, over facts from records dated on or before upto. With canonical keys, a fact sits in
        its key's group unless JEV judged it against earlier facts of that key and found none the same attribute."""
        keys = self.keys()
        if not keys:
            return group_ids(*self.best_links(upto, need_value=False))
        judged, passed = set(), set()
        for r in self.db.execute("SELECT fact_id, same_attribute, failed FROM links"):
            judged.add(r[0])
            if not r[2] and r[1] >= SAME_AT:
                passed.add(r[0])
        return {r["fact_id"]: (f"k:{keys[r['fact_id']]}" if r["fact_id"] in keys and (r["fact_id"] not in judged or r["fact_id"] in passed)
                               else r["fact_id"]) for r in self.facts(upto)}

    def value_classes(self, upto: str | None = None) -> dict[str, str]:
        """fact_id -> value class: each fact joins its best match judged the same attribute and the same value."""
        return group_ids(*self.best_links(upto, need_value=True))


def group_ids(ids: list[str], pairs: list[tuple[str, str]]) -> dict[str, str]:
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    return {i: find(i) for i in ids}


def norm(v: str) -> str:
    return " ".join(v.lower().replace("$", "").replace(".00", "").split())


def vkey(f: dict) -> str:
    return f.get("vclass") or norm(f["value"])


def current(facts: list[dict], as_of: str) -> dict | None:
    """The group's value as of a date, with the reversion guard. facts: dicts with value, dated, record_date and
    optionally vclass (the JEV same-value class; without it, values compare as normalized text)."""
    known = [f for f in facts if f["record_date"] <= as_of]
    # phase C: a later record that gives the same value a different start date replaces the earlier start (a delay notice)
    moved = {id(f) for f in known for g in known if f.get("effective") and g.get("effective") and g["record_date"] > f["record_date"]
             and g["effective"] != f["effective"] and vkey(g) == vkey(f)}
    seen = sorted((f for f in known if f["dated"] <= as_of and id(f) not in moved), key=lambda f: (f["dated"], f["record_date"]))
    if not seen:
        return None
    top = max(rank(f) for f in seen)
    if top:  # source rank: an SOP or governance version in force outranks an announcement, which outranks a ticket
        return max((f for f in seen if rank(f) == top), key=lambda f: (f["dated"], f["record_date"]))
    cur, superseded, backers = seen[0], set(), {}
    for f in seen[1:]:
        v = vkey(f)
        if v == vkey(cur):
            continue
        if v in superseded:
            backers.setdefault(v, []).append(f)
            if len(backers[v]) < REVERT_AFTER:
                continue
        superseded.add(vkey(cur))
        backers.pop(v, None)
        cur = f
    return cur


def rank(f: dict) -> int:
    return 2 if f.get("official") else 1 if f.get("announced") else 0


def official_source(record_id: str) -> str | None:
    """'sop-02-v6' -> 'SOP-02 v6' for SOP and governance records; None for tickets and call logs."""
    if not record_id.startswith(("sop-", "gov-")):
        return None
    doc, v = record_id.rsplit("-v", 1)
    return f"{doc.upper()} v{v}"


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1.0)


def statement(f: dict) -> str:
    return f"{f['subject']}, {f['attribute']}: {f['value']}"


def extract(client, rec: dict, keys: list[str] | None = None) -> tuple[list[dict], float]:
    """keys None: run a/a2/a3 extraction (key returned but unused). keys list: canonical-key extraction.
    A local model gets LOCAL_HINT and a second pass that asks for the facts the first pass left out."""
    local = getattr(client, "local", False)
    held, keys = keys, ([] if local and keys is not None else keys)
    head = "" if keys is None else "Keys memory already holds: " + (", ".join(sorted(keys)) or "none yet") + "\n\n"
    system = EXTRACT + ("" if keys is None else KEYED) + (LOCAL_HINT if local else "")
    user = f"{head}Record {rec['id']}, dated {rec['date']}, {rec['kind']}:\n\n{rec['text']}"
    facts, spent = [], 0.0
    for prompt in ([user, None] if local else [user]):
        if prompt is None:
            found = "\n".join(f"- {f['subject']} {f['attribute']}: {f['value']}" for f in facts) or "- none"
            prompt = user + "\n\n" + LOCAL_MISSED.format(found=found)
        resp = client.messages.create(model=MODEL, max_tokens=3000, system=system,
                                      output_config={"effort": "low", "format": {"type": "json_schema", "schema": EXTRACT_SCHEMA}},
                                      messages=[{"role": "user", "content": prompt}])
        if resp.stop_reason != "end_turn":
            raise RuntimeError(f"{rec['id']}: extraction stopped with {resp.stop_reason}")
        facts += json.loads(next(b.text for b in resp.content if b.type == "text"))["facts"]
        spent += cost(MODEL, usage(resp))
    if local and held and facts:
        named = local_keys(client, facts, held)
        if len(named) != len(facts):  # the list came back short or long: key each fact on its own
            named = [k for f in facts for k in local_keys(client, [f], held)[:1]]
        if len(named) != len(facts):
            raise RuntimeError(f"{rec['id']}: keying returned {len(named)} keys for {len(facts)} facts")
        for i in range(len(named)):  # two facts of one record never share a key: re-key the later one without it
            taken = set(named[:i])
            if named[i] in taken and norm(facts[i]["value"]) not in {norm(f["value"]) for f, k in zip(facts[:i], named) if k == named[i]}:
                again = local_keys(client, [facts[i]], [k for k in held if k not in taken])[:1]
                named[i] = again[0] if again and again[0] not in taken else f"{named[i]}_{i + 1}"
        facts = [{**f, "key": k} for f, k in zip(facts, named)]
    return facts, spent


def local_keys(client, facts: list[dict], held: list[str]) -> list[str]:
    # the quote carries the record's own label ("Fix for a Q-Box red light: ..."), which the attribute often loses
    listed = "\n".join(f"{i + 1}. {f['subject']} {f['attribute']}: {f['value']} (from: \"{f['quote']}\")" for i, f in enumerate(facts))
    resp = client.messages.create(model=MODEL, max_tokens=1500, system=LOCAL_KEYING,
                                  output_config={"format": {"type": "json_schema", "schema": KEYING_SCHEMA}},
                                  messages=[{"role": "user", "content": f"Held keys: {', '.join(sorted(held))}\n\nFacts:\n{listed}"}])
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"keying stopped with {resp.stop_reason}")
    return json.loads(next(b.text for b in resp.content if b.type == "text"))["keys"]


def link_key(mem: Memory, judge, new: dict, key: str, cfg) -> float:
    """JEV checks the extractor's key: the new fact against the latest earlier facts holding that key (at most K)."""
    from hces.judge_all import billed_tokens
    from hces.units import Unit

    keys = mem.keys()
    near = [r for r in mem.facts() if r["fact_id"] != new["fact_id"] and keys.get(r["fact_id"]) == key][-K:]
    if not near:
        return 0.0
    return store_links(mem, judge, new, near, cfg, billed_tokens, Unit)


def store_links(mem: Memory, judge, new: dict, near: list, cfg, billed_tokens, Unit) -> float:
    task = f"New statement, dated {new['dated']}: {new['statement']}"
    js = judge.judge(task, LINK_RUBRIC, [Unit(r["fact_id"], f"Stored statement, dated {r['dated']}: {r['statement']}") for r in near])
    by: dict[str, dict] = {}
    for j in js:
        by.setdefault(j.unit_id, {})[j.question_key] = j
    rows = []
    for r in near:
        a = by.get(r["fact_id"], {})
        failed = any(a.get(k) is None or a[k].failed for k in ("related", "same_attribute", "same_value"))
        val = lambda k: None if failed else a[k].value  # noqa: E731
        rows.append((new["fact_id"], r["fact_id"], val("related"), val("same_attribute"), val("same_value"), int(failed)))
    mem.add_links(rows)
    if sum(r[5] for r in rows) > len(rows) // 10:
        raise RuntimeError(f"{new['fact_id']}: {sum(r[5] for r in rows)} of {len(rows)} JEV requests failed")
    return billed_tokens(js) * cfg.price_per_million / 1e6


def link(mem: Memory, judge, new: dict, embedder_vec: list[float], cfg) -> float:
    """JEV judges the new fact against its K nearest stored facts. Returns JEV cost."""
    from hces.judge_all import billed_tokens
    from hces.units import Unit

    old = [r for r in mem.facts() if r["fact_id"] != new["fact_id"]]
    near = sorted(old, key=lambda r: -cosine(embedder_vec, json.loads(r["vector"])))[:K]
    if not near:
        return 0.0
    return store_links(mem, judge, new, near, cfg, billed_tokens, Unit)


def notes(mem: Memory, question: str, as_of: str, embedder) -> str:
    """Current value and history for the groups nearest the question, as of its date."""
    rows = [dict(r) for r in mem.facts(as_of)]
    if not rows:
        return ""
    groups, classes = mem.groups(as_of), mem.value_classes(as_of)
    for r in rows:
        r["vclass"] = classes[r["fact_id"]]
        r["official"] = official_source(r["record_id"])
        r["announced"] = r["record_id"].startswith("ann-")
    qv = embedder.embed([question])[0]
    ranked = sorted(rows, key=lambda r: -cosine(qv, json.loads(r["vector"])))
    picked = []
    for r in ranked:
        if groups[r["fact_id"]] not in picked:
            picked.append(groups[r["fact_id"]])
        if len(picked) == CONTEXT_GROUPS:
            break
    out = []
    for g in picked:
        members = [r for r in rows if groups[r["fact_id"]] == g]
        cur = current(members, as_of)
        if cur is None:
            continue
        hist = sorted({(m["dated"], m["value"]) for m in members if vkey(m) != vkey(cur)})
        src = f"; per {cur['official']}" if cur.get("official") else "; per a staff announcement" if cur.get("announced") else ""
        out.append(f"- {statement(cur)} (as of {as_of}; stated from {cur['dated']}{src}, {len(members)} records)"
                   + (f"; earlier or disputed values: {'; '.join(f'{v} ({d})' for d, v in hist[-3:])}" if hist else ""))
    return "\n".join(out)


def ask(client, mem: Memory, q: dict, embedder) -> float:
    t0 = time.perf_counter()
    n = notes(mem, q["question"], q["as_of"], embedder)
    if not n:
        answer, c = NOT_KNOWN, 0.0
    else:
        resp = client.messages.create(model=MODEL, max_tokens=300, system=ANSWER, output_config={"effort": "low"},
                                      messages=[{"role": "user", "content": f"Question date: {q['as_of']}\n\nMemory notes:\n{n}\n\nQuestion: {q['question']}"}])
        answer, c = "".join(b.text for b in resp.content if b.type == "text").strip(), cost(MODEL, usage(resp))
    with mem.db:
        mem.db.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?)",
                       (q["id"], q["as_of"], n, answer, c, (time.perf_counter() - t0) * 1000, time.time()))
    mem.add_spend("answer", None, c)
    return c


def mem_path(run: str) -> Path:
    return T.out_dir() / f"memory-{run}.sqlite"


def fork(src: str, run: str) -> int:
    """New store for a rerun: copies the facts, the JEV links and their spend, so only answering and grading are new."""
    if mem_path(run).exists():
        raise SystemExit(f"{mem_path(run)} already exists")
    mem = Memory(mem_path(run))
    with mem.db:
        mem.db.execute("ATTACH DATABASE ? AS src", (str(mem_path(src)),))
        for t, where in (("facts", ""), ("links", ""), ("fact_keys", ""), ("spend", " WHERE what IN ('extract', 'jev')")):
            mem.db.execute(f"INSERT INTO {t} SELECT * FROM src.{t}{where}")
    mem.db.execute("DETACH DATABASE src")
    print(f"{run}: {len(mem.facts())} facts, {len(mem.done_records())} records, carried spend ${mem.spent():.2f}")
    return 0


def records(phase: str) -> list[dict]:
    """Later phases replay earlier phases' records too, so each record sees only what memory held at its date."""
    return [json.loads(l) for ph in ("a", "b", "c")[: "abc".index(phase) + 1]
            for l in (T.kb_dir(ph) / "records.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def load(phase: str) -> tuple[list[dict], list[dict]]:
    recs = records(phase)
    qs = [json.loads(l) for l in (T.out_dir() / "quillmere-questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return sorted(recs, key=lambda r: (r["date"], r["id"])), [q for q in qs if q["phase"] == phase]


def ingest(client, mem: Memory, rec: dict, embedder, judge, cfg, keyed: bool = True) -> list[dict]:
    """One record into memory: extract its facts, store each with its vector, link it (by key or by nearest facts)
    and record the spend. rec: id, date (YYYY-MM-DD), kind, text. Returns the extracted facts."""
    facts, c = extract(client, rec, sorted(set(mem.keys().values())) if keyed else None)
    jev = 0.0
    for n, f in enumerate(facts, start=1):
        row = {"fact_id": f"{rec['id']}#f{n}", "record_id": rec["id"], "record_date": rec["date"],
               "effective": f["effective_date"] or None, "dated": f["effective_date"] or rec["date"],
               "subject": f["subject"], "attribute": f["attribute"], "value": f["value"], "quote": f["quote"]}
        row["statement"] = statement(row)
        row["vector"] = embedder.embed([row["statement"]])[0]
        mem.add_fact(row)
        if keyed:
            mem.add_key(row["fact_id"], f["key"])
            jev += link_key(mem, judge, row, f["key"], cfg)
        else:
            jev += link(mem, judge, row, row["vector"], cfg)
    mem.add_spend("extract", rec["id"], c)
    mem.add_spend("jev", rec["id"], jev)
    return facts


def replay(client, phase: str, cap: float, run: str, keyed: bool = False) -> int:
    from hces.config import load as load_cfg
    from hces.embed import FastEmbedder
    from hces.judge import JevJudge

    cfg = load_cfg()
    embedder = FastEmbedder(cfg.embedder)
    judge = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    mem = Memory(mem_path(run))
    recs, qs = load(phase)
    done = mem.done_records()
    asked = {r[0] for r in mem.db.execute("SELECT question_id FROM answers")}
    pending = sorted((q for q in qs if q["id"] not in asked), key=lambda q: q["as_of"])
    for rec in recs:
        while pending and pending[0]["as_of"] < rec["date"]:  # ask before any record dated after the question
            ask(client, mem, pending.pop(0), embedder)
        if rec["id"] in done:
            continue
        t0 = time.perf_counter()
        facts = ingest(client, mem, rec, embedder, judge, cfg, keyed)
        print(rec["id"], rec["date"], len(facts), "facts", f"{(time.perf_counter() - t0):.1f} s", f"total ${mem.spent():.2f}", flush=True)
        if mem.spent() > cap:
            raise SystemExit(f"Spend ${mem.spent():.2f} passed the cap ${cap:.2f}; stopped")
    for q in pending:
        ask(client, mem, q, embedder)
    return 0


def grade(client, phase: str, run: str) -> int:
    mem = Memory(mem_path(run))
    _, qs = load(phase)
    answers = {r["question_id"]: dict(r) for r in mem.db.execute("SELECT * FROM answers")}
    out = T.out_dir() / f"quillmere-{run}-grades{GRADE_TAG}.jsonl"
    done = {json.loads(l)["id"] for l in out.read_text(encoding="utf-8").splitlines()} if out.exists() else set()
    random.Random(7).shuffle(qs)
    for q in qs:
        if q["id"] in done:
            continue
        a = answers[q["id"]]
        resp = client.messages.create(model=MODEL, max_tokens=500, system=GRADER,
                                      output_config={"effort": "low", "format": {"type": "json_schema", "schema": GRADE_SCHEMA}},
                                      messages=[{"role": "user", "content": f"Question (as of {q['as_of']}): {q['question']}\n\n"
                                                 f"Expected: {q['expected']}\nOther values at other times: {', '.join(q['other_values']) or 'none'}"
                                                 f"\n\nAnswer: {a['answer']}"}])
        v = json.loads(next(b.text for b in resp.content if b.type == "text"))
        c = cost(MODEL, usage(resp))
        mem.add_spend("grade", None, c)
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"id": q["id"], **v, "cost": c}) + "\n")
        print(q["id"], v["verdict"], flush=True)
    return 0


def merges(mem: Memory, phase: str) -> list[tuple[str, list[str]]]:
    """Groups holding facts from records planned for different keys: wrong merges. A fact is mapped to its record's
    key only when its quote is the record's planned quote (or contains it), so side facts are not counted."""
    recs = {r["id"]: r for r in records(phase)}
    key_of = {}
    for f in mem.facts():
        r = recs.get(f["record_id"])
        if r and r.get("style") == "noise":  # chatter states no fact: any of its facts merged into a real key is wrong
            key_of[f["fact_id"]] = "noise"
            continue
        if r and r.get("cites") and re.match(r"^((sop|gov)-\d+\s+)?(v|version)\s*\w+$", f["value"].strip(), re.I):
            # a ticket that cites "SOP-04 v8" states that version too: it belongs with the document's version facts
            key_of[f["fact_id"]] = r["cites"].split()[0].lower().replace("-", "_") + "_version"
            continue
        for key, quote in (r.get("quotes") or {r["key"]: r["quote"]}).items() if r else ():
            if norm(quote) in norm(f["quote"]) or norm(f["quote"]) in norm(quote):
                key_of[f["fact_id"]] = key
                break
    groups: dict[str, set] = {}
    for fid, g in mem.groups().items():
        if fid in key_of:
            groups.setdefault(g, set()).add(key_of[fid])
    return [(g, sorted(ks)) for g, ks in groups.items() if len(ks) > 1]


def report(phase: str, run: str) -> int:
    mem = Memory(mem_path(run))
    _, qs = load(phase)
    grades = {g["id"]: g for g in map(json.loads, (T.out_dir() / f"quillmere-{run}-grades{GRADE_TAG}.jsonl").read_text(encoding="utf-8").splitlines())}
    if set(q["id"] for q in qs) - set(grades):
        raise SystemExit("Some questions have no grade")
    bad = merges(mem, phase)
    c = lambda v, xs: sum(grades[q["id"]]["verdict"] == v for q in xs)  # noqa: E731
    ms = sorted(r["ms"] for r in mem.db.execute("SELECT ms FROM answers"))
    spend = {r[0]: r[1] for r in mem.db.execute("SELECT what, SUM(cost) FROM spend GROUP BY what")}
    lines = [f"# Quillmere Phase {phase.upper()} Scorecard" + ("" if run == phase else f" (run {run})"), "",
             f"{len(qs)} dated questions, each asked when the replay reached its date. {mem.db.execute('SELECT COUNT(*) FROM facts').fetchone()[0]} "
             f"facts from {len(mem.done_records())} records; {len(set(mem.groups().values()))} fact groups.", "",
             "| Bar | Result | Pass |", "|-----|--------|------|",
             f"| Current fact correct, at least 95% | {c('correct', qs)} of {len(qs)} ({100 * c('correct', qs) / len(qs):.0f}%) | "
             f"{'PASS' if c('correct', qs) >= 0.95 * len(qs) else 'FAIL'} |",
             f"| Superseded fact returned as current: never | {c('stale', qs)} | {'PASS' if c('stale', qs) == 0 else 'FAIL'} |",
             f"| Wrongly merged facts: none | {len(bad)} groups | {'PASS' if not bad else 'FAIL'} |", "",
             "| Question kind | Correct | Stale | Wrong | Abstained |", "|---|---|---|---|---|"]
    for kind in sorted({q["kind"] for q in qs}):
        xs = [q for q in qs if q["kind"] == kind]
        lines.append(f"| {kind} | {c('correct', xs)} of {len(xs)} | {c('stale', xs)} | {c('wrong', xs)} | {c('abstained', xs)} |")
    lines += ["", "## Misses", "", "| Question | As of | Expected | Verdict | Reason |", "|---|---|---|---|---|"]
    for q in sorted(qs, key=lambda q: q["id"]):
        g = grades[q["id"]]
        if g["verdict"] != "correct":
            lines.append(f"| {q['id']} {q['key']} | {q['as_of']} | {q['expected']} | {g['verdict']} | {' '.join(g['reason'].split())[:160]} |")
    lines += ["", f"Wrong merges: {', '.join('+'.join(k) for _, k in bad) or 'none'}.", "",
              f"Answer time median {ms[len(ms) // 2]:.0f} ms. Spend: " + ", ".join(f"{k} ${v:.2f}" for k, v in sorted(spend.items())) + "."]
    (T.out_dir() / f"quillmere-{run}-scorecard{GRADE_TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def estimate(phase: str) -> int:
    recs = [json.loads(l) for l in (T.out_dir() / f"quillmere-plan-{phase}.jsonl").read_text(encoding="utf-8").splitlines()]
    qs = [q for q in map(json.loads, (T.out_dir() / "quillmere-questions.jsonl").read_text(encoding="utf-8").splitlines()) if q["phase"] == phase]
    i, o, _, _ = PRICES[MODEL]
    per_rec_in, per_rec_out = 600 + sum(T.WORDS) / 2 * 1.35, 250
    extract_c = len(recs) * (per_rec_in * i + per_rec_out * o) / 1e6
    answer_c = len(qs) * (500 * i + 60 * o) / 1e6
    grade_c = len(qs) * (350 * i + 120 * o) / 1e6
    facts = len(recs) * 1.5
    jev = facts * K * 700 * 0.042 / 1e6
    print(json.dumps({"records": len(recs), "questions": len(qs), "extract": round(extract_c, 2), "answer": round(answer_c, 2),
                      "grade": round(grade_c, 2), "jev_requests": round(facts * K), "jev": round(jev, 2)}))
    return 0


def main(argv=None) -> int:
    global SAME_AT, GRADE_TAG
    ap = argparse.ArgumentParser(prog="python -m hces.memory")
    mode = ap.add_mutually_exclusive_group(required=True)
    for m in ("estimate", "fork", "replay", "grade", "report"):
        mode.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--phase", default="a")
    ap.add_argument("--run", help="store and output name; defaults to the phase")
    ap.add_argument("--local", metavar="MODEL", help="use this local model (llama-server) instead of Claude (costs nothing)")
    ap.add_argument("--keys", action="store_true", help="--replay: canonical keys at extraction, JEV checks them")
    ap.add_argument("--src", help="--fork: the run to copy facts and links from")
    ap.add_argument("--same-at", type=float, default=SAME_AT, help="same_attribute probability that links facts")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--cap", type=float, default=3.0)
    a = ap.parse_args(argv)
    run = a.run or a.phase
    SAME_AT = a.same_at
    GRADE_TAG = "-local" if a.local and (a.grade or a.report) else GRADE_TAG
    if a.estimate:
        return estimate(a.phase)
    if a.report:
        return report(a.phase, run)
    if a.fork:
        return fork(a.src or a.phase, run)
    if not a.yes:
        raise SystemExit("This spends credit; pass --yes")
    if a.local:
        from hces.local_llm import LocalClient

        client = LocalClient(a.local)
    else:
        import anthropic

        client = anthropic.Anthropic()
    return replay(client, a.phase, a.cap, run, a.keys) if a.replay else grade(client, a.phase, run)


if __name__ == "__main__":
    raise SystemExit(main())
