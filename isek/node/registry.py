from abc import ABC, abstractmethod
from typing import Optional, Dict


class Registry(ABC):

    @abstractmethod
    def register_node(self, node_id: str, host: str, port: int, metadata: Optional[Dict[str, str]] = None):
        """注册节点到注册中心"""
        pass

    @abstractmethod
    def get_available_nodes(self) -> dict:
        """获取当前可用节点列表"""
        pass

    @abstractmethod
    def deregister_node(self, node_id: str):
        """从注册中心移除节点"""
        pass

    @abstractmethod
    def lease_refresh(self, node_id: str):
        pass
