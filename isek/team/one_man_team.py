from isek.team.base import Team, TeamCard
from isek.agent.isek_agent import IsekAgent


class OneManTeam(Team):
    """A simple team implementation for testing and basic use cases."""

    def __init__(self, name: str, description: str, agent):
        self.name = name or "SimpleTeam"
        self.description = description or "A simple team for testing"
        self.agent = agent or IsekAgent()

    def run(self, prompt: str) -> str:
        output_msg = self.agent.run(prompt)
        return output_msg

    def get_team_card(self) -> TeamCard:
        """Get team card for A2A protocol."""
        return TeamCard(
            name=self.name,
            bio=self.description,
            lore="Created for testing purposes",
            knowledge="Basic testing knowledge",
            routine="Respond to messages",
        )
