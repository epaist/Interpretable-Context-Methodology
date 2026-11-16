from hces.rollup import Scored, fill


def s(uid, score, crit=0.0, rank=1, tokens=100, failed=False):
    return Scored(uid, tokens, score, crit, rank, failed)


def test_critical_first_then_score_then_unsure():
    kept, cut = fill([s("low", 0.2), s("unsure", 0.55, rank=1), s("good", 0.8, rank=5), s("crit", 0.3, crit=0.9, rank=9)], 1000)
    assert [u.unit_id for u, _ in kept] == ["crit", "good", "unsure"]
    assert cut[0][0].unit_id == "low" and "below" in cut[0][1]


def test_budget_is_never_exceeded_and_ties_go_to_rank():
    kept, cut = fill([s("b", 0.8, rank=2, tokens=300), s("a", 0.8, rank=1, tokens=300), s("c", 0.7, tokens=50)], 400)
    assert [u.unit_id for u, _ in kept] == ["a", "c"]
    assert sum(u.tokens for u, _ in kept) <= 400 and "no room" in cut[0][1]


def test_failed_judgment_kept_only_after_unsure():
    kept, _ = fill([s("f", 0.0, failed=True), s("u", 0.52)], 1000)
    assert [u.unit_id for u, _ in kept] == ["u", "f"]


def test_cutoffs_can_be_passed_without_touching_defaults():
    from hces.rollup import Cutoffs
    u = Scored("u", 10, 0.5, 0.0, 1)
    kept, _ = fill([u], 100, Cutoffs(cutoff=0.75, unsure_low=0.75, critical_at=0.5))
    assert kept == []
    kept, _ = fill([u], 100)
    assert [k.unit_id for k, _ in kept] == ["u"]
