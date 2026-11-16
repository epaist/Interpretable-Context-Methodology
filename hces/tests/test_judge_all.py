from hces.judge import Judgment
from hces.judge_all import billed_tokens


def test_billed_tokens_counts_each_request_once():
    js = [Judgment("u1", "relevance", "score", 3.0, tokens_in=500), Judgment("u1", "contains_fact", "noul", 0.9, tokens_in=500),
          Judgment("u2", "relevance", "score", 1.0, tokens_in=450), Judgment("u3", "relevance", "score", None, error="x")]
    assert billed_tokens(js) == 950


def test_done_pairs_is_per_arm(tmp_path):
    from hces.judge_all import done_pairs
    from hces.store import Store

    s = Store(tmp_path / "r.db")
    s.add_run({"run_id": "r1", "arm": "judge", "variant": "plain", "question_id": "v/q01", "access_ms": 1,
               "analysis_ms": 1, "response_ms": 1, "peak_rss_mb": 1, "tokens_in": 1, "cost_usd": 0})
    assert done_pairs(s) == {("v/q01", "plain")}
    assert done_pairs(s, "judge-repeat") == set()
