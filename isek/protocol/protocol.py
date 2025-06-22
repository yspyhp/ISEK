from abc import ABC, abstractmethod
from typing import Any, Optional

from isek.adapter.base import Adapter


class Protocol(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        adapter: Optional[Adapter] = None,
        **kwargs: Any,
    ):
        self.adapter = adapter
        self.host = host or "localhost"
        self.port = port or 8080

    @abstractmethod
    def bootstrap_server(self):
        pass

    @abstractmethod
    def stop_server(self) -> None:
        pass

    @abstractmethod
    def send_message(self, target_address, message):
        pass
