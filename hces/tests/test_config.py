import pytest

from hces import config

TABLE = """# Constants

| Name | Value | Why |
|------|-------|-----|
| JEV model | jev-1.14.0 | x |
| Vector store | sqlite-vec plus SQLite FTS5 | x |
| Embedder | bge-small-en-v1.5 (via fastembed, CPU) | x |
| Token budget | 6000 | x |
| Candidate sweep | 20, 50, 100 | x |
| Python | .venv\\Scripts\\python.exe | x |
| Judge workers | 6 | x |
| Results store | `hces/data/results.db` | x |
| JEV state cap | 32k tokens per question, 64k per request | x |
| JEV price | $0.042 per million input tokens, output free | x |

## Starting Bars

| Measure | Bar |
|---------|-----|
| Speed | later |
"""


def write(tmp_path, text):
    p = tmp_path / "constants.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_parses_all_values(tmp_path):
    c = config.load(write(tmp_path, TABLE))
    assert c.jev_model == "jev-1.14.0"
    assert c.embedder == "BAAI/bge-small-en-v1.5"
    assert c.token_budget == 6000
    assert c.top_k_sweep == (20, 50, 100)
    assert c.judge_workers == 6
    assert c.state_cap_question == 32000 and c.state_cap_request == 64000
    assert c.price_per_million == pytest.approx(0.042)
    assert c.results_store == config.ROOT / "hces" / "data" / "results.db"


def test_placeholder_is_refused(tmp_path):
    with pytest.raises(config.ConfigError, match="placeholder"):
        config.load(write(tmp_path, TABLE.replace("| 6000 |", "| {{TOKEN_BUDGET}} |")))


def test_missing_row_is_refused(tmp_path):
    with pytest.raises(config.ConfigError, match="Judge workers"):
        config.load(write(tmp_path, TABLE.replace("| Judge workers | 6 | x |\n", "")))


def test_real_constants_file_loads():
    c = config.load()
    assert c.token_budget > 0 and c.top_k_sweep
