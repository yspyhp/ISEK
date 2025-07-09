import time
from isek.node.node_v2 import Node
from isek.utils.log import log
from isek.adapter.simple_adapter import SimpleAdapter
from isek.utils.print_utils import print_send_message_result
from isek.utils.log import LoggerManager

# LoggerManager.debug_mode()
LoggerManager.plain_mode()


def main():
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # Create teams for the nodes
    team1 = SimpleAdapter(name="Node1Team", description="Team for Node1 communication")
    team2 = SimpleAdapter(name="Node2Team", description="Team for Node2 communication")
    
    # Create two nodes with different ports and IDs, using the default registry (local, no real discovery)
    node1 = Node(node_id="Node1", port=9000, adapter=team1)
    node2 = Node(node_id="Node2", port=9001, adapter=team2)

    # Start both node servers in daemon mode (background threads)
    node1.build_server(daemon=True)
    node2.build_server(daemon=True)
    log.info("Node servers started in background.")

    # Give some time for servers to start and register
    time.sleep(2)

    # Manually add node2 to node1's local cache for demo purposes (since DefaultRegistry does not do real discovery)
    node1.all_nodes[node2.node_id] = {
        "host": node2.host,
        "port": node2.port,
        "metadata": {"url": f"http://{node2.host}:{node2.port}"}
    }

    # Send a message from node1 to node2 with nice formatting
    print_send_message_result(
        lambda msg: node1.send_message(node2.node_id, msg),
        source_node_id=node1.node_id,
        target_node_id=node2.node_id,
        message="Hello, I am Node1!"
    )

    # Keep the script alive for a short while to allow background threads to run
    time.sleep(2)

if __name__ == "__main__":
    main() 