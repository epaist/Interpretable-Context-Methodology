"""The embedder interface. fastembed now; fasttextembed is compared in the stage 03 bake-off."""

from __future__ import annotations

from typing import Protocol, Sequence


class Embedder(Protocol):
    model_id: str
    dim: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class FastEmbedder:
    """fastembed (ONNX Runtime). batch_size=1: on the PC, batch 64 peaked at 1,346 MB and batch 1 at
    243 MB for the same speed (stage 03 sweep), because memory grows with batch x passage length."""

    def __init__(self, model_id: str, dim: int = 384, batch_size: int = 1):
        from fastembed import TextEmbedding

        self.model_id = model_id
        self.dim = dim
        self.batch_size = batch_size
        self._model = TextEmbedding(model_name=model_id)

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = [list(map(float, v)) for v in self._model.embed(list(texts), batch_size=self.batch_size)]
        for v in vectors:
            if len(v) != self.dim:
                raise ValueError(f"{self.model_id} returned {len(v)} dimensions, expected {self.dim}")
        return vectors
