"""A local model behind the slice of the Anthropic client that stage 06 uses, so runs cost nothing.

  client = LocalClient("Qwen3.5-9B-Q4_K_M.gguf", host="http://127.0.0.1:11435")
  client.messages.create(model=..., max_tokens=..., system=..., output_config=..., messages=[...])

Talks to an OpenAI-compatible /v1/chat/completions server: llama.cpp's llama-server (used on this PC, in Docker)
or Ollama. A json_schema format in output_config becomes response_format json_schema. Usage is reported as zero
tokens, so cost() prices every local call at $0. The model argument of create() is ignored: the local model named
at construction answers every call.
"""

from __future__ import annotations

import json
import urllib.request
from types import SimpleNamespace

HOST = "http://127.0.0.1:11435"


def request_body(model: str, max_tokens: int, system: str | None, output_config: dict | None, messages: list[dict],
                 temperature: float = 0) -> dict:
    msgs = ([{"role": "system", "content": system}] if system else []) + [
        {"role": m["role"], "content": m["content"]} for m in messages]
    body = {"model": model, "messages": msgs, "stream": False, "max_tokens": max_tokens, "temperature": temperature}
    fmt = (output_config or {}).get("format")
    if fmt:
        if fmt.get("type") != "json_schema":
            raise ValueError(f"Unsupported output format {fmt.get('type')!r}")
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "out", "strict": True, "schema": fmt["schema"]}}
    return body


def to_message(raw: dict) -> SimpleNamespace:
    """OpenAI-style reply -> the fields stage 06 reads: stop_reason, content[].type/.text, usage."""
    choice = raw["choices"][0]
    done = choice.get("finish_reason", "stop")
    u = raw.get("usage", {})
    return SimpleNamespace(
        stop_reason={"stop": "end_turn", "length": "max_tokens"}.get(done, done),
        content=[SimpleNamespace(type="text", text=choice["message"]["content"] or "")],
        usage=SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0),
        local_tokens=(u.get("prompt_tokens", 0), u.get("completion_tokens", 0)),
    )


class _Messages:
    def __init__(self, model: str, host: str, timeout: float):
        self.model, self.host, self.timeout = model, host, timeout

    def create(self, model: str, max_tokens: int, messages: list[dict], system: str | None = None,
               output_config: dict | None = None, temperature: float = 0) -> SimpleNamespace:
        body = json.dumps(request_body(self.model, max_tokens, system, output_config, messages, temperature)).encode()
        req = urllib.request.Request(f"{self.host}/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return to_message(json.loads(r.read()))


class LocalClient:
    def __init__(self, model: str, host: str = HOST, timeout: float = 300):
        self.messages = _Messages(model, host, timeout)
        self.local = True  # memory.extract adds LOCAL_HINT for local models


def models(host: str = HOST) -> list[str]:
    with urllib.request.urlopen(f"{host}/v1/models", timeout=5) as r:
        return [m["id"] for m in json.loads(r.read())["data"]]
