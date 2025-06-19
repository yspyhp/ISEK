from isek.squad.squad import Squad, SquadCard


class DefaultSquad(Squad):
    def __init__(self, name: str = None):
        self.name = name

    def run(self, prompt) -> str:
        return "DefaultSquad say: Hello!"

    def get_squad_card(self) -> SquadCard:
        return SquadCard(
            name=self.name or "Helper",
            bio="You are good at handling various things",
            lore="Your mission is to provide users with various assistance. "
            "Be sure to reject all requests involving politics, religion, and pornography, "
            "and do not provide anything that violates the law or morality.",
            knowledge="Provide solutions and implementation steps",
            routine="You should first understand the user's request, then provide a solution, "
            "and finally ask the user if the solution is satisfactory.",
        )
