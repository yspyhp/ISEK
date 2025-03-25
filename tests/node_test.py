from isek.node.etcd_registry import EtcdRegistry
from isek.node.node import Node


class DefaultNode(Node):

    def metadata(self):
        return {}

    def on_message(self, sender, message):
        return f"{self.node_id}"


registry = EtcdRegistry(host="47.236.116.81", port=2379)
node_a = DefaultNode(host="localhost", port=8080, registry=registry)
node_b = DefaultNode(host="localhost", port=8081, registry=registry)

# time.sleep(2)
# node_a.registry.get_available_nodes()


