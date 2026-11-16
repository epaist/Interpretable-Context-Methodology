from hces.rag import fill_budget, summarize


def test_fill_budget_keeps_whole_units_in_rank_order():
    tokens = {"a": 300, "b": 400, "c": 250, "d": 100}
    assert fill_budget(["a", "b", "c", "d"], tokens, 700) == ["a", "b"]
    assert fill_budget(["b", "a", "c", "d"], tokens, 650) == ["b", "c"]
    assert fill_budget(["a", "b", "c", "d"], tokens, 50) == []


def run(qid, gold_retrieved, gold_kept, hard=(), answerable=True, decoys=0):
    return {"variant": "vector/plain", "k": 20, "question_id": qid, "access_ms": 5.0, "peak_rss_mb": 200.0,
            "notes": {"answerable": answerable, "gold_retrieved": gold_retrieved, "gold_kept": gold_kept,
                      "decoys_kept": decoys, "tokens_used": 5000, "hard_case": list(hard)}}


def test_summary_rates_and_misses():
    s = summarize([run("n1", 1, 1, ["needle"], decoys=1), run("n2", 0, 0, ["needle"]),
                   run("q1", 2, 1), run("q2", 0, 0, answerable=False)])[0]
    assert s["retrieved_any_gold"] == round(2 / 3, 3) and s["needles_kept"] == 0.5 and s["real_kept"] == 1.0
    assert s["misses"] == ["n2"] and s["decoys_kept"] == 1
