"""The unit of text HCES judges: a passage, a section, a chapter or a whole volume."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

MAX_PASSAGE_TOKENS = 512  # bge-small reads no further than this


def approx_tokens(text: str) -> int:
    """Rough token count (4 characters per token). Stage 02 stores real counts per passage."""
    return max(1, math.ceil(len(text) / 4))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Unit:
    id: str
    text: str
    level: str = "passage"
    parent_id: str | None = None
    source: str = ""
    tokens: int = 0

    @property
    def token_count(self) -> int:
        return self.tokens or approx_tokens(self.text)
