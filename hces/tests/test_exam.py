from hces.exam import best, evaluate
from hces.rollup import Cutoffs, Scored


def case(units, gold, answerable=True, needle=False, decoys=()):
    return {"id": "v/q", "shape": "plain", "answerable": answerable, "needle": needle,
            "gold": set(gold), "decoys": set(decoys), "units": units}


def test_evaluate_counts_gold_share_and_decoys():
    cs = [case([Scored("g", 100, 1.0, 0.9, 1), Scored("d", 300, 0.75, 0.0, 2)], ["g"], decoys=["d"])]
    m = evaluate(cs, Cutoffs(0.75, 0.5, 0.5), 1000)
    assert (m["gold_caught"], m["decoys_kept"]) == (1, 1) and m["gold_share"] == 0.25
    m = evaluate(cs, Cutoffs(1.0, 1.01, 0.5), 1000)
    assert (m["gold_caught"], m["decoys_kept"], m["gold_share"]) == (1, 0, 1.0)


def test_best_prefers_recall_over_precision():
    cs = [case([Scored("g", 100, 0.5, 0.0, 1), Scored("x", 100, 1.0, 0.0, 2)], ["g"])]
    c, m = best(cs, 1000)
    assert m["gold_caught"] == 1 and c.unsure_low <= 0.5


def test_compare_reports_overlap():
    from hces.exam import compare
    a = [case([Scored("g", 100, 1.0, 0.0, 1), Scored("x", 100, 1.0, 0.0, 2)], ["g"])]
    b = [case([Scored("g", 100, 1.0, 0.0, 1), Scored("x", 100, 0.0, 0.0, 2)], ["g"])]
    m = compare(a, b, Cutoffs(0.75, 0.5, 0.5), 1000)
    assert m["mean_overlap"] == 0.5 and m["same_gold_outcome"] == 1 and m["identical"] == 0
