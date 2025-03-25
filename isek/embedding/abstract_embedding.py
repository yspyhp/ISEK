"""encoding=utf-8"""

from abc import ABC, abstractmethod
from typing import Optional


class AbstractEmbedding(ABC):

    def __init__(self, dim: Optional[int]):
        self.dim = dim

    def embedding_one(self, data: str) -> list[float]:
        return self.embedding([data])[0]

    @abstractmethod
    def embedding(self, datas: list[str]) -> list[list[float]]:
        pass
