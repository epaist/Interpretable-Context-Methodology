import pytest

from hces import local_llm as L
from hces.endtoend import cost, usage


def test_request_body_maps_system_schema_and_limits():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}}
    b = L.request_body("qwen", 300, "be brief", {"effort": "low", "format": {"type": "json_schema", "schema": schema}},
                       [{"role": "user", "content": "hi"}])
    assert b["messages"][0] == {"role": "system", "content": "be brief"}
    assert b["response_format"]["json_schema"]["schema"] == schema and b["max_tokens"] == 300 and b["stream"] is False


def test_request_body_rejects_unknown_format():
    with pytest.raises(ValueError):
        L.request_body("qwen", 10, None, {"format": {"type": "xml"}}, [{"role": "user", "content": "x"}])


def test_reply_reads_like_anthropic_and_costs_nothing():
    raw = {"choices": [{"message": {"content": '{"a": "b"}'}, "finish_reason": "stop"}],
           "usage": {"prompt_tokens": 50, "completion_tokens": 9}}
    m = L.to_message(raw)
    assert m.stop_reason == "end_turn" and m.content[0].text == '{"a": "b"}'
    assert cost("claude-opus-5-5", usage(m)) == 0 and m.local_tokens == (50, 9)
    assert L.to_message({"choices": [{"message": {"content": None}, "finish_reason": "length"}]}).stop_reason == "max_tokens"
