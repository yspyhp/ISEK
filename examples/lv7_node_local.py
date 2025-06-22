import time
from isek.node.node_v2 import Node
from isek.utils.logger import LoggerManager, PRINT_LOG_LEVEL
from isek.team.simple_team import SimpleTeam

# Initialize logger for debug output
LoggerManager.init(level=PRINT_LOG_LEVEL)

def main():
    # Create teams for the nodes
    team1 = SimpleTeam(name="Node1Team", description="Team for Node1 communication")
    team2 = SimpleTeam(name="Node2Team", description="Team for Node2 communication")
    
    # Create two nodes with different ports and IDs, using the default registry (local, no real discovery)
    node1 = Node(node_id="Node1", port=9000, team=team1)
    node2 = Node(node_id="Node2", port=9001, team=team2)

    # Start both node servers in daemon mode (background threads)
    node1.build_server(daemon=True)
    node2.build_server(daemon=True)

    # Give some time for servers to start and register
    time.sleep(2)

    # Manually add node2 to node1's local cache for demo purposes (since DefaultRegistry does not do real discovery)
    node1.all_nodes[node2.node_id] = {
        "host": node2.host,
        "port": node2.port,
        "metadata": {"url": f"http://{node2.host}:{node2.port}"}
    }

    # Send a message from node1 to node2
    result = node1.send_message(node2.node_id, "Hello, I am Node1!")
    print(f"Node1 sent message to Node2, got reply: {result}")

    # Keep the script alive for a short while to allow background threads to run
    time.sleep(2)

if __name__ == "__main__":
    main() 