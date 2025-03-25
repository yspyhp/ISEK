from isek.node.isek_center_registry import IsekCenterRegistry


node_a = IsekCenterRegistry()
node_a.register_node("node_a", "localhost", 8080, {"name": "a"})

node_b = IsekCenterRegistry()
node_b.register_node("node_b", "localhost", 8082, {"name": "b"})

print(node_b.get_available_nodes())
node_a.deregister_node("node_a")
print(node_b.get_available_nodes())
