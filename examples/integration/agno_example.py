from isek.team import Team, TeamCard
from isek.node.node_v2 import Node

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from isek.team.one_man_team import OneManTeam


random_agent = Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[],
        instructions=[
            "Only can generator a random number"
        ],
        markdown=True,
    )

rn_team = OneManTeam(name="RandomNumberTeam", description="A team that generates random numbers", agent=random_agent)

# Create the server node.
server_node = Node(node_id="RN", port=8080, team=rn_team)

# Start the server in the foreground.
server_node.build_server(daemon=True)
print(server_node.team.run("random a number 0-10"))

