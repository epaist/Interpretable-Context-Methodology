"""Stage 04 HTML report: the scorecard, rotation, noise, second rubric, confirmation and audit in one page.

  python -m hces.report_html

Reads the markdown files in stages/04-exam/output and writes report.html beside them. No network,
no scripts; one self-contained page with light and dark themes.
"""

from __future__ import annotations

import html
import re

from hces.exam import output_dir

ORDER = ("audit.md", "scorecard.md", "rotation.md", "confirm.md", "noise.md", "rubric2.md", "answer-probe.md")
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e3e1da;--head:#f1efe8;--bad:#a3341f;--good:#2f6b3a}
@media (prefers-color-scheme:dark){:root{--bg:#171715;--fg:#ecebe6;--muted:#a3a29b;--line:#34332f;--head:#22221f;--bad:#e2725b;--good:#7cc08a}}
body{background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;padding:24px 16px}
main{max-width:1100px;margin:0 auto}h1{font-size:1.6rem}h2{font-size:1.2rem;margin-top:2.2rem;border-top:1px solid var(--line);padding-top:1rem}
p{color:var(--muted);max-width:75ch}.wrap{overflow-x:auto}table{border-collapse:collapse;font-size:.85rem;margin:.6rem 0 1rem}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:var(--head)}
td.fail{color:var(--bad);font-weight:600}td.pass{color:var(--good);font-weight:600}
"""


def inline(text: str) -> str:
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", t)


def cell(text: str, tag: str) -> str:
    t = text.strip()
    cls = ' class="fail"' if tag == "td" and (t.startswith("FAIL") or t == "NO") else (' class="pass"' if t.startswith("PASS") else "")
    return f"<{tag}{cls}>{inline(t)}</{tag}>"


def md_to_html(md: str, level_shift: int) -> str:
    out, table = [], []

    def flush():
        if table:
            rows = [r for r in table if not re.match(r"^\|[\s\-|]+\|$", r)]
            cells = [[c for c in r.strip().strip("|").split("|")] for r in rows]
            body = "".join("<tr>" + "".join(cell(c, "th" if i == 0 else "td") for c in row) + "</tr>" for i, row in enumerate(cells))
            out.append(f'<div class="wrap"><table>{body}</table></div>')
            table.clear()

    for line in md.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        flush()
        m = re.match(r"^(#+)\s+(.*)", line)
        if m:
            n = min(6, len(m.group(1)) + level_shift)
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif line.startswith("- "):
            out.append(f"<p>{inline(line[2:])}</p>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "\n".join(out)


def main(argv=None) -> int:
    out = output_dir()
    parts = [md_to_html((out / name).read_text(encoding="utf-8"), 1) for name in ORDER if (out / name).exists()]
    page = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" "
            "content=\"width=device-width,initial-scale=1\"><title>HCES Stage 04 Exam</title><style>" + CSS +
            "</style></head><body><main><h1>HCES Stage 04: The Exam</h1>" + "\n".join(parts) + "</main></body></html>\n")
    (out / "report.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out / 'report.html'} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
