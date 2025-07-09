from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from isek.utils.print_utils import print_response


@dataclass
class AdapterCard:
    name: str
    bio: str
    lore: str
    knowledge: str
    routine: str


class Adapter(ABC):
    """
    Abstract base class for all team implementations.

    This class defines the interface that all team implementations must follow.
    Teams can coordinate multiple agents or other teams to work together.
    """

    @abstractmethod
    def run(self, prompt: str, **kwargs) -> str:
        """
        Execute the team's main functionality with the given prompt.

        Args:
            prompt: The input prompt or task for the team to process
            **kwargs: Additional keyword arguments

        Returns:
            str: The team's response or result

        Raises:
            NotImplementedError: If the concrete class doesn't implement this method
        """
        pass

    @abstractmethod
    def get_adapter_card(self) -> AdapterCard:
        """
        Get metadata about the team for discovery and identification purposes.

        Returns:
            TeamCard: A card containing team metadata including name, bio, lore, knowledge, and routine

        Raises:
            NotImplementedError: If the concrete class doesn't implement this method
        """
        pass

    def print_response(self, *args, **kwargs):
        """
        Proxy to the shared print_response utility, passing self.run as run_func.
        """
        return print_response(self.run, *args, **kwargs)
