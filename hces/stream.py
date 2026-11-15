"""Stage 06: the Quillmere memory stream. Code plans every record and owns the truth; Claude only writes text.

  python -m hces.stream --ledger                 ledger + phase A record plan + questions from the company sheet
  python -m hces.stream --estimate --phase a     token and cost estimate for writing the records
  python -m hces.stream --write --phase a --yes --cap 3    Opus writes the planned records
  python -m hces.stream --ledger --phase b       phase B plan (SOP and governance versions, tickets citing them) + questions
  python -m hces.stream --write --phase b --local qwen9b --yes    code writes the SOP versions, the local model the tickets
  python -m hces.stream --ledger --phase c       phase C plan (announcements, meeting notes, newsletters, chatter) + questions

The ledger comes from the company sheet's tables by code, so expected answers never depend on a model.
Each planned record conveys one fact value in a set style; Claude returns the text plus the exact sentence
that conveys it, and code checks that sentence is in the text.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from datetime import date, timedelta
from pathlib import Path

from hces.endtoend import PRICES, cost, usage

MODEL = "claude-opus-5-5"
YEAR = 2026
START, END = date(YEAR, 1, 5), date(YEAR, 12, 18)
SEED = 6
HOT = ("refund_window", "spark_price", "support_phone", "outage_credit", "redlight_fix", "agent_refund_limit")
COLD = ("paperless_credit", "senior_discount", "recording_consent", "mesh_max", "reconnect_fee")
WORDS = (150, 260)
CELL = re.compile(r"^(.*?)\s*\((\d\d)-(\d\d)\)$")

# How a question names each fact. Written by hand once; the values come from the sheet.
ASK = {
    "hq": "Where is Quillmere's head office?", "founded": "What year was Quillmere founded?",
    "glide_cap": "Does the Glide 500 plan have a data cap?", "torrent_download": "What download speed does Torrent 1G give?",
    "router_brand": "What router do Quillmere customers get?", "billing_day": "On what day of the month do bills issue?",
    "email_support": "What is Quillmere's support email address?", "contract_none": "Is month-to-month service available?",
    "spark_price": "What is the monthly price of the Spark 100 plan?", "glide_price": "What is the monthly price of Glide 500?",
    "torrent_price": "What is the monthly price of Torrent 1G?", "torrent_upload": "What upload speed does Torrent 1G give?",
    "spark_cap": "What is the data cap on Spark 100?", "lite_plan": "Can customers sign up for the Lite 25 plan?",
    "overage_fee": "What is the data overage fee?", "modem_fee": "What is the monthly modem rental fee?",
    "install_fee": "What is the installation fee?", "etf": "What is the early termination fee?",
    "senior_discount": "How much is the senior discount?", "paperless_credit": "Is there a paperless billing credit, and how much?",
    "refund_window": "How long is the refund window?", "outage_credit": "How are outage credits calculated?",
    "late_fee": "What is the late payment fee?", "grace_period": "How long is the grace period before suspension?",
    "reconnect_fee": "What is the reconnection fee?", "price_lock": "How long is the price lock for new signups?",
    "support_hours": "What are phone support hours?", "support_phone": "What is the support phone number?",
    "tier2_sla": "How fast does tier 2 call back?", "tech_visit_fee": "What does a technician visit cost when the fault is the customer's?",
    "move_fee": "What does it cost to move service to a new address?", "payment_methods": "Which payment methods are accepted?",
    "autopay_discount": "How much is the autopay discount?", "redlight_fix": "What is the fix for a Q-Box showing a red light?",
    "firmware": "What is the current Q-Box firmware version?", "status_page": "Where is the outage status page?",
    "fiber_towns": "Which towns have fiber?", "maintenance_window": "When is the planned maintenance window?",
    "extender_model": "Which Wi-Fi extender model is offered?", "mesh_max": "How many extenders can a mesh have?",
    "agent_refund_limit": "Up to what amount can an agent refund without approval?", "retention_offer": "What is the retention offer?",
    "recording_consent": "Which call recording consent script is in use?", "recording_retention": "How long are call recordings kept?",
    "id_check": "How do agents verify a customer's identity?", "missed_appt_credit": "What credit is given for a missed technician appointment?",
    "big_credit_approver": "Who approves outage credits over $100?", "contract_terms": "Which contract terms are offered?",
}

# Phase A contradictions from the sheet (tickets and call logs only): key, date, style, value index.
# style stale = a record after a change states the old value; early = states the next value before it starts.
CONTRADICTIONS_A = [
    ("refund_window", "04-08", "stale", 0), ("refund_window", "04-25", "stale", 0),
    ("outage_credit", "06-20", "stale", 0), ("outage_credit", "06-20", "normal", 1),
    ("payment_methods", "05-12", "early", 1), ("tech_visit_fee", "04-15", "normal", 1),
    ("firmware", "08-10", "early", 2), ("support_phone", "04-22", "stale", 0), ("support_phone", "04-22", "normal", 1),
]

# Phase B: the line each SOP or governance version gives a fact it owns. Written by hand once; values come from the sheet.
LABEL = {
    "spark_price": "Spark 100 monthly price", "torrent_price": "Torrent 1G monthly price", "overage_fee": "Data overage fee",
    "modem_fee": "Modem rental fee", "late_fee": "Late payment fee", "grace_period": "Grace period before suspension",
    "autopay_discount": "Autopay discount", "refund_window": "Refund window", "outage_credit": "Outage credit calculation",
    "agent_refund_limit": "Agent refund limit without approval", "missed_appt_credit": "Credit for a missed technician appointment",
    "big_credit_approver": "Approval of outage credits over $100", "redlight_fix": "Fix for a Q-Box red light",
    "firmware": "Current Q-Box firmware version", "status_page": "Outage status page", "maintenance_window": "Planned maintenance window",
    "glide_price": "Glide 500 monthly price", "spark_cap": "Spark 100 data cap", "lite_plan": "Lite 25 plan",
    "install_fee": "Installation fee", "etf": "Early termination fee", "price_lock": "Price lock for new signups",
    "contract_terms": "Contract terms offered", "id_check": "Customer identity check", "recording_consent": "Call recording consent script",
    "recording_retention": "Call recording retention", "retention_offer": "Retention offer",
}
# Phase B stale citations: a ticket on this date quotes the fact from the latest earlier version of its SOP that gave a
# different value (contradiction c is the first). Nobody corrects it.
STALE_CITES_B = [("refund_window", "10-20"), ("firmware", "09-10"), ("late_fee", "03-20"), ("spark_price", "09-15"),
                 ("install_fee", "08-15")]
# Phase C contradiction (e): an announcement on 03-02 says Calder fiber starts 03-15; a notice on 03-12 moves it to the
# real start, 04-01. Contradiction (i): meeting notes on 10-08 float a $46 Spark price from 11-01 that never ships.
EARLY_ANNOUNCE_C = ("fiber_towns", "03-02", "03-15", "03-12")
FLOATED_C = ("spark_price", "10-08", "$46", "11-01")
STATES = ("normal", "rephrase", "cite", "announce", "plan", "delay")  # styles that state a value as true from its start
KIND_TEXT = {"announcement": "an internal announcement from Quillmere management to all support staff",
             "meeting notes": "notes from an internal Quillmere team meeting, with attendees, agenda items and action items",
             "newsletter": "a Quillmere customer newsletter with community news and home Wi-Fi tips",
             "chatter": "an off-topic message thread from a Quillmere staff chat channel"}


def home() -> Path:
    from hces.sections import root

    return root() / "workspaces" / "hces-lab" / "stages" / "06-memory-stream"


def out_dir() -> Path:
    return home() / "output"


def kb_dir(phase: str) -> Path:
    from hces.sections import root

    return root() / "workspaces" / "hces-lab" / "kb" / "streams" / "quillmere" / phase


def table(text: str, heading: str) -> list[list[str]]:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise ValueError(f"Company sheet has no '## {heading}' section")
    rows = []
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else None
        if cells and not set(cells[0]) <= set("-: ") and cells[0] not in ("Key", "#"):
            rows.append(cells)
    return rows


def ledger(sheet: str) -> list[dict]:
    """One row per fact value: key, value, valid_from, valid_to (exclusive, None = still current), kind."""
    rows = []
    for key, value in table(sheet, "Stable Facts (never change: control set)"):
        rows.append({"key": key, "value": value, "valid_from": f"{YEAR}-01-01", "valid_to": None, "kind": "stable"})
    for cells in table(sheet, "Changing Facts (40 planted changes)"):
        _, key, old, *later = cells
        values = [(old, f"{YEAR}-01-01")]
        for c in later:
            if not c:
                continue
            m = CELL.match(c)
            if not m:
                raise ValueError(f"{key}: cannot read a dated value from {c!r}")
            values.append((m.group(1), f"{YEAR}-{m.group(2)}-{m.group(3)}"))
        for i, (v, start) in enumerate(values):
            end = values[i + 1][1] if i + 1 < len(values) else None
            rows.append({"key": key, "value": v, "valid_from": start, "valid_to": end, "kind": "changing"})
    keys = {r["key"] for r in rows}
    if keys != set(ASK):
        raise ValueError(f"Sheet keys and question phrases differ: {sorted(keys ^ set(ASK))}")
    return rows


def value_at(led: list[dict], key: str, day: str) -> dict:
    hits = [r for r in led if r["key"] == key and r["valid_from"] <= day and (r["valid_to"] is None or day < r["valid_to"])]
    if len(hits) != 1:
        raise ValueError(f"{key} at {day}: {len(hits)} ledger rows")
    return hits[0]


def rand_day(rng: random.Random, lo: str, hi: str | None) -> str:
    a = max(date.fromisoformat(lo), START)
    b = min(date.fromisoformat(hi) - timedelta(days=1), END) if hi else END
    if b < a:
        raise ValueError(f"Empty interval {lo} to {hi}")
    return (a + timedelta(days=rng.randrange((b - a).days + 1))).isoformat()


def plan_a(led: list[dict]) -> list[dict]:
    """Phase A record plan: tickets and call logs, each conveying one fact value in a set style."""
    rng = random.Random(SEED)
    plan = []
    for r in led:
        n = 2 if r["key"] in HOT else 1  # hot facts get a rephrased duplicate in every interval
        for _ in range(n):
            plan.append({"date": rand_day(rng, r["valid_from"], r["valid_to"]), "key": r["key"], "value": r["value"],
                         "style": "normal" if not plan or rng.random() < 0.6 else "rephrase"})
    for key, md, style, idx in CONTRADICTIONS_A:
        vals = [r for r in led if r["key"] == key]
        plan.append({"date": f"{YEAR}-{md}", "key": key, "value": vals[idx]["value"], "style": style})
    plan.sort(key=lambda p: (p["date"], p["key"]))
    for i, p in enumerate(plan, start=1):
        p["id"] = f"qa-{i:03d}"
        p["kind"] = rng.choice(("ticket", "call log"))
        p["phase"] = "a"
    return plan


def docs(sheet: str) -> list[dict]:
    """SOP and governance documents: code, title, owned keys, versions as (number, effective date)."""
    num = {cells[0]: cells[1] for cells in table(sheet, "Changing Facts (40 planted changes)")}
    out = []
    for name, versions, owned in table(sheet, "SOPs and Governance (phase B)"):
        if name == "Doc":
            continue
        code, title = name.split(" ", 1)
        vs = [(int(v), f"{YEAR}-{m}-{d}") for v, m, d in re.findall(r"v(\d+) \((\d\d)-(\d\d)\)", versions)]
        if [v for v, _ in vs] != list(range(1, len(vs) + 1)):
            raise ValueError(f"{code}: versions are not 1..n: {versions!r}")
        out.append({"doc": code, "title": title, "keys": [num[n.strip()] for n in owned.split(",")], "versions": vs})
    return out


def version_key(d: dict) -> str:
    return d["doc"].lower().replace("-", "_") + "_version"


def doc_ledger(dl: list[dict]) -> list[dict]:
    """One ledger row per document version, so 'which version is in force' has a code-owned answer."""
    rows = []
    for d in dl:
        for i, (v, start) in enumerate(d["versions"]):
            end = d["versions"][i + 1][1] if i + 1 < len(d["versions"]) else None
            rows.append({"key": version_key(d), "value": f"v{v}", "valid_from": start, "valid_to": end, "kind": "doc"})
    return rows


def version_at(d: dict, day: str) -> int:
    return max(v for v, start in d["versions"] if start <= day)


def plan_b(led: list[dict], dl: list[dict]) -> list[dict]:
    """Phase B record plan: every SOP and governance version (text by code), one ticket per value of each owned
    fact that cites the version in force, and the stale citations."""
    rng = random.Random(SEED + 2)
    owner = {k: d for d in dl for k in d["keys"]}
    for d in dl:
        for v, start in d["versions"][1:]:
            if all(value_at(led, k, start)["valid_from"] != start for k in d["keys"]):
                raise ValueError(f"{d['doc']} v{v} ({start}) changes none of its facts")
    plan = []
    for d in dl:
        for v, start in d["versions"]:
            facts = {k: value_at(led, k, start)["value"] for k in d["keys"]}
            plan.append({"id": f"{d['doc'].lower()}-v{v}", "date": start, "kind": "sop" if d["doc"].startswith("SOP") else "governance",
                         "doc": d["doc"], "title": d["title"], "version": v, "facts": {**facts, version_key(d): f"v{v}"},
                         "style": "official", "key": None, "value": None})
    tickets = []
    for r in led:
        if r["key"] in owner:
            day = rand_day(rng, r["valid_from"], r["valid_to"])
            d = owner[r["key"]]
            tickets.append({"date": day, "key": r["key"], "value": r["value"], "style": "cite", "cites": f"{d['doc']} v{version_at(d, day)}"})
    for key, md in STALE_CITES_B:
        day, d = f"{YEAR}-{md}", owner[key]
        now = value_at(led, key, day)["value"]
        older = [(v, start) for v, start in d["versions"] if start <= day and value_at(led, key, start)["value"] != now]
        if not older:
            raise ValueError(f"{key} on {day}: no earlier {d['doc']} version with a different value")
        v, start = older[-1]
        tickets.append({"date": day, "key": key, "value": value_at(led, key, start)["value"], "style": "stale_cite", "cites": f"{d['doc']} v{v}"})
    tickets.sort(key=lambda p: (p["date"], p["key"]))
    for i, p in enumerate(tickets, start=1):
        p.update({"id": f"qb-{i:03d}", "kind": rng.choice(("ticket", "call log")), "phase": "b"})
    plan = sorted(plan + tickets, key=lambda p: (p["date"], p["id"]))
    for p in plan:
        p["phase"] = "b"
    return plan


def sop_text(p: dict) -> tuple[str, dict]:
    """An SOP or governance version written by code, and the sentence that states each fact it owns."""
    head = f"Version {p['version']}, effective {p['date']}."
    lines, quotes = [f"{p['doc']} {p['title']}. {head}" + (f" Replaces version {p['version'] - 1}." if p["version"] > 1 else ""),
                     "All support agents follow this document from its effective date. Earlier versions no longer apply.", ""], {}
    for n, (k, v) in enumerate((k, v) for k, v in p["facts"].items() if not k.endswith("_version")):
        quotes[k] = f"{n + 1}. {LABEL[k]}: {v}."
        lines.append(quotes[k])
    quotes[next(k for k in p["facts"] if k.endswith("_version"))] = head
    return "\n".join(lines), quotes


def support(plan: list[dict], key: str, value: str) -> list[str]:
    """Dates from which records convey this value as true (stale, early and floated records do not count). An
    announcement or a meeting decision supports its value from the start date it gives, not from its own date."""
    return sorted(max(p["date"], p.get("effective") or p["date"]) for p in plan
                  if (p["key"] == key and p["value"] == value and p["style"] in STATES) or p.get("facts", {}).get(key) == value)


def after(day: str, n: int = 1) -> str:
    return (date.fromisoformat(day) + timedelta(days=n)).isoformat()


def plan_c(led: list[dict], dl: list[dict]) -> list[dict]:
    """Phase C record plan: an announcement before every change of a fact no SOP owns (Calder announced early, then
    moved), meeting notes that decide 20 SOP-owned changes ahead of time plus one floated price that never ships,
    two customer newsletters a month that restate a fact in force, and 40 off-topic chatter threads with no fact."""
    rng = random.Random(SEED + 4)
    owned = {k for d in dl for k in d["keys"]}
    key, early_day, early_start, delay_day = EARLY_ANNOUNCE_C
    ann, rest = [], []
    for r in led:
        if r["kind"] != "changing" or r["valid_from"] == f"{YEAR}-01-01":
            continue
        if r["key"] not in owned:
            if r["key"] == key and r["valid_from"] == f"{YEAR}-04-01":
                ann.append({"date": f"{YEAR}-{early_day}", "key": key, "value": r["value"], "style": "early_announce",
                            "effective": f"{YEAR}-{early_start}"})
                ann.append({"date": f"{YEAR}-{delay_day}", "key": key, "value": r["value"], "style": "delay",
                            "effective": r["valid_from"], "was": f"{YEAR}-{early_start}"})
            else:
                ann.append({"date": after(r["valid_from"], -rng.randint(3, 10)), "key": r["key"], "value": r["value"],
                            "style": "announce", "effective": r["valid_from"]})
    changes = [r for r in led if r["kind"] == "changing" and r["key"] in owned and r["valid_from"] != f"{YEAR}-01-01"]
    for r in rng.sample(changes, 20):
        rest.append({"date": after(r["valid_from"], -rng.randint(5, 20)), "key": r["key"], "value": r["value"],
                     "style": "plan", "effective": r["valid_from"], "kind": "meeting notes"})
    fk, fday, fval, fstart = FLOATED_C
    rest.append({"date": f"{YEAR}-{fday}", "key": fk, "value": fval, "style": "floated", "effective": f"{YEAR}-{fstart}",
                 "kind": "meeting notes"})
    keys = sorted({r["key"] for r in led if r["kind"] in ("stable", "changing")})
    for m in range(1, 13):
        for d in (6, 16):
            day, k = f"{YEAR}-{m:02d}-{d:02d}", rng.choice(keys)
            rest.append({"date": day, "key": k, "value": value_at(led, k, day)["value"],
                         "style": rng.choice(("normal", "rephrase")), "kind": "newsletter"})
    for _ in range(40):
        rest.append({"date": rand_day(rng, START.isoformat(), None), "key": None, "value": None, "style": "noise", "kind": "chatter"})
    ann.sort(key=lambda p: (p["date"], p["key"]))
    for i, p in enumerate(ann, start=1):
        p.update({"id": f"ann-{i:03d}", "kind": "announcement"})
    rest.sort(key=lambda p: (p["date"], p["key"] or ""))
    for i, p in enumerate(rest, start=1):
        p["id"] = f"qc-{i:03d}"
    plan = sorted(ann + rest, key=lambda p: (p["date"], p["id"]))
    for p in plan:
        p["phase"] = "c"
    return plan


def questions_a(led: list[dict], plan: list[dict]) -> list[dict]:
    """About 60 dated questions, each asked when replay reaches its date. Each as_of falls after at least one
    record that states the expected value, so a correct memory can always answer."""
    rng = random.Random(SEED + 1)
    picks = []

    def pick(key: str, kind: str, not_before: str | None = None) -> None:
        options = []
        for r in led:
            days = [d for d in support(plan, key, r["value"]) if d >= r["valid_from"]] if r["key"] == key else []
            if not days:
                continue
            lo = max([after(days[0])] + ([after(not_before)] if not_before else []))
            if lo < (r["valid_to"] or after(END.isoformat())):
                options.append((r, lo))
        if not options:
            raise ValueError(f"No answerable date for {key} ({kind})")
        r, lo = rng.choice(options)
        picks.append((key, rand_day(rng, lo, r["valid_to"]), kind))

    for key in sorted({r["key"] for r in led if r["kind"] == "changing"}):
        pick(key, "current")
    for key in rng.sample(sorted({r["key"] for r in led if r["kind"] == "stable"}), 6):
        pick(key, "stable")
    for key, md, _, _ in CONTRADICTIONS_A[::2]:
        pick(key, "contradiction", f"{YEAR}-{md}")
    for key in HOT:
        pick(key, "hot", f"{YEAR}-06-01")
    out = []
    for n, (key, day, kind) in enumerate(sorted(picks, key=lambda q: q[1]), start=1):
        truth = value_at(led, key, day)
        if not any(d <= day for d in support(plan, key, truth["value"])):
            raise ValueError(f"{key} at {day}: no record states {truth['value']!r} by then")
        history = [r["value"] for r in led if r["key"] == key and r["value"] != truth["value"]]
        out.append({"id": f"qa-q{n:02d}", "key": key, "as_of": day, "question": ASK[key], "expected": truth["value"],
                    "other_values": history, "kind": kind, "phase": "a"})
    return out


def questions_b(led: list[dict], plan: list[dict], dl: list[dict]) -> list[dict]:
    """About 60 dated questions over phases A and B together: every SOP-owned fact, every ticket-only fact, the
    version in force of each document, each stale citation on its day, and 6 stable controls."""
    rng = random.Random(SEED + 3)
    owned = {k for d in dl for k in d["keys"]}
    ask = {**ASK, **{version_key(d): f"Which version of {d['doc']} {d['title']} is in force?" for d in dl}}
    picks = []

    def pick(key: str, kind: str) -> None:
        options = []
        for r in led:
            days = [d for d in support(plan, key, r["value"]) if d >= r["valid_from"]] if r["key"] == key else []
            if days and after(days[0]) < (r["valid_to"] or after(END.isoformat())):
                options.append((r, after(days[0])))
        if not options:
            raise ValueError(f"No answerable date for {key} ({kind})")
        r, lo = rng.choice(options)
        picks.append((key, rand_day(rng, lo, r["valid_to"]), kind))

    for key in sorted({r["key"] for r in led if r["kind"] == "changing"}):
        pick(key, "sop key" if key in owned else "ticket key")
    for d in dl:
        pick(version_key(d), "doc version")
    for p in plan:
        if p.get("style") == "stale_cite":
            picks.append((p["key"], p["date"], "stale citation"))
    for key in rng.sample(sorted({r["key"] for r in led if r["kind"] == "stable"}), 6):
        pick(key, "stable")
    out = []
    for n, (key, day, kind) in enumerate(sorted(picks, key=lambda q: q[1]), start=1):
        truth = value_at(led, key, day)
        if not any(d <= day for d in support(plan, key, truth["value"])):
            raise ValueError(f"{key} at {day}: no record states {truth['value']!r} by then")
        history = [r["value"] for r in led if r["key"] == key and r["value"] != truth["value"]]
        out.append({"id": f"qb-q{n:02d}", "key": key, "as_of": day, "question": ask[key], "expected": truth["value"],
                    "other_values": history, "kind": kind, "phase": "b"})
    return out


def questions_c(led: list[dict], plan: list[dict], dl: list[dict]) -> list[dict]:
    """About 60 dated questions over phases A, B and C: every fact on a date after its newest announced or decided value
    starts, 10 changes asked between the notice and the start (expected: the old value), Calder between the early date
    and the real start, Spark after the floated $46 start, and 6 stable controls."""
    rng = random.Random(SEED + 5)
    owned = {k for d in dl for k in d["keys"]}
    picks = []
    for key in sorted({r["key"] for r in led if r["kind"] == "changing"}):
        options = []
        for r in led:
            days = [d for d in support(plan, key, r["value"]) if d >= r["valid_from"]] if r["key"] == key and r["valid_from"] != f"{YEAR}-01-01" else []
            if days and after(days[0]) < (r["valid_to"] or after(END.isoformat())):
                options.append((r, after(days[0])))
        if not options:
            raise ValueError(f"No answerable date for {key}")
        r, lo = rng.choice(options)
        picks.append((key, rand_day(rng, lo, r["valid_to"]), "sop key" if key in owned else "ticket key"))
    ahead = []
    for p in plan:
        if p.get("phase") == "c" and p["style"] in ("announce", "plan"):
            old = value_at(led, p["key"], p["date"])
            first = [d for d in support(plan, p["key"], old["value"]) if d >= old["valid_from"]]
            lo = max([after(p["date"])] + ([after(first[0])] if first else []))
            if first and lo < p["effective"]:
                ahead.append((p["key"], rand_day(rng, lo, p["effective"]), "announced, not yet"))
    picks += rng.sample(ahead, 10)
    key, _, early_start, _ = EARLY_ANNOUNCE_C
    picks.append((key, rand_day(rng, f"{YEAR}-{early_start}", f"{YEAR}-04-01"), "early announcement"))
    fk, _, fval, fstart = FLOATED_C
    picks.append((fk, rand_day(rng, after(f"{YEAR}-{fstart}"), None), "never valid"))
    for key in rng.sample(sorted({r["key"] for r in led if r["kind"] == "stable"}), 6):
        picks.append((key, rand_day(rng, after(min(support(plan, key, value_at(led, key, f"{YEAR}-01-01")["value"]))), None), "stable"))
    out = []
    for n, (key, day, kind) in enumerate(sorted(picks, key=lambda q: q[1]), start=1):
        truth = value_at(led, key, day)
        if not any(d <= day for d in support(plan, key, truth["value"])):
            raise ValueError(f"{key} at {day}: no record states {truth['value']!r} by then")
        history = [r["value"] for r in led if r["key"] == key and r["value"] != truth["value"]] + ([fval] if kind == "never valid" else [])
        out.append({"id": f"qc-q{n:02d}", "key": key, "as_of": day, "question": ASK[key], "expected": truth["value"],
                    "other_values": history, "kind": kind, "phase": "c"})
    return out


def subject(key: str) -> str:
    return ASK[key].rstrip("?")


def names_value(value: str, text: str) -> bool:
    """A phase C record must carry its value's numbers as digits and its names (Calder, PayPal, QB-2), so the fact is
    in the text and not only implied ('the new phase', 'five dollars')."""
    words = value.replace(",", " ").split()
    nums = re.findall(r"\d+", value)
    names = [w for w in words[1:] if w[:1].isupper()]
    return (all(re.search(rf"(?<!\d){n}(?!\d)", text) for n in nums)
            and all(re.search(rf"(?<!\w){re.escape(w)}", text) for w in names))


def spoken(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d:%B} {d.day}, {d.year}"


def write_prompt(batch: list[dict]) -> str:
    if all(p.get("kind") in KIND_TEXT for p in batch):
        return write_prompt_c(batch)
    lines = []
    for p in batch:
        how = {"normal": "states it plainly",
               "rephrase": "states it in different everyday words (for example 'two weeks' for 14 days), without copying the wording",
               "stale": "has the agent wrongly quote this old value as if still current; nobody corrects it",
               "early": "states this value before it officially starts, as if already in effect; nobody corrects it",
               "cite": f"has the agent state it and name the rule it comes from, written exactly as \"{p.get('cites')}\"",
               "stale_cite": f"has the agent quote it from an outdated version, written exactly as \"{p.get('cites')}\", as if still in force; nobody corrects it",
               }[p["style"]]
        lines.append(f'- id {p["id"]}, {p["date"]}, {p["kind"]}: conveys "{subject(p["key"])}" = "{p["value"]}"; the record {how}.')
    return ("Write these customer-support records for Quillmere Broadband, a made-up regional home-internet provider. "
            f"Each record is {WORDS[0]} to {WORDS[1]} words, written as a real {', '.join(sorted({p['kind'] for p in batch}))} "
            "with a made-up customer name, the issue, what the agent said and the outcome. Each record must convey only "
            "its one assigned fact about Quillmere; any other detail must be ordinary (names, the customer's problem), never "
            "another Quillmere price, fee, rule, number or date. Do not mention dates of policy changes unless asked. "
            "Never use em dashes or en dashes. For each record also return 'quote': the exact sentence from your text that "
            "conveys the fact.\n\n" + "\n".join(lines))


def write_prompt_c(batch: list[dict]) -> str:
    """Phase C: internal and customer-facing records that are not tickets. Each conveys its one fact, or none."""
    lines = []
    for p in batch:
        if p["style"] == "noise":
            lines.append(f'- id {p["id"]}, {p["date"]}, {p["kind"]}: conveys no Quillmere fact at all. Staff talk about lunch, '
                         "sports, weekend plans or the office; any numbers are about those, never a Quillmere price, fee, plan, "
                         "speed, rule, phone number or support detail. For 'quote' return any one sentence of the text.")
            continue
        start, was = (spoken(p[k]) if p.get(k) else None for k in ("effective", "was"))
        how = {"normal": "states it plainly as true now",
               "rephrase": "states it as true now in different everyday words, without copying the wording",
               "announce": f"announces that this becomes the value from {start}, and gives that start date",
               "early_announce": f"announces that this becomes the value from {start}, and gives that start date",
               "delay": f"says the change announced for {was} is delayed: this becomes the value from {start} instead, "
                        "and gives that new start date",
               "plan": f"records the team's decision that this becomes the value from {start}, and gives that start date",
               "floated": f"has one attendee float this as an idea for {start}; nothing is decided or approved, and the notes say so",
               }[p["style"]]
        lines.append(f'- id {p["id"]}, {p["date"]}, {p["kind"]}: conveys "{subject(p["key"])}" = "{p["value"]}"; the record {how}.')
    return ("Write these records for Quillmere Broadband, a made-up regional home-internet provider. Each record is "
            f"{WORDS[0]} to {WORDS[1]} words, written as " + "; or ".join(sorted({KIND_TEXT[p['kind']] for p in batch})) +
            ", with made-up staff names. A record that has an assigned fact conveys only that one fact about Quillmere, "
            "names the thing and writes the value as given (numbers as digits, every name); any "
            "other detail is ordinary (names, events, chit-chat), never another Quillmere price, fee, rule, number or date. "
            "Never use em dashes or en dashes. For each record also return 'quote': the exact sentence from your text that "
            "conveys the fact.\n\n" + "\n".join(lines))


SCHEMA = {"type": "object", "properties": {"records": {"type": "array", "items": {
    "type": "object", "properties": {"id": {"type": "string"}, "text": {"type": "string"}, "quote": {"type": "string"}},
    "required": ["id", "text", "quote"], "additionalProperties": False}}},
    "required": ["records"], "additionalProperties": False}


def batches(plan: list[dict], size: int = 8) -> list[list[dict]]:
    return [plan[i:i + size] for i in range(0, len(plan), size)]


def check(batch: list[dict], got: list[dict]) -> list[dict]:
    """Every planned id back once, quote inside text, no dashes. Fails loudly."""
    by = {g["id"]: g for g in got}
    if set(by) != {p["id"] for p in batch} or len(got) != len(batch):
        raise ValueError(f"Batch ids differ: planned {[p['id'] for p in batch]}, got {[g['id'] for g in got]}")
    out = []
    for p in batch:
        g = by[p["id"]]
        if p.get("style") == "noise" and " ".join(g["quote"].split()) not in " ".join(g["text"].split()):  # chatter: any sentence
            g = {**g, "quote": re.split(r"(?<=[.!?])\s+", " ".join(g["text"].split()))[0]}
        quote, text = " ".join(g["quote"].split()), " ".join(g["text"].split())
        if quote not in text:  # a local model often misquotes itself: take the sentence that states the value, or the
            sents = re.split(r"(?<=[.!?])\s+", text)  # text sentence most like its quote
            stating = [x for x in sents if p.get("value") and p["value"].lower() in x.lower()]
            words = set(re.findall(r"\w+", quote.lower()))
            best = stating[0] if stating else max(reversed(sents), key=lambda x: len(words & set(re.findall(r"\w+", x.lower()))) / (len(set(re.findall(r"\w+", x.lower()))) or 1))
            if not stating and len(words & set(re.findall(r"\w+", best.lower()))) < 0.6 * len(set(re.findall(r"\w+", best.lower()))):
                raise ValueError(f"{p['id']}: quote is not in the text")
            g = {**g, "quote": best}
        if any(c in g["text"] for c in ("\u2014", "\u2013")):
            raise ValueError(f"{p['id']}: text has a dash")
        if p.get("phase") == "c" and p.get("value") and not names_value(p["value"], g["text"]):
            raise ValueError(f"{p['id']}: text does not give the value {p['value']!r}")
        if p.get("cites") and p["cites"].split()[0] not in g["text"]:
            raise ValueError(f"{p['id']}: text does not name {p['cites'].split()[0]}")
        out.append({**p, "text": g["text"].strip(), "quote": g["quote"].strip()})
    return out


def write(client, phase: str, cap: float) -> int:
    """Records for the plan. SOP and governance versions are written by code; a local model writes one record per
    call and gets 5 tries, at rising temperature, to pass the checks; a record that never passes is left out and named."""
    plan = [json.loads(l) for l in (out_dir() / f"quillmere-plan-{phase}.jsonl").read_text(encoding="utf-8").splitlines()]
    dest = kb_dir(phase) / "records.jsonl"
    dest.parent.mkdir(parents=True, exist_ok=True)
    have = [json.loads(l) for l in dest.read_text(encoding="utf-8").splitlines()] if dest.exists() else []
    done, spent = {r["id"] for r in have}, 0.0
    local = getattr(client, "local", False)
    with open(dest, "a", encoding="utf-8", newline="\n") as f:
        for p in plan:
            if p["style"] == "official" and p["id"] not in done:
                text, quotes = sop_text(p)
                f.write(json.dumps({**p, "text": text, "quote": next(iter(quotes.values())), "quotes": quotes,
                                    "stream": "quillmere", "gen_cost": 0.0}) + "\n")
    for b in batches([p for p in plan if p["style"] != "official"], 1 if local else 8):
        if all(p["id"] in done for p in b):
            continue
        rows = None
        for attempt in range(5 if local else 1):
            extra = {"temperature": 0.3 * attempt} if local else {}  # at temperature 0 a retry repeats the same text
            resp = client.messages.create(model=MODEL, max_tokens=2000 if local else 16000, output_config={"effort": "low", "format": {
                "type": "json_schema", "schema": SCHEMA}}, messages=[{"role": "user", "content": write_prompt(b)}], **extra)
            if resp.stop_reason != "end_turn":
                raise SystemExit(f"Batch {b[0]['id']}: stopped with {resp.stop_reason}")
            try:
                rows = check(b, json.loads(next(x.text for x in resp.content if x.type == "text"))["records"])
                break
            except (ValueError, json.JSONDecodeError) as e:
                if not local:
                    raise
                print(f"{b[0]['id']}: retry, {e}", flush=True)
        if rows is None:  # a local model may never pass: the record is left out and named, the run goes on
            print(f"SKIPPED {b[0]['id']} after 5 tries", flush=True)
            continue
        c = cost(MODEL, usage(resp))
        spent += c
        with open(dest, "a", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps({**r, "stream": "quillmere", "gen_cost": c / len(rows)}) + "\n")
        print(b[0]["id"], "to", b[-1]["id"], f"${spent:.2f}", flush=True)
        if spent > cap:
            raise SystemExit(f"Spend ${spent:.2f} passed the cap ${cap:.2f}; stopped")
    return 0


def build(phase: str) -> int:
    if phase not in ("a", "b", "c"):
        raise SystemExit("Only phases A, B and C are planned")
    sheet = (out_dir() / "quillmere-company.md").read_text(encoding="utf-8")
    led = ledger(sheet)
    if phase == "a":
        plan = plan_a(led)
        qs = questions_a(led, plan)
        files = (("quillmere-ledger.jsonl", led), ("quillmere-plan-a.jsonl", plan), ("quillmere-questions.jsonl", qs))
    else:
        dl = docs(sheet)
        led = led + doc_ledger(dl)
        earlier = [json.loads(l) for ph in "ab"[: "bc".index(phase) + 1]
                   for l in (out_dir() / f"quillmere-plan-{ph}.jsonl").read_text(encoding="utf-8").splitlines()]
        plan = plan_b(led, dl) if phase == "b" else plan_c(led, dl)
        qs = (questions_b if phase == "b" else questions_c)(led, earlier + plan, dl)
        old_qs = [json.loads(l) for l in (out_dir() / "quillmere-questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        files = ((f"quillmere-ledger-{phase}.jsonl", led), (f"quillmere-plan-{phase}.jsonl", plan),
                 ("quillmere-questions.jsonl", [q for q in old_qs if q["phase"] != phase] + qs))
    for name, rows in files:
        (out_dir() / name).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")
    styles = {s: sum(p["style"] == s for p in plan) for s in sorted({p["style"] for p in plan})}
    print(json.dumps({"ledger_rows": len(led), "records": len(plan), "styles": styles, "questions": len(qs),
                      "question_kinds": {k: sum(q["kind"] == k for q in qs) for k in sorted({q["kind"] for q in qs})}}))
    return 0


def estimate(phase: str) -> int:
    plan = [json.loads(l) for l in (out_dir() / f"quillmere-plan-{phase}.jsonl").read_text(encoding="utf-8").splitlines()]
    i, o, _, _ = PRICES[MODEL]
    words = sum(WORDS) / 2
    out_tok = len(plan) * (words * 1.35 + 60)  # text plus quote and JSON keys
    in_tok = sum(len(write_prompt(b)) / 4 for b in batches(plan))
    print(json.dumps({"records": len(plan), "batches": len(batches(plan)), "input_tokens": round(in_tok),
                      "output_tokens": round(out_tok), "write_cost": round((in_tok * i + out_tok * o) / 1e6, 2)}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.stream")
    mode = ap.add_mutually_exclusive_group(required=True)
    for m in ("ledger", "estimate", "write"):
        mode.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--phase", default="a")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--cap", type=float, default=3.0)
    ap.add_argument("--local", metavar="MODEL", help="--write: a local model (llama-server) writes the records, at no cost")
    a = ap.parse_args(argv)
    if a.ledger:
        return build(a.phase)
    if a.estimate:
        return estimate(a.phase)
    if not a.yes:
        raise SystemExit("This spends Claude credit; pass --yes")
    if a.local:
        from hces.local_llm import LocalClient

        return write(LocalClient(a.local), a.phase, a.cap)
    import anthropic

    return write(anthropic.Anthropic(), a.phase, a.cap)


if __name__ == "__main__":
    raise SystemExit(main())
