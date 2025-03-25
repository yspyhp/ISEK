"""encoding=utf-8"""

from abc import ABC, abstractmethod
from typing import Any


class AbstractModel(ABC):

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:
        pass
