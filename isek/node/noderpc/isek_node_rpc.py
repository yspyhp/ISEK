from isek.node.noderpc import node_pb2, node_pb2_grpc


class IsekNodeServiceServicer(node_pb2_grpc.IsekNodeServiceServicer):

    def __init__(self, isek_node):
        self.isek_node = isek_node

    def send_message(self, request, context):
        # 返回消息
        return node_pb2.CallResponse(reply=f"Hello, {request.message}, I am {self.isek_node.node_id}!")
