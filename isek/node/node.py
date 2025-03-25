import json
import threading
from abc import ABC, abstractmethod
from concurrent import futures
from typing import Dict

import faiss
import copy
import grpc
import numpy as np

from isek.constant.exceptions import NodeUnavailableError
from isek.node.noderpc import node_pb2, node_pb2_grpc
from isek.node.registry import Registry
from isek.util.logger import logger
from isek.node.node_index import NodeIndex
from isek.embedding.abstract_embedding import AbstractEmbedding
from isek.node.isek_center_registry import IsekCenterRegistry


class Node(node_pb2_grpc.IsekNodeServiceServicer, ABC):
    def __init__(self,
                 host: str = "localhost",
                 port: int = 8080,
                 registry: Registry = IsekCenterRegistry(),
                 embedding: AbstractEmbedding = None,
                 **kwargs
                 ):
        if not host or not port or not registry:
            raise ValueError("Node")
        self.node_id = self.build_node_id()
        self.host = host
        self.port = port
        self.registry = registry
        self.all_nodes = {}
        self.node_index = None
        if embedding:
            self.node_index = NodeIndex(embedding)
        self.node_list = None
        # self.__build_server()

    @abstractmethod
    def build_node_id(self) -> str:
        pass

    @abstractmethod
    def metadata(self) -> Dict:
        pass

    @abstractmethod
    def on_message(self, sender, message) -> str:
        pass

    def build_server(self):
        self.registry.register_node(node_id=self.node_id, host=self.host, port=self.port, metadata=self.metadata())
        self.__bootstrap_heartbeat()
        self.__bootstrap_grpc_server()

    def __bootstrap_heartbeat(self):
        self.registry.lease_refresh(self.node_id)
        self.__refresh_nodes()
        # logger.debug(f"{self.node_id} get all available nodes: {self.all_nodes}")
        timer = threading.Timer(5, self.__bootstrap_heartbeat)
        timer.daemon = True
        timer.start()

    def __refresh_nodes(self):
        all_nodes = self.registry.get_available_nodes()
        # todo self.node_index.compare_and_build(all_nodes)
        # is_nodes_changed = False
        # for node_id, node_info in all_nodes.items():
        #     if node_id not in self.all_nodes:
        #         is_nodes_changed = True
        #         break
        # if is_nodes_changed or len(all_nodes) != len(self.all_nodes):
        #     node_ids, vectors = zip(*[(node_id, n['metadata']['intro_vector']) for node_id, n in all_nodes.items()])
        #     vector_dim = len(vectors[0])
        #     vectors = np.array(vectors, dtype='float32')
        #     self.node_index = faiss.IndexFlatL2(vector_dim)
        #     self.node_index.add(vectors)
        #     self.node_list = node_ids
        #     logger.debug("Node index rebuild finished.")
        self.all_nodes = all_nodes

    def __bootstrap_grpc_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        node_pb2_grpc.add_IsekNodeServiceServicer_to_server(self, server)

        # 监听端口
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        logger.info(f"[{self.node_id}] Node started on port {self.port}...")
        server.wait_for_termination()
        # def wait_for_termination():
        #
        #
        # termination_thread = threading.Thread(target=wait_for_termination)
        # termination_thread.start()

    def send_message(self, receiver_node_id, message):
        """
        send message to another node by providing receiver_node_id= agent_name and message = message
        """
        logger.info(f"[{self.node_id}] send msg to [{receiver_node_id}]: {message}")
        receiver_node = self.all_nodes.get(receiver_node_id, None)
        if not receiver_node:
            raise NodeUnavailableError(receiver_node)
        # 连接到 gRPC 服务
        channel = grpc.insecure_channel(f"{receiver_node['host']}:{receiver_node['port']}")
        stub = node_pb2_grpc.IsekNodeServiceStub(channel)

        # 创建请求消息
        request = node_pb2.CallRequest(sender=self.node_id, receiver=receiver_node_id, message=message)

        # 调用远程服务方法
        response = stub.call(request)
        # log the response
        logger.info(f"[{self.node_id}] receive message from [{receiver_node_id}]: {response.reply}")
        return f"{response.reply}"

    def get_nodes_by_vector(self, query, limit=20):
        return self.all_nodes.values()
        # todo
        # if len(self.all_nodes) > limit and self.node_index is not None:
        #     node_ids = self.node_index.search(query, limit=limit)
        #     results = [self.all_nodes[node_id] for node_id in node_ids]
        # else:
        #     results = self.all_nodes.values()
        # return results

    def call(self, request, context):
        # 返回消息
        return node_pb2.CallResponse(reply=self.on_message(request.sender, request.message))
