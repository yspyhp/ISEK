from isek.adapter.base import Adapter, AdapterCard
from isek.node.node_v2 import Node
import time
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from isek.node.etcd_registry import EtcdRegistry


class RandomNumberAdapter(Adapter):

    def __init__(self):
        self.random_agent = Agent(
            model=DeepSeek(api_key="sk-2d52100fe9b348afa71dc9d5b31db07f"),
            tools=[],
            instructions=[
                "Only can generator a random number"
            ],
            markdown=True,
        )

    def run(self, prompt: str) -> str:
        output_msg = self.random_agent.run(prompt)
        return output_msg.content

    def get_adapter_card(self) -> AdapterCard:
        return AdapterCard(
            name="Random Number Generator",
            bio="",
            lore="",
            knowledge="",
            routine="",
        )


def build_node():
    rn_team = RandomNumberAdapter()
    registry = EtcdRegistry(host="47.236.116.81", port=2379)
    # Create the server node.
    server_node = Node(node_id="RN", port=8080, Adapter=rn_team, registry=registry)
    client_node = Node(node_id="RNClient", port=8081, Adapter=rn_team, registry=registry)

    # Start the server in the foreground.
    server_node.build_server(daemon=False)
    client_node.build_server(daemon=True)
    time.sleep(5)
    print(client_node.send_message("RN", "random a number 0-10"))


build_node()
