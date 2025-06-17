from abc import ABC, abstractmethod


class Squad(ABC):
    @abstractmethod
    def run(self, prompt) -> str:
        pass

    @abstractmethod
    def get_squad_card(self) -> dict:
        pass
