from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SquadCard:
    name: str
    bio: str
    lore: str
    knowledge: str
    routine: str


class Squad(ABC):
    @abstractmethod
    def run(self, prompt) -> str:
        pass

    @abstractmethod
    def get_squad_card(self) -> SquadCard:
        pass
