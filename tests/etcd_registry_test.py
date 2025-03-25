import ecdsa
from isek.node.etcd_registry import EtcdRegistry


node_a = EtcdRegistry(host="47.236.116.81", port=2379)
node_a.register_node("node_a", "localhost", 8080, {"name": "a"})

node_b = EtcdRegistry(host="47.236.116.81", port=2379)
node_b.register_node("node_b", "localhost", 8082, {"name": "b"})

node_c = EtcdRegistry(host="47.236.116.81", port=2379, parent_node_id="abc")
node_c.register_node("node_c", "localhost", 8082, {"name": "c"})

print(node_b.get_available_nodes())
try:
    node_b.deregister_node("node_a")
except ValueError as e:
    print(f"node_b can not deregister node_a: {e}")
print(node_b.get_available_nodes())
node_a.deregister_node("node_a")
print("node_a deregister node_a")
print(node_b.get_available_nodes())
print(node_c.get_available_nodes())


# public_registry = EtcdRegistry(host="47.236.116.81", port=2379)
# public_registry.register_node("node_1", "localhost", 8080, {"name": "a"})
# public_registry.register_node("node_2", "localhost", 8082, {"name": "b"})
#
# print(public_registry.get_available_nodes())
# public_registry.deregister_node("node_1")
# print(public_registry.get_available_nodes())
