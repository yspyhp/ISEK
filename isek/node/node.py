import threading
from abc import ABC, abstractmethod
from concurrent import futures
from typing import Dict, Any, Optional, List  # Added Optional, List

# import faiss # Commented out as per original
import grpc  # type: ignore # If grpc stubs are missing

# import numpy as np # Commented out as per original

from isek.constant.exceptions import NodeUnavailableError
from isek.node.noderpc import (
    node_pb2,
    node_pb2_grpc,
)  # Assuming these are generated gRPC files
from isek.node.registry import Registry
from isek.utils.logger import logger  # Assuming logger is configured

# from isek.node.node_index import NodeIndex # Commented out
from isek.embedding.abstract_embedding import AbstractEmbedding
from isek.node.isek_center_registry import IsekCenterRegistry

# Type alias for node information stored in self.all_nodes
NodeDetails = Dict[str, Any]  # e.g., {"host": str, "port": int, "metadata": dict}


class Node(node_pb2_grpc.IsekNodeServiceServicer, ABC):
    """
    Represents a node in a distributed system of agents.

    This class provides capabilities for network communication, interaction with a
    service registry (e.g., Isek Center or etcd), and handling messages from
    other nodes via gRPC. Each node has a unique ID, registers itself with the
    registry, and can send/receive messages to/from other registered nodes.
    It also maintains a local cache of available nodes and periodically refreshes
    its lease with the registry.

    Subclasses must implement `build_node_id`, `metadata`, and `on_message`.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        registry: Optional[Registry] = None,  # Allow None for default
        embedding: Optional[AbstractEmbedding] = None,
        **kwargs: Any,  # To absorb any extra arguments
    ):
        """
        Initializes a Node instance.

        :param host: The hostname or IP address that this node will advertise for
                     other nodes to connect to. Defaults to "localhost".
        :type host: str
        :param port: The port number on which this node's gRPC service will listen.
                     Defaults to 8080.
        :type port: int
        :param registry: An instance of a :class:`~isek.node.registry.Registry`
                         implementation (e.g., :class:`~isek.node.isek_center_registry.IsekCenterRegistry`
                         or :class:`~isek.node.etcd_registry.EtcdRegistry`).
                         If `None`, defaults to `IsekCenterRegistry()`.
        :type registry: typing.Optional[isek.node.registry.Registry]
        :param embedding: An optional embedding model instance for advanced node
                          discovery or indexing (currently partially implemented).
        :type embedding: typing.Optional[isek.embedding.abstract_embedding.AbstractEmbedding]
        :param kwargs: Additional keyword arguments (currently not used but allows for future expansion).
        :type kwargs: typing.Any
        :raises ValueError: If `host`, `port`, or `registry` are not validly provided (though
                            defaults make this less likely for `host` and `port` if `registry` is defaulted).
        """
        if not host:
            raise ValueError("Node host cannot be empty.")
        if not isinstance(port, int) or not (0 < port < 65536):
            raise ValueError(f"Invalid port number for Node: {port}")

        self.host: str = host
        self.port: int = port
        self.registry: Registry = (
            registry if registry is not None else IsekCenterRegistry()
        )
        # self.embedding is stored but not fully used yet based on commented code
        self.embedding: Optional[AbstractEmbedding] = embedding

        self.node_id: str = self.build_node_id()
        if not self.node_id:  # build_node_id should return a non-empty string
            raise ValueError("build_node_id() must return a non-empty node identifier.")

        self.all_nodes: Dict[str, NodeDetails] = {}  # Cache of discovered nodes
        self.grpc_server: Optional[grpc.Server] = (
            None  # To hold the gRPC server instance
        )

        # Node index related attributes (currently partially implemented based on comments)
        # self.node_index = None # Placeholder for a potential Faiss index or similar
        # if embedding:
        # self.node_index = NodeIndex(embedding) # Assuming NodeIndex class exists
        # self.node_list = None # Placeholder for an ordered list of node_ids if using an index

        logger.info(
            f"Node '{self.node_id}' initialized with host={host}, port={port}, "
            f"registry={type(self.registry).__name__}."
        )

    @abstractmethod
    def build_node_id(self) -> str:
        """
        Abstract method to generate a unique identifier for this node.

        This ID is used for registration with the registry and for addressing
        messages between nodes.

        :return: A unique string identifier for the node.
        :rtype: str
        """
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Abstract method to provide metadata about this node.

        This metadata is registered with the service registry and can be used by
        other nodes for discovery or decision-making (e.g., capabilities, persona info).

        :return: A dictionary containing metadata for this node.
        :rtype: typing.Dict[str, typing.Any]
        """
        pass

    @abstractmethod
    def on_message(self, sender: str, message: str) -> str:
        """
        Abstract method called when this node receives a message via gRPC.

        Subclasses must implement this to define how the node processes
        incoming messages.

        :param sender: The node ID of the message sender.
        :type sender: str
        :param message: The content of the message received.
        :type message: str
        :return: A string reply to be sent back to the sender.
        :rtype: str
        """
        pass

    def build_server(self) -> None:
        """
        Builds and starts the node's services.

        This involves:
        1. Registering the node with the configured service registry.
        2. Starting a periodic heartbeat to refresh the lease and update the local
           cache of available nodes.
        3. Starting the gRPC server to listen for incoming messages from other nodes.
        """
        try:
            node_metadata = self.metadata()
            self.registry.register_node(
                node_id=self.node_id,
                host=self.host,
                port=self.port,
                metadata=node_metadata,
            )
            logger.info(
                f"Node '{self.node_id}' successfully registered with the registry."
            )
        except Exception as e:
            logger.error(
                f"Failed to register node '{self.node_id}' with the registry: {e}",
                exc_info=True,
            )
            raise  # Re-raise as this is a critical step

        self.__bootstrap_heartbeat()  # Starts the recurring heartbeat
        self.__bootstrap_grpc_server()  # Starts the gRPC server (blocking if not in a thread)

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

    def __bootstrap_grpc_server(self) -> None:
        """
        Starts the gRPC server for this node.

        The server listens on the configured host and port for incoming messages
        from other nodes and uses a thread pool to handle requests.
        This method will block until the server is terminated if run in the main thread.
        """
        if self.grpc_server:
            logger.warning(
                f"gRPC server for node '{self.node_id}' is already running or was not shut down properly."
            )
            return

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        node_pb2_grpc.add_IsekNodeServiceServicer_to_server(
            self, server
        )  # 'self' implements the service methods

        listen_addr = f"[::]:{self.port}"  # Listen on all IPv6 interfaces, includes IPv4 on many systems
        try:
            server.add_insecure_port(listen_addr)
            server.start()
            self.grpc_server = server  # Store server instance for potential shutdown
            logger.info(
                f"Node '{self.node_id}' gRPC server started, listening on {listen_addr}."
            )
            # server.wait_for_termination() # This blocks. If build_server is called in main thread,
            # it will block here. Consider running this in a separate thread
            # or making build_server non-blocking if the node needs to do other things.
            # For non-blocking startup, remove wait_for_termination() here and handle shutdown elsewhere.
        except Exception as e:
            logger.error(
                f"Failed to start gRPC server for node '{self.node_id}' on {listen_addr}: {e}",
                exc_info=True,
            )
            self.grpc_server = None  # Ensure it's None if start failed
            raise

    def stop_server(self, grace_period_seconds: float = 1.0) -> None:
        """
        Stops the gRPC server and attempts to deregister the node.

        :param grace_period_seconds: The time (in seconds) to wait for ongoing RPCs
                                     to complete before forcefully terminating them.
        :type grace_period_seconds: float
        """
        logger.info(f"Attempting to stop node '{self.node_id}'...")
        # Stop gRPC server
        if self.grpc_server:
            logger.info(f"Stopping gRPC server for node '{self.node_id}'...")
            # The `stop` method returns a threading.Event that is set when shutdown is complete.
            # A grace period of None means immediate, hard shutdown.
            # A grace period allows ongoing RPCs to finish.
            shutdown_event = self.grpc_server.stop(grace_period_seconds)
            shutdown_event.wait()  # Wait for shutdown to complete
            self.grpc_server = None
            logger.info(f"gRPC server for node '{self.node_id}' stopped.")
        else:
            logger.info(
                f"No active gRPC server found for node '{self.node_id}' to stop."
            )

        # Deregister from registry
        try:
            logger.info(f"Deregistering node '{self.node_id}' from registry...")
            self.registry.deregister_node(self.node_id)
            logger.info(f"Node '{self.node_id}' deregistered successfully.")
        except Exception as e:
            logger.error(
                f"Failed to deregister node '{self.node_id}': {e}", exc_info=True
            )
            # Continue shutdown even if deregistration fails.

        # Note: Heartbeat timer is a daemon thread, so it should not prevent exit.
        # If it weren't a daemon, you'd need to cancel it here.
        logger.info(f"Node '{self.node_id}' shutdown process completed.")

    def send_message(
        self, receiver_node_id: str, message: str, retry_count: int = 3
    ) -> str:
        """
        Sends a message to another node identified by `receiver_node_id`.

        Implements a retry mechanism for transient failures.

        :param receiver_node_id: The ID of the target node (e.g., an agent's name).
        :type receiver_node_id: str
        :param message: The message content to send.
        :type message: str
        :param retry_count: The number of times to retry sending the message if an error occurs.
                            Defaults to 3.
        :type retry_count: int
        :return: The reply from the receiver node, or an error message if sending fails after all retries.
        :rtype: str
        """
        current_retry = 0
        while current_retry < retry_count:
            try:
                return self.__send_message_impl(receiver_node_id, message)
            except NodeUnavailableError as nue:  # Specific error for node not found
                logger.warning(
                    f"Attempt {current_retry + 1}/{retry_count}: Node '{receiver_node_id}' is unavailable. Error: {nue}"
                )
                # No point retrying immediately if node is simply not in all_nodes,
                # unless all_nodes is expected to update quickly.
                # Refreshing nodes here might be too aggressive.
                if current_retry == retry_count - 1:
                    return f"Error: Node '{receiver_node_id}' is currently unavailable."
                # Consider a short delay before retry if it's a transient issue
                # time.sleep(1)
            except (
                grpc.RpcError
            ) as rpc_e:  # Catch gRPC specific errors (network, server-side issues)
                logger.warning(
                    f"Attempt {current_retry + 1}/{retry_count}: gRPC error sending message to "
                    f"node '{receiver_node_id}'. Error: {rpc_e.details() if hasattr(rpc_e, 'details') else rpc_e}",
                    exc_info=True,
                )
                # Could check rpc_e.code() for specific handling (e.g., grpc.StatusCode.UNAVAILABLE)
            except Exception as e:  # Catch other unexpected errors
                logger.error(
                    f"Attempt {current_retry + 1}/{retry_count}: Unexpected error sending message to "
                    f"node '{receiver_node_id}'. Message: '{message}'. Error: {e}",
                    exc_info=True,
                )

            current_retry += 1
            if current_retry < retry_count:
                logger.info(f"Retrying message to '{receiver_node_id}'...")
                # Optional: implement a backoff strategy for retries
                # time.sleep(current_retry) # Simple linear backoff

        logger.error(
            f"Failed to send message to node '{receiver_node_id}' after {retry_count} retries."
        )
        return f"Error: Message delivery to '{receiver_node_id}' failed after {retry_count} attempts."

    def __send_message_impl(self, receiver_node_id: str, message: str) -> str:
        """
        Internal implementation for sending a message to a single node.

        :param receiver_node_id: The ID of the target node.
        :type receiver_node_id: str
        :param message: The message content.
        :type message: str
        :return: The reply from the receiver.
        :rtype: str
        :raises NodeUnavailableError: If the `receiver_node_id` is not found in the local cache (`self.all_nodes`).
        :raises grpc.RpcError: If a gRPC communication error occurs.
        """
        logger.info(
            f"Node '{self.node_id}' attempting to send message to '{receiver_node_id}': '{message[:50]}...'"
        )

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
                    receiver_node_id, "Node not found in registry after refresh."
                )

        target_address = (
            f"{receiver_node_details['host']}:{receiver_node_details['port']}"
        )
        # Consider using grpc.secure_channel if security is needed.
        # Channel and stub creation could be cached for frequently contacted nodes.
        try:
            with grpc.insecure_channel(
                target_address
            ) as channel:  # `with` ensures channel is closed
                stub = node_pb2_grpc.IsekNodeServiceStub(channel)
                grpc_request = node_pb2.CallRequest(
                    sender=self.node_id, receiver=receiver_node_id, message=message
                )

                # Add a timeout to the gRPC call
                timeout_seconds = 10.0
                grpc_response = stub.call(grpc_request, timeout=timeout_seconds)

                logger.info(
                    f"Node '{self.node_id}' received reply from '{receiver_node_id}': '{grpc_response.reply[:50]}...'"
                )
                return grpc_response.reply  # Assuming reply is always a string
        except grpc.RpcError as e:
            logger.error(
                f"gRPC call to node '{receiver_node_id}' at {target_address} failed: {e.code()} - {e.details()}",
                exc_info=True,
            )
            raise  # Re-raise the RpcError to be handled by the retry logic in send_message

    def get_nodes_by_vector(
        self, query_vector: List[float], limit: int = 20
    ) -> List[NodeDetails]:
        """
        Retrieves a list of nodes based on a query vector, potentially using a vector index.

        Currently, if no vector index (`self.node_index`) is available or the number of
        nodes is small, it returns all known nodes up to the limit.
        The actual vector search logic (commented out) would require `self.node_index`
        to be properly initialized and populated with node embeddings.

        :param query_vector: A list of floats representing the query embedding.
        :type query_vector: typing.List[float]
        :param limit: The maximum number of nodes to return. Defaults to 20.
        :type limit: int
        :return: A list of node detail dictionaries.
        :rtype: typing.List[NodeDetails]
        """
        # TODO: Implement actual vector search using self.node_index (e.g., Faiss)
        # The current implementation is a placeholder.
        logger.debug(
            f"get_nodes_by_vector called. Query (vector type): {type(query_vector)}, Limit: {limit}"
        )

        # Placeholder logic:
        if not self.all_nodes:
            return []

        # The commented Faiss logic:
        # if self.node_index is not None and len(self.all_nodes) > limit: # Assuming node_index is a Faiss index
        #     try:
        #         # query_vector needs to be a NumPy array for Faiss
        #         query_np = np.array([query_vector], dtype='float32') # Faiss expects a 2D array of queries
        #         distances, indices = self.node_index.search(query_np, k=limit)
        #
        #         # self.node_list should be an ordered list of node_ids corresponding to the Faiss index
        #         if self.node_list:
        #             # indices[0] because search was for a single query vector
        #             found_node_ids = [self.node_list[i] for i in indices[0] if i != -1] # -1 indicates no more results
        #             results = [self.all_nodes[node_id] for node_id in found_node_ids if node_id in self.all_nodes]
        #             logger.debug(f"Vector search found {len(results)} nodes.")
        #             return results
        #         else:
        #             logger.warning("Node index exists but node_list is not populated. Cannot map Faiss indices to node IDs.")
        #             # Fallback to returning all nodes if mapping fails
        #     except Exception as e_idx:
        #         logger.error(f"Error during vector search: {e_idx}", exc_info=True)
        #         # Fallback on error

        # Fallback: return all nodes (or a subset if limit is smaller)
        # This is not a vector search, just a simple truncation.
        all_node_values = list(self.all_nodes.values())
        return all_node_values[:limit]

    # --- gRPC Service Implementation ---
    def call(
        self, request: node_pb2.CallRequest, context: grpc.ServicerContext
    ) -> node_pb2.CallResponse:
        """
        gRPC service method implementation for handling incoming calls from other nodes.

        This method is invoked by the gRPC framework when another node sends a message
        to this node's `IsekNodeService.call` RPC endpoint. It delegates processing
        to the `self.on_message` abstract method.

        :param request: The incoming `node_pb2.CallRequest` object containing
                        sender ID, receiver ID (this node's ID), and message content.
        :type request: node_pb2.CallRequest
        :param context: The gRPC `ServicerContext` providing call-specific information
                        and an interface to manipulate RPC-level states.
        :type context: grpc.ServicerContext
        :return: A `node_pb2.CallResponse` object containing the reply.
        :rtype: node_pb2.CallResponse
        """
        try:
            client_ip = (
                context.peer().split(":")[1] if context.peer() else "unknown"
            )  # Basic client IP
            logger.info(
                f"Node '{self.node_id}' received gRPC call from sender '{request.sender}' (IP: {client_ip}). "
                f"Message: '{request.message[:50]}...'"
            )

            # Delegate to the user-defined message handler
            reply_content = self.on_message(
                sender=request.sender, message=request.message
            )

            logger.info(
                f"Node '{self.node_id}' sending reply to '{request.sender}': '{reply_content[:50]}...'"
            )
            return node_pb2.CallResponse(reply=reply_content)
        except Exception as e:
            logger.error(
                f"Error processing gRPC call in on_message for node '{self.node_id}' "
                f"from sender '{request.sender}': {e}",
                exc_info=True,
            )
            # Send an error back to the client
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error processing message: {e}")
            # Return an empty or error-indicating response
            return node_pb2.CallResponse(reply=f"Error processing your request: {e}")
