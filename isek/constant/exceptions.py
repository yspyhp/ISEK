
class NodeUnavailableError(Exception):
    def __init__(self, node_name, message="Node is unavailable"):
        self.node_name = node_name
        self.message = f"Node '{node_name}' is unavailable: {message}"
        super().__init__(self.message)

