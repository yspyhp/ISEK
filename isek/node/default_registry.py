from abc import ABC
from typing import Optional, Dict
from isek.util.logger import logger


class DefaultRegistry(ABC):
    def register_node(
        self,
        node_id: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, str]] = None,
    ):
        logger.info(f"Node {node_id} registered.")

    def get_available_nodes(self) -> dict:
        return {}

    def deregister_node(self, node_id: str):
        logger.info(f"Node {node_id} deregistered.")

    def lease_refresh(self, node_id: str):
        logger.info(f"Node {node_id} lease refresh.")
