import time
from isek.node.node_v2 import Node
from isek.util.logger import LoggerManager, PRINT_LOG_LEVEL

def main():
    """
    This script acts as a client to send a message to the server node.
    Run this script in a separate terminal after starting the server.
    """
    LoggerManager.init(level=PRINT_LOG_LEVEL)

    # Define the server's details so the client knows where to send the message.
    server_node_id = "server_node_1"
    server_host = "localhost"
    server_port = 9000

    # Create the client node. Its own ID and port are not critical for sending a single message.
    client_node = Node(node_id="client_node")
    
    # The client needs to know about the server. Since we are using DefaultRegistry,
    # discovery is not automatic. We manually add the server's information
    # to the client's local node cache.
    client_node.all_nodes[server_node_id] = {
        "host": server_host,
        "port": server_port,
        "metadata": {"url": f"http://{server_host}:{server_port}"}
    }
    
    print(f"Client node is ready. Sending a message to '{server_node_id}'...")

    # Send a message from the client to the server
    message_to_send = "Hello from the client!"
    response = client_node.send_message(server_node_id, message_to_send)

    print(f"\nSent message: '{message_to_send}'")
    print(f"Received response from server: {response}")

if __name__ == "__main__":
    main() 