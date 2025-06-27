from isek.node.etcd_registry import EtcdRegistry
from isek.node.node_v2 import Node

# Create the server node.
etcd_registry = EtcdRegistry(host="47.236.116.81", port=2379)
server_node = Node(node_id="RN_client", port=8889, p2p=True, p2p_server_port=9001, registry=etcd_registry)

# Start the server in the foreground.
server_node.build_server(daemon=True)
# time.sleep(5)
reply = server_node.send_message("RN", "random a number 0-10")
print(f"RN say:\n{reply}")
