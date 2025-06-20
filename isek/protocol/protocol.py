from abc import ABC, abstractmethod
from typing import Any, Optional

from isek.squad.default_squad import DefaultSquad
from isek.squad.squad import Squad


class Protocol(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        squad: Optional[Squad] = None,
        **kwargs: Any,
    ):
        self.squad = squad or DefaultSquad()
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
