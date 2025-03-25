import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../isek")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples")))

from agent.distributed_agent import DistributedAgent
from node.etcd_registry import EtcdRegistry
from node.isek_center_registry import IsekCenterRegistry
from agent.persona import Persona

os.environ['OPENAI_API_KEY'] = ""


def main():
    registry = EtcdRegistry(host="47.236.116.81", port=2379)
    # registry = IsekCenterRegistry()

    Mani_info = {
        "name": "Mani",
        "bio": "An experienced manager",
        "lore": "Your mission is to manage the team",
        "knowledge": "recruit, assign tasks, manage tasks, manage projects"
    }

    Doki_info = {
        "name": "Doki",
        "bio": "An experienced doctor",
        "lore": "Your mission is to treat patients",
        "knowledge": "diagnose, treat, prescribe, surgery"
    }
    Brook_info = {
        "name": "Brook",
        "bio": "An experienced bookkeeper",
        "lore": "Your mission is to manage the accounts of the company",
        "knowledge": "bookkeeping, accounting, finance, tax"
    }

    Mani = Persona.from_json(Mani_info)
    Doki = Persona.from_json(Doki_info)
    Brook = Persona.from_json(Brook_info)

    Mani_agent = DistributedAgent(persona=Mani, host="localhost", port=8080, registry=registry)
    Mani_agent.tool_manager.register_tools([
        Mani_agent.search_partners,
        Mani_agent.send_message,
        Mani_agent.decompose_task,
    ])

    Doki_agent = DistributedAgent(persona=Doki, host="localhost", port=8081, registry=registry)
    Brook_agent = DistributedAgent(persona=Brook, host="localhost", port=8082, registry=registry)

    # dobby = Persona.load("examples/dobby.character.json")
    # dobby_agent = DistributedAgent(persona=dobby, host="localhost", port=8081, registry=registry)
    time.sleep(5)

    print(Mani_agent.search_partners("An experienced doctor"))
    print(Mani_agent.search_partners("An experienced bookkeeper"))
    print(Mani_agent.search_partners("I'm sick."))


main()