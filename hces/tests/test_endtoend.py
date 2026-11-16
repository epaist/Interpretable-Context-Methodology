from hces.endtoend import NOT_IN_DOCS, cost, full_request, gated_request, points


def test_points_reward_abstaining_only_on_unanswerable():
    assert points("abstained", False) == 1.0
    assert points("correct", False) == 0.0
    assert points("abstained", True) == 0.0
    assert points("partial", True) == 0.5
    assert points("correct", True) == 1.0


def test_cost_prices_cache_reads_below_input():
    base = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    read = cost("claude-opus-5-5", {**base, "cache_read": 1_000_000})
    fresh = cost("claude-opus-5-5", {**base, "input": 1_000_000})
    assert read < fresh


def test_both_arms_share_instructions_and_only_full_is_cached():
    g = gated_request("claude-opus-5-5", [{"id": "v/p1", "tokens": 3, "text": "hello"}], "Q?")
    f = full_request("claude-opus-5-5", "v", "the book", "Q?")
    assert g["system"][0] == f["system"][0]
    assert NOT_IN_DOCS in g["system"][0]["text"]
    assert "cache_control" in f["system"][1] and "cache_control" not in g["system"][0]
    assert "Q?" in g["messages"][0]["content"] and f["messages"][0]["content"] == "Q?"
