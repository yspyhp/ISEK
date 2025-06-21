import os
from dotenv import load_dotenv

from isek.agent.isek.agent import Agent
from isek.models.openai import OpenAIModel
from isek.tools.calculator import calculator_tools
from isek.memory.memory import Memory as SimpleMemory
from isek.node.node_v2 import Node
from isek.squad.squad import Squad, SquadCard
from isek.util.logger import LoggerManager, PRINT_LOG_LEVEL

# Load environment variables from .env file
load_dotenv()

# A custom Squad to wrap an ISEK Agent, allowing it to be hosted on a Node.
class AgentSquad(Squad):
    """
    This Squad implementation wraps a complete Agent.
    When the node receives a message, it passes the prompt to this squad's 'run' method,
    which in turn executes the agent's logic.
    """
    def __init__(self, agent: Agent):
        self.agent = agent

    def run(self, prompt: str) -> str:
        """
        Execute the agent with the given prompt.
        """
        print(f"AgentSquad received prompt: '{prompt}'")
        response = self.agent.run(prompt)
        print(f"Agent produced response: '{response}'")
        return response

    def get_squad_card(self) -> SquadCard:
        """
        Provide metadata about the agent for discovery purposes.
        """
        routine_str = ""
        if isinstance(self.agent.instructions, list):
            routine_str = "\n".join(self.agent.instructions)
        elif isinstance(self.agent.instructions, str):
            routine_str = self.agent.instructions

        return SquadCard(
            name=self.agent.name or "Unnamed Agent",
            bio=self.agent.description or "No description",
            lore="This agent is hosted on an ISEK node.",
            knowledge="Can use a calculator and remembers previous interactions in the same session.",
            routine=routine_str,
        )

def main():
    """
    This script starts a node server that hosts a memory-and-tool-enabled agent.
    Run this script in one terminal.
    """
    LoggerManager.init(level=PRINT_LOG_LEVEL)

    # 1. Create the Agent
    # This agent has both memory (to remember facts) and tools (a calculator).
    print("Initializing the memory-tool agent...")
    memory_tool_agent = Agent(
        name="LV9-Agent",
        model=OpenAIModel(
            model_id=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        ),
        tools=[calculator_tools],
        memory=SimpleMemory(),
        description="A helpful assistant with memory and calculator abilities, hosted on a node.",
        instructions=["Be polite", "Answer questions based on memory", "Use tools for math"],
        success_criteria="User gets a helpful, context-aware response.",
        debug_mode=True
    )
    print("Agent initialized.")

    # 2. Wrap the Agent in our custom Squad
    agent_squad = AgentSquad(agent=memory_tool_agent)

    # 3. Start the Node Server with the Agent Squad
    server_node_id = "agent_server_1"
    server_port = 9005
    print(f"Starting server node '{server_node_id}' on port {server_port} to host the agent...")
    
    server_node = Node(
        node_id=server_node_id,
        port=server_port,
        squad=agent_squad
    )

    # Start the server in the foreground. It will now listen for messages.
    server_node.build_server(daemon=False)

if __name__ == "__main__":
    main() 