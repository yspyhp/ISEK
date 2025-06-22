import asyncio
from isek.node.node_v2 import Node
from isek.util.logger import LoggerManager, PRINT_LOG_LEVEL
from isek.team.isek_team import IsekTeam
from isek.agent.isek.agent import Agent
from isek.models.simpleModel import SimpleModel

def main():
    """
    This script starts a single node server that hosts a simple team
    and listens for messages.
    Run this script in one terminal.
    """
    LoggerManager.init(level=PRINT_LOG_LEVEL)

    # Define a stable node_id and port for the server
    server_node_id = "server_node_1"
    server_port = 9000

    print(f"Starting server node '{server_node_id}' on port {server_port}...")
    
    # A node must host a team to be able to respond to messages.
    # We'll create a simple team with one agent that just echoes prompts.
    echo_agent = Agent(
        name="Echo Agent",
        model=SimpleModel(),
        description="An agent that echoes back whatever it receives."
    )
    
    echo_team = IsekTeam(
        name="Echo Team",
        members=[echo_agent]
    )

    # Create the server node.
    server_node = Node(node_id=server_node_id, port=server_port, team=echo_team)

    # Start the server in the foreground.
    server_node.build_server(daemon=False)

if __name__ == "__main__":
    main() 