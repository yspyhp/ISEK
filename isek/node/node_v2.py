import threading

# import faiss # Commented out as per original
import uuid  # type: ignore # If grpc stubs are missing
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional  # Added Optional, List

# from isek.node.node_index import NodeIndex # Commented out
from isek.node.default_registry import DefaultRegistry
from isek.node.registry import Registry
from isek.squad.squad import Squad
from isek.util.logger import logger  # Assuming logger is configured

# import numpy as np # Commented out as per original

# Type alias for node information stored in self.all_nodes
NodeDetails = Dict[str, Any]  # e.g., {"host": str, "port": int, "metadata": dict}


class Node(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        node_id: Optional[str] = None,
        registry: Optional[Registry] = None,
        squad: Optional[Squad] = None,
        **kwargs: Any,  # To absorb any extra arguments
    ):
        if not host:
            raise ValueError("Node host cannot be empty.")
        if not isinstance(port, int) or not (0 < port < 65536):
            raise ValueError(f"Invalid port number for Node: {port}")
        if not node_id:
            node_id = uuid.uuid4().hex

        self.host: str = host
        self.port: int = port
        self.node_id: str = node_id
        self.all_nodes: Dict[str, NodeDetails] = {}
        self.p2p = False
        self.registry: Registry = (
            registry if registry is not None else DefaultRegistry()
        )
        self.squad = squad

    # def with_p2p(self):
    #     self.p2p = True
    #     return self

    def attach(self, squad):
        self.squad = squad
        return self

    @abstractmethod
    def bootstrap_server(self):
        pass

    def build_server(self, daemon: bool = False) -> None:
        if self.registry and self.squad:
            node_metadata = self.squad.get_squad_card()
            self.registry.register_node(
                node_id=self.node_id,
                host=self.host,
                port=self.port,
                metadata=node_metadata,
            )
            self.__bootstrap_heartbeat()  # Starts the recurring heartbeat

        if not daemon:
            self.bootstrap_server()
        else:
            server_thread = threading.Thread(target=self.bootstrap_server, daemon=True)
            server_thread.start()

    def __bootstrap_heartbeat(self) -> None:
        """
        Manages the node's heartbeat to the registry.

        This method performs two main actions:
        1. Refreshes the node's lease with the registry to keep it active.
        2. Refreshes the local cache of available nodes (`self.all_nodes`).

        It then schedules itself to run again after a fixed interval (5 seconds).
        """
        try:
            self.registry.lease_refresh(self.node_id)
            logger.debug(f"Node '{self.node_id}' lease refreshed successfully.")
        except Exception as e:
            logger.warning(
                f"Failed to refresh lease for node '{self.node_id}': {e}. "
                "Node might be deregistered if this persists.",
                exc_info=True,
            )
            # Depending on severity, could attempt re-registration or shutdown.

        try:
            self.__refresh_nodes()
        except Exception as e:
            logger.warning(
                f"Failed to refresh node list for '{self.node_id}': {e}", exc_info=True
            )

        # Schedule next heartbeat
        # Ensure timer is managed properly if the node is shut down
        timer = threading.Timer(5, self.__bootstrap_heartbeat)
        timer.daemon = True  # Allows main program to exit even if timer is active
        timer.start()
        logger.debug(f"Node '{self.node_id}' heartbeat scheduled.")

    def __refresh_nodes(self) -> None:
        """
        Refreshes the local cache of available nodes (`self.all_nodes`)
        by querying the service registry.

        The commented-out section suggests plans for integrating a vector-based
        node index (e.g., using Faiss) for more advanced node discovery.
        """
        try:
            current_available_nodes = self.registry.get_available_nodes()
            # Simple update: replace the old list.
            # More sophisticated updates might involve diffing for logging or specific actions.
            if self.all_nodes != current_available_nodes:  # Basic check for changes
                # logger.info(f"Node list updated for '{self.node_id}'. "
                #             f"Previous count: {len(self.all_nodes)}, New count: {len(current_available_nodes)}.")
                self.all_nodes = current_available_nodes
            else:
                logger.debug(
                    f"Node list for '{self.node_id}' remains unchanged. Count: {len(self.all_nodes)}."
                )

            # TODO: Implement node index building if self.embedding and NodeIndex are available.
            # The commented section for Faiss index:
            # if self.node_index and current_available_nodes: # Assuming self.node_index is an instance of NodeIndex
            #     try:
            #         # This implies NodeIndex.compare_and_build needs the full node info
            #         # and handles extraction of vectors and building the index.
            #         self.node_index.compare_and_build(current_available_nodes)
            #         logger.debug("Node index rebuild finished based on refreshed nodes.")
            #     except Exception as e_idx:
            #         logger.error(f"Error rebuilding node index: {e_idx}", exc_info=True)
        except Exception as e:
            # This exception is from self.registry.get_available_nodes()
            logger.error(
                f"Failed to retrieve available nodes from registry: {e}", exc_info=True
            )
            # self.all_nodes might become stale if this fails repeatedly.

    def stop_server(self) -> None:
        pass
