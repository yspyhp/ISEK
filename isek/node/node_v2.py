import threading
import uuid
from abc import ABC
from typing import Dict, Any, Optional
from isek.constant.exceptions import NodeUnavailableError
from isek.node.default_registry import DefaultRegistry
from isek.node.registry import Registry
from isek.protocol.a2a_protocol import A2AProtocol
from isek.protocol.protocol import Protocol
from isek.team.team import Team
from isek.util.logger import logger

NodeDetails = Dict[str, Any]


class Node(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        node_id: Optional[str] = None,
        protocol: Optional[Protocol] = None,
        registry: Optional[Registry] = None,
        team: Optional[Team] = None,
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
        self.registry = registry or DefaultRegistry()
        self.team = team
        self.protocol = protocol or A2AProtocol(
            host=self.host, port=self.port, team=self.team
        )

    def send_message(self, receiver_node_id: str, message: str, retry_count: int = 3):
        current_retry = 0
        while current_retry < retry_count:
            try:
                receiver_node_details = self.all_nodes.get(receiver_node_id)
                if not receiver_node_details:
                    # Refresh nodes once if not found, in case cache is stale.
                    logger.warning(
                        f"Receiver node '{receiver_node_id}' not found in local cache. Refreshing node list once."
                    )
                    self.__refresh_nodes()
                    receiver_node_details = self.all_nodes.get(receiver_node_id)
                    if not receiver_node_details:
                        raise NodeUnavailableError(
                            receiver_node_id,
                            "Node not found in registry after refresh.",
                        )
                return self.protocol.send_message(
                    receiver_node_details["metadata"]["url"], message
                )
            except Exception as e:
                logger.exception(
                    f"Attempt {current_retry + 1}/{retry_count}: Unexpected error sending message to "
                    f"node '{receiver_node_id}'. Message: '{message}'. Error: {e}",
                    exc_info=True,
                )

            current_retry += 1

        logger.error(
            f"Failed to send message to node '{receiver_node_id}' after {retry_count} retries."
        )
        return f"Error: Message delivery to '{receiver_node_id}' failed after {retry_count} attempts."

    def build_server(self, daemon: bool = False) -> None:
        if self.registry and self.team:
            node_metadata = self.team.get_team_card().__dict__
            node_metadata["url"] = f"http://{self.host}:{self.port}"
            self.registry.register_node(
                node_id=self.node_id,
                host=self.host,
                port=self.port,
                metadata=node_metadata,
            )
            self.__bootstrap_heartbeat()  # Starts the recurring heartbeat

        if not daemon:
            self.protocol.bootstrap_server()
        else:
            server_thread = threading.Thread(
                target=self.protocol.bootstrap_server, daemon=True
            )
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
        except Exception as e:
            # This exception is from self.registry.get_available_nodes()
            logger.error(
                f"Failed to retrieve available nodes from registry: {e}", exc_info=True
            )
            # self.all_nodes might become stale if this fails repeatedly.

    def stop_server(self) -> None:
        self.protocol.stop_server()
