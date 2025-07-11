from isek.utils.log import log
from isek.node.node_v2 import Node
from isek.utils.print_utils import print_send_message_result, print_panel

def main():
    """
    This script acts as a client to interact with the agent hosted on the server node.
    Run this script in a separate terminal after starting the lv9 server.
    """
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # Server details must match the running server script
    server_node_id = "agent_server_1"
    server_host = "localhost"
    server_port = 9005

    # Create a client node to send messages
    client_node = Node(node_id="lv9_client")
    
    # Manually add the server's info to the client's local cache
    client_node.all_nodes[server_node_id] = {
        "host": server_host,
        "port": server_port,
        "metadata": {"url": f"http://{server_host}:{server_port}"}
    }
    
    print_panel(title="LV9 Agent Client",
                content="This client will test the agent's memory and tool use.",
                color="bright_yellow")

    # --- Test 1: Memory ---
    print_panel(title="Test 1", content="Storing a fact in the agent's memory...", color="yellow")
    print_send_message_result(
        lambda msg: client_node.send_message(server_node_id, msg),
        source_node_id=client_node.node_id,
        target_node_id=server_node_id,
        message="Hi there, please remember that my favorite color is blue."
    )

    # --- Test 2: Retrieval and Tool Use ---
    print_panel(title="Test 2", content="Asking a question that requires both memory and a tool...", color="yellow")
    print_send_message_result(
        lambda msg: client_node.send_message(server_node_id, msg),
        source_node_id=client_node.node_id,
        target_node_id=server_node_id,
        message="What is 15 plus 8? And what is my favorite color?"
    )

    print_panel(title="Test Complete", color="bright_yellow")


if __name__ == "__main__":
    main() 