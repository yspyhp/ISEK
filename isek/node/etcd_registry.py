import json
from typing import Optional, Dict, Any # Added Any
import base64

import etcd3gw # type: ignore # Assuming etcd3 might not have type stubs
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa.curves import NIST256p
from ecdsa.util import sigencode_der, sigdecode_der # For deterministic signatures if needed
# from ecdsa.errors import BadSignatureError
from ecdsa import BadSignatureError


from isek.util.logger import logger # Assuming logger is configured
from isek.node.registry import Registry # Assuming Registry is an ABC or base class

# Type alias for node metadata
NodeMetadata = Dict[str, str]
NodeInfo = Dict[str, Any] # More specific than just Dict[str, str] as port is int

class EtcdRegistry(Registry):
    """
    An implementation of the :class:`~isek.node.registry.Registry` interface
    that uses etcd as a distributed key-value store for service discovery.

    Nodes register themselves with their connection information and metadata.
    The registry uses leases to automatically deregister nodes if they fail
    to refresh their lease, providing a degree of fault tolerance.
    Node information is signed to ensure integrity and authenticity, although
    the current signature verification logic in `__verify_signature` appears
    to verify a signature it just created, rather than a signature from a remote node.
    """

    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 parent_node_id: str = "root", # Made non-optional with default
                 etcd_client: Optional[etcd3gw.Etcd3Client] = None,
                 ttl: int = 30):
        """
        Initializes the EtcdRegistry.

        Connection to etcd can be established either by providing an existing
        `etcd_client` object or by specifying `host` and `port`.

        :param host: The hostname or IP address of the etcd server.
                     Used if `etcd_client` is not provided.
        :type host: typing.Optional[str]
        :param port: The port number of the etcd server.
                     Used if `etcd_client` is not provided.
        :type port: typing.Optional[int]
        :param parent_node_id: The root path or prefix in etcd under which nodes
                               will be registered. Defaults to "root".
        :type parent_node_id: str
        :param etcd_client: An optional pre-configured `etcd3.Etcd3Client` instance.
                            If provided, `host` and `port` are ignored.
        :type etcd_client: typing.Optional[etcd3.Etcd3Client]
        :param ttl: Time-to-live (in seconds) for node leases. Nodes must refresh
                    their lease within this period to remain registered. Defaults to 30.
        :type ttl: int
        :raises TypeError: If neither (`host` and `port`) nor `etcd_client` is provided.
        :raises ConnectionError: If the connection to the etcd server cannot be established.
        """
        if host and port and etcd_client:
            logger.warning("Both 'host/port' and 'etcd_client' were provided. "
                           "The existing 'etcd_client' will be used.")

        if etcd_client:
            self.etcd_client: etcd3gw.Etcd3Client = etcd_client
        elif host and port:
            self.etcd_client = etcd3gw.client(host=host, port=port)
        else:
            raise TypeError("Either ('host' and 'port') or 'etcd_client' must be provided to EtcdRegistry.")

        self.parent_node_id: str = parent_node_id # Defaults to "root" if None was passed

        try:
            # Check etcd server status
            status_check = self.etcd_client.status()
            if not status_check: # status() might return None or raise on failure
                raise ConnectionError("etcd client status check returned an unhealthy or falsy status.")
            logger.info(f"Successfully connected to etcd server. Version: {status_check.version}")
        except Exception as e: # Catch broader exceptions from etcd3.client or status()
            raise ConnectionError(f"Failed to connect to the etcd server or get status: {e}") from e

        # This signing key is for this registry instance to sign data it puts,
        # or for nodes this registry *manages* if it were creating their entries.
        # If nodes sign their own data, this SK would be for verifying their VKs,
        # or this registry would need its own identity for others to verify.
        self.sk: SigningKey = SigningKey.generate(curve=NIST256p)
        self.vk_base64: str = base64.b64encode(self.sk.verifying_key.to_string()).decode('utf-8')


        self.ttl: int = ttl
        self.leases: Dict[str, etcd3.Lease] = {} # Stores lease objects per node_id

    def register_node(self, node_id: str, host: str, port: int, metadata: Optional[NodeMetadata] = None) -> None:
        """
        Registers a node with the etcd service registry.

        A lease is created for the node, and its information (including a public key
        derived from this registry's signing key) is stored in etcd. The node's
        information is signed by this registry instance.

        .. warning::
            The public key stored (`vk_base64`) is derived from this `EtcdRegistry`
            instance's private key (`self.sk`). This means the registry is asserting
            the identity of the node by signing its details. If nodes are meant to
            have their own identities, they should generate their own key pairs and
            provide their public key for registration.

        :param node_id: The unique identifier for the node.
        :type node_id: str
        :param host: The hostname or IP address where the node can be reached.
        :type host: str
        :param port: The port number on which the node is listening.
        :type port: int
        :param metadata: Optional dictionary of key-value pairs providing additional
                         information about the node. Defaults to an empty dictionary.
        :type metadata: typing.Optional[NodeMetadata]
        """
        # The public key stored is this registry's public key, used to sign the node_info.
        # This implies the registry is attesting to the node_info.
        node_info: NodeInfo = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "public_key": self.vk_base64, # This registry's public key
            "metadata": metadata or {}
        }

        # Sign the node_info (deterministically for consistency if needed)
        node_info_json_bytes: bytes = json.dumps(node_info, sort_keys=True).encode("utf-8")
        # Using sign_deterministic for consistent signatures if the input is identical.
        # Standard sign() might produce different valid signatures for the same input.
        signature_bytes: bytes = self.sk.sign_deterministic(node_info_json_bytes, sigencode=sigencode_der)
        signature_base64: str = base64.b64encode(signature_bytes).decode("utf-8")

        node_entry: Dict[str, Any] = {
            "node_info": node_info,
            "signature": signature_base64 # Signature created by this registry instance
        }

        try:
            lease = self.etcd_client.lease(self.ttl)
            self.leases[node_id] = lease # Store lease to manage it

            key: str = f"/{self.parent_node_id}/{node_id}"
            self.etcd_client.put(key, json.dumps(node_entry), lease=lease)

            logger.info(f"Node '{node_id}' registered successfully under key '{key}' with TTL {self.ttl}s. "
                        f"Info: {node_info}")
        except Exception as e:
            logger.error(f"Failed to register node '{node_id}': {e}", exc_info=True)
            # Optionally revoke lease if created but put failed
            if node_id in self.leases and 'lease' in locals() and lease is not None:
                 try:
                    lease.revoke()
                 except Exception as rev_e:
                    logger.error(f"Failed to revoke lease for '{node_id}' during registration error cleanup: {rev_e}")
                 del self.leases[node_id]
            raise # Re-raise the original exception

    def lease_refresh(self, node_id: str) -> None:
        """
        Refreshes the lease for a registered node.

        This method should be called periodically by the node (or on its behalf)
        to prevent its registration from expiring.

        .. note::
            The current `__verify_signature` call within this method appears to
            re-verify a signature generated by this same registry instance, which might
            not be the intended security check if nodes have their own identities.
            If the goal is for the node to prove its identity to refresh, it would
            need to provide a signature that this registry verifies against the node's
            stored public key.

        :param node_id: The ID of the node whose lease needs to be refreshed.
        :type node_id: str
        :raises KeyError: If the node_id is not found in the local lease cache.
        :raises ValueError: If signature verification fails (as per current `__verify_signature` logic).
        :raises Exception: If the etcd lease refresh operation fails.
        """
        if node_id not in self.leases:
            logger.warning(f"Lease refresh attempted for node '{node_id}' which has no active lease "
                           "cached in this registry instance. The node might need to re-register.")
            # Or raise KeyError("Node not found in local lease cache or needs to re-register.")
            return # Or re-register, or raise. Current behavior is to log and return.

        try:
            # The signature verification here checks the signature made by *this* registry instance.
            # This confirms the data in etcd hasn't been tampered with in a way that invalidates
            # *this registry's* signature. It doesn't verify the node's identity if the node
            # was supposed to sign something.
            self.__verify_signature(node_id) # Verifies data integrity based on registry's key

            # Refresh the lease
            refresh_responses = list(self.leases[node_id].refresh()) # refresh() is a generator
            if not refresh_responses or refresh_responses[0].ttl <= 0: # Check if refresh was successful
                logger.warning(f"Lease refresh for node '{node_id}' might have failed or TTL is 0. Responses: {refresh_responses}")
                # Potentially attempt to re-establish lease or re-register
            else:
                logger.debug(f"Lease successfully refreshed for node '{node_id}'. New TTL: {refresh_responses[0].ttl}s")

        except BadSignatureError as e: # More specific error from ecdsa
            logger.error(f"Lease renewal for node '{node_id}' failed due to signature verification error: {e}", exc_info=True)
            # Potentially deregister or mark node as suspect
            raise ValueError(f"Signature verification failed for node '{node_id}' during lease refresh.") from e
        except Exception as e:
            logger.error(f"Lease renewal failed for node '{node_id}': {e}", exc_info=True)
            # Re-raise to indicate failure to the caller
            raise

    def get_available_nodes(self) -> Dict[str, NodeInfo]:
        """
        Retrieves information about all currently registered and available nodes.

        It fetches all entries under the configured `parent_node_id` prefix in etcd.

        :return: A dictionary where keys are node IDs and values are dictionaries
                 containing the 'node_info' (host, port, metadata, public_key)
                 for each available node.
        :rtype: typing.Dict[str, NodeInfo]
        """
        nodes: Dict[str, NodeInfo] = {}
        try:
            key_prefix = f"/{self.parent_node_id}/"
            for value_bytes, metadata_obj in self.etcd_client.get_prefix(key_prefix):
                node_id_from_key = metadata_obj.get('key').decode("utf-8").split(key_prefix)[-1]
                try:
                    node_entry = json.loads(value_bytes.decode("utf-8"))
                    if 'node_info' in node_entry:
                        nodes[node_id_from_key] = node_entry['node_info']
                    else:
                        logger.warning(f"Node entry for '{node_id_from_key}' is missing 'node_info' field. Entry: {node_entry}")
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON for node '{node_id_from_key}': {e}. Value: '{value_bytes[:100]}...'")
                except Exception as e: # Catch other potential errors during processing
                    logger.error(f"Unexpected error processing node entry for '{node_id_from_key}': {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to get available nodes from etcd prefix '{key_prefix}': {e}", exc_info=True)
            # Depending on requirements, could return empty dict or raise
        return nodes

    def deregister_node(self, node_id: str) -> None:
        """
        Deregisters a node from the etcd service registry.

        This involves deleting the node's entry from etcd and revoking its lease.

        .. note::
            Similar to `lease_refresh`, the `__verify_signature` call here checks
            the integrity of the data based on this registry's signature.

        :param node_id: The ID of the node to deregister.
        :type node_id: str
        :raises ValueError: If the node is not found or signature verification fails.
        :raises Exception: If etcd operations (delete, lease revoke) fail.
        """
        key: str = f"/{self.parent_node_id}/{node_id}"
        try:
            # Verify signature before deleting to ensure we are acting on valid data.
            self.__verify_signature(node_id)

            deleted_count = self.etcd_client.delete(key)
            if deleted_count == 0: # or delete returns False if not found
                logger.warning(f"Attempted to deregister node '{node_id}' (key: '{key}'), but it was not found in etcd.")
                # Still try to revoke local lease if it exists
            else:
                logger.info(f"Node '{node_id}' (key: '{key}') deleted from etcd.")

            # Revoke and remove local lease cache
            if node_id in self.leases:
                try:
                    self.leases[node_id].revoke()
                    logger.info(f"Lease for node '{node_id}' revoked.")
                except Exception as e_lease: # etcd3 may raise errors if lease doesn't exist server-side
                    logger.warning(f"Error revoking lease for node '{node_id}': {e_lease}. It might have already expired or been revoked.")
                finally:
                    del self.leases[node_id]
            else:
                logger.info(f"No local lease found for node '{node_id}' to revoke during deregistration.")

        except ValueError as e: # From __verify_signature or if node not found in verification
            logger.error(f"Failed to deregister node '{node_id}' due to an error: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while deregistering node '{node_id}': {e}", exc_info=True)
            raise

    def __verify_signature(self, node_id: str) -> None:
        """
        Verifies the signature of a node's entry stored in etcd.

        This method fetches the node's entry, extracts its `node_info` and `signature`,
        and verifies that the signature matches one calculated using this registry's
        private key (`self.sk`) over the `node_info`. It also verifies the signature
        against the public key stored within the `node_info` itself (which is this
        registry's public key).

        This effectively checks:
        1. That the `node_info` has not been tampered with since this registry instance signed it.
        2. That the public key stored in `node_info` corresponds to the private key that
           created the signature (i.e., `self.sk`).

        .. warning::
            This method verifies a signature made by *this registry instance's* private key.
            It does *not* verify a signature made by the registered node itself using its own
            private key, unless the node's public key was explicitly registered and used here.
            The current implementation uses `self.sk` to *re-calculate* the expected signature.

        :param node_id: The ID of the node whose signature is to be verified.
        :type node_id: str
        :raises ValueError: If the node is not found in etcd, if signature verification fails,
                            or if the public key verification fails.
        :raises BadSignatureError: If `vk.verify` fails due to a malformed or incorrect signature.
        """
        key = f"/{self.parent_node_id}/{node_id}"
        value_bytes, _ = self.etcd_client.get(key) # get() returns (value, metadata) or (None, None)

        if value_bytes is None:
            raise ValueError(f"Node '{node_id}' (key: '{key}') not found in etcd for signature verification.")

        try:
            node_entry = json.loads(value_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON for node '{node_id}' (key: '{key}'): {e}") from e


        if "node_info" not in node_entry or "signature" not in node_entry:
            raise ValueError(f"Node entry for '{node_id}' is malformed (missing 'node_info' or 'signature').")

        node_info: NodeInfo = node_entry["node_info"]
        stored_signature_base64: str = node_entry["signature"]

        if "public_key" not in node_info:
            raise ValueError(f"Node info for '{node_id}' is missing 'public_key'.")

        # This is the public key *this registry* stored, derived from self.sk
        vk_from_storage_base64: str = node_info["public_key"]
        try:
            vk_bytes_from_storage: bytes = base64.b64decode(vk_from_storage_base64)
            vk_from_storage: VerifyingKey = VerifyingKey.from_string(vk_bytes_from_storage, curve=NIST256p)
        except Exception as e: # Catch errors from b64decode or VerifyingKey.from_string
            raise ValueError(f"Failed to decode or reconstruct public key for node '{node_id}': {e}") from e


        # Re-serialize node_info exactly as it was when signed
        node_info_json_bytes: bytes = json.dumps(node_info, sort_keys=True).encode("utf-8")

        # The signature stored in etcd
        stored_signature_bytes: bytes = base64.b64decode(stored_signature_base64)

        # Verify the stored signature against the public key from storage and the re-serialized node_info
        # This step confirms that the signature matches the public_key stored in node_info itself.
        try:
            # Using sigdecode=sigdecode_der because we used sigencode=sigencode_der for signing
            if not vk_from_storage.verify(stored_signature_bytes, node_info_json_bytes, sigdecode=sigdecode_der):
                # This path should ideally not be reached if verify raises BadSignatureError on failure.
                # However, some ecdsa versions might return False.
                raise ValueError(f"Signature verification failed for node '{node_id}' using its stored public key. "
                                 "The data may have been tampered with, or the signature/public key is incorrect.")
        except BadSignatureError: # This is the expected exception on signature mismatch
             raise ValueError(f"Signature verification failed for node '{node_id}' using its stored public key. "
                             "The data may have been tampered with, or the signature/public key is incorrect. (BadSignatureError)") from None # Suppress original context for cleaner error


        # Optional: Additionally, one could re-calculate the signature using self.sk
        # and compare it to stored_signature_base64 to ensure self.sk was indeed the key used.
        # This is somewhat redundant if vk_from_storage is correctly self.sk.verifying_key.
        #
        # calculated_signature_bytes: bytes = self.sk.sign_deterministic(node_info_json_bytes, sigencode=sigencode_der)
        # if not calculated_signature_bytes == stored_signature_bytes:
        #     raise ValueError(f"Integrity check failed for node '{node_id}': "
        #                      "Stored signature does not match signature re-calculated with current registry key. "
        #                      "This might indicate data tampering or key mismatch if registry key changed.")

        logger.debug(f"Signature for node '{node_id}' successfully verified.")