from isek.node.node_v2 import Node
from isek.util.logger import LoggerManager, PRINT_LOG_LEVEL

def main():
    """
    This script starts a single node server that listens for messages.
    Run this script in one terminal.
    """
    LoggerManager.init(level=PRINT_LOG_LEVEL)

    # Define a stable node_id and port for the server
    server_node_id = "server_node_1"
    server_port = 9000

    print(f"Starting server node '{server_node_id}' on port {server_port}...")
    
    # Create the server node. It uses DefaultRegistry by default.
    server_node = Node(node_id=server_node_id, port=server_port)

    # Start the server in the foreground. This will block and listen for incoming messages.
    # To stop the server, you'll need to interrupt the script (e.g., Ctrl+C).
    server_node.build_server(daemon=False)

if __name__ == "__main__":
    main() 