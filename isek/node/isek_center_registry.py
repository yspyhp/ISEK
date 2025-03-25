import json
from typing import Optional, Dict

import requests

from isek.util.logger import logger
from isek.node.registry import Registry


class IsekCenterRegistry(Registry):
    def __init__(self,
                 host: Optional[str] = "localhost",
                 port: Optional[int] = 8088,
                 ):
        self.center_address = f"http://{host}:{port}"
        self.node_info = {}

    def register_node(self, node_id: str, host: str, port: int, metadata: Optional[Dict[str, str]] = None):
        """注册节点到注册中心，使用租约保证节点自动过期"""

        register_url = f"{self.center_address}/isek_center/register"
        self.node_info = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "metadata": metadata or {}
        }

        response = requests.post(url=register_url, json=self.node_info)
        response_json = json.loads(response.content)
        if response_json['code'] != 200:
            raise RuntimeError(f'Register isek center error {response_json}')
        logger.debug(f"Node {node_id} registered, response info: {response.content}")

    def lease_refresh(self, node_id: str):
        lease_refresh_url = f"{self.center_address}/isek_center/renew"
        node_info = {
            "node_id": node_id,
        }

        response = requests.post(url=lease_refresh_url, json=node_info)
        response_json = json.loads(response.content)
        if response_json['code'] != 200:
            raise RuntimeError(f'deregister from isek center error {response_json}')
        # logger.debug(f"Node {node_id} lease refresh.")


    def get_available_nodes(self) -> Dict[str, dict]:
        """获取当前可用节点列表"""
        register_url = f"{self.center_address}/isek_center/available_nodes"
        response = requests.get(url=register_url)
        response_json = json.loads(response.content)
        if response_json['code'] != 200:
            raise RuntimeError(f'Get available nodes from isek center error {response_json}')
        return response_json['data']['available_nodes']

    def deregister_node(self, node_id: str):
        """从注册中心移除节点并撤销租约"""
        register_url = f"{self.center_address}/isek_center/deregister"
        node_info = {
            "node_id": node_id,
        }

        response = requests.post(url=register_url, json=node_info)
        response_json = json.loads(response.content)
        if response_json['code'] != 200:
            raise RuntimeError(f'deregister from isek center error {response_json}')
        logger.info(f"Node {node_id} deregistered.")
