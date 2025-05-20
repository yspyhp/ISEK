import yaml
import etcd3 # type: ignore # If etcd3 lacks type stubs
from typing import Any, Optional, Dict, Union # Added Union

from isek.util.logger import logger, LoggerManager # Assuming these are configured/available
from isek.agent.persona import Persona
from isek.agent.single_agent import SingleAgent
from isek.agent.distributed_agent import DistributedAgent
from isek.llm.openai_model import OpenAIModel # Example, actual LLM class might vary
from isek.embedding.openai_embedding import OpenAIEmbedding # Example, actual Embedding class might vary
from isek.node.etcd_registry import EtcdRegistry
from isek.node.isek_center_registry import IsekCenterRegistry
from isek.node.registry import Registry # Import the abstract Registry for type hinting
from isek.llm import llms # Assuming this is a module or dict mapping names to LLM classes
from isek.embedding import embeddings # Assuming this maps names to Embedding classes
from isek.llm.abstract_model import AbstractModel # For type hinting
from isek.embedding.abstract_embedding import AbstractEmbedding # For type hinting


class IsekConfig:
    """
    Manages application configuration loaded from a YAML file.

    This class provides a structured way to access configuration values
    and to instantiate various components of the Isek system, such as agents,
    registries, language models (LLMs), and embedding models, based on the
    loaded configuration.
    """

    def __init__(self, yaml_path: str):
        """
        Initializes the IsekConfig by loading configuration from a YAML file.

        :param yaml_path: The file path to the YAML configuration file.
        :type yaml_path: str
        :raises FileNotFoundError: If the `yaml_path` does not exist.
        :raises yaml.YAMLError: If the YAML file is malformed.
        :raises Exception: For other unexpected errors during file loading or parsing.
        """
        self.config: Dict[str, Any] = {}
        try:
            with open(yaml_path, "r") as f:
                self.config = yaml.safe_load(f)
            if not isinstance(self.config, dict):
                # Ensure loaded config is a dictionary, yaml.safe_load can return other types for simple YAMLs
                raise ValueError("YAML root must be a mapping (dictionary).")
            logger.info(f"IsekConfig loaded successfully from '{yaml_path}'.")
        except FileNotFoundError:
            logger.error(f"Configuration file not found at '{yaml_path}'.")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file '{yaml_path}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading IsekConfig from '{yaml_path}': {e}", exc_info=True)
            raise

    def get(self, *keys: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Retrieves a configuration value using a sequence of keys (path).

        Traverses the nested configuration dictionary. If any key in the path
        is not found, or if the path leads to a `None` value explicitly,
        it returns the `default` value.

        Example: `config.get("agent", "persona", "name", default="Unknown")`

        :param keys: A sequence of string keys representing the path to the desired value.
        :type keys: str
        :param default: The value to return if the path is not found or the value is `None`.
                        Defaults to `None`.
        :type default: typing.Optional[typing.Any]
        :return: The configuration value if found, otherwise the `default` value.
        :rtype: typing.Optional[typing.Any]
        """
        value = self.config
        for key in keys:
            if not isinstance(value, dict): # Cannot traverse further if not a dict
                return default
            value = value.get(key) # Using .get() which returns None if key not found
            if value is None: # Check for explicit None or key not found
                # This condition means if a key exists but its value is `null` in YAML,
                # it will also return default. If you want to distinguish `null` from
                # "key not found", the logic needs adjustment.
                return default
        return value

    def get_sub_config(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a sub-dictionary from the configuration.

        :param key: The top-level key for the desired sub-configuration dictionary.
        :type key: str
        :return: The sub-configuration dictionary if the key exists and its value
                 is a dictionary, otherwise `None`.
        :rtype: typing.Optional[typing.Dict[str, typing.Any]]
        """
        sub_config = self.config.get(key)
        if isinstance(sub_config, dict):
            return sub_config
        elif sub_config is not None:
            logger.warning(f"Expected sub-config for key '{key}' to be a dictionary, "
                           f"but found type {type(sub_config)}. Returning None.")
        return None

    def load_agent(self) -> Union[SingleAgent, DistributedAgent]:
        """
        Loads and returns an agent instance (SingleAgent or DistributedAgent)
        based on the configuration.

        Configures the agent with its persona, language model, and, if distributed,
        its network settings (host, port, registry) and embedding model.
        Also initializes the logger based on the 'debug' setting.

        :return: An instance of :class:`~isek.agent.single_agent.SingleAgent` or
                 :class:`~isek.agent.distributed_agent.DistributedAgent`.
        :rtype: typing.Union[isek.agent.single_agent.SingleAgent, isek.agent.distributed_agent.DistributedAgent]
        :raises ValueError: If essential configuration for the agent is missing or invalid.
        """
        is_distributed: bool = self.get("distributed", "enabled", default=False) # More specific path

        agent_config = self.get_sub_config("agent")
        if not agent_config:
            raise ValueError("Missing 'agent' configuration section.")

        persona_path = agent_config.get("persona_path")
        if not persona_path:
            raise ValueError("Missing 'agent.persona_path' in configuration.")
        try:
            persona = Persona.load(persona_path)
        except Exception as e:
            raise ValueError(f"Failed to load persona from '{persona_path}': {e}") from e

        debug_level: Optional[str] = agent_config.get("debug_level", "INFO") # e.g. "DEBUG", "INFO"
        # Assuming LoggerManager.init takes a string log level
        try:
            LoggerManager.init(level=debug_level.upper() if debug_level else "INFO")
        except Exception as e:
            logger.warning(f"Failed to initialize LoggerManager with level '{debug_level}': {e}. Using default.")


        llm = self.load_llm() # load_llm will handle if it's None or raises error

        if not is_distributed:
            logger.info("Loading SingleAgent.")
            return SingleAgent(persona=persona, model=llm)

        logger.info("Loading DistributedAgent.")
        dist_config = self.get_sub_config("distributed")
        if not dist_config:
            raise ValueError("Missing 'distributed' configuration section for a distributed agent.")

        host: str = dist_config.get("server", {}).get("host", "localhost") # Nested get
        port: int = dist_config.get("server", {}).get("port", 8080)

        registry = self.load_registry() # Handles errors internally or returns specific registry
        embedding = self.load_embedding() # Handles if None

        return DistributedAgent(
            host=host, port=port, registry=registry,
            persona=persona, model=llm, embedding=embedding
        )

    def load_registry(self) -> Registry:
        """
        Loads and returns a service registry instance based on the configuration.

        Supports "etcd" or "isek_center" (defaulting to "isek_center" if 'registry.mode' is missing).

        :return: An instance of a :class:`~isek.node.registry.Registry` implementation.
        :rtype: isek.node.registry.Registry
        :raises ValueError: If the registry configuration is missing or invalid.
        """
        registry_config = self.get_sub_config("registry")
        if not registry_config:
            logger.warning("Registry configuration section ('registry') not found. Defaulting to IsekCenterRegistry with default settings.")
            return IsekCenterRegistry() # Default behavior

        registry_mode: str = registry_config.get("mode", "isek_center") # Default to isek_center

        if registry_mode == "etcd":
            logger.info("Loading EtcdRegistry.")
            return self.load_etcd_registry(registry_config.get("etcd", {}))
        elif registry_mode == "isek_center":
            logger.info("Loading IsekCenterRegistry.")
            return self.load_isek_center_registry(registry_config.get("isek_center", {}))
        else:
            raise ValueError(f"Unsupported registry mode: '{registry_mode}'. Supported modes are 'etcd', 'isek_center'.")

    def load_etcd_registry(self, etcd_specific_config: Dict[str, Any]) -> EtcdRegistry:
        """
        Loads an EtcdRegistry instance using etcd-specific configuration.

        :param etcd_specific_config: A dictionary containing parameters for
                                     `etcd3.Etcd3Client` (e.g., `host`, `port`)
                                     and `EtcdRegistry` (e.g., `ttl`, `parent_node_id`).
        :type etcd_specific_config: typing.Dict[str, typing.Any]
        :return: An instance of :class:`~isek.node.etcd_registry.EtcdRegistry`.
        :rtype: isek.node.etcd_registry.EtcdRegistry
        :raises ValueError: If essential etcd configuration is missing or `etcd3.client` fails.
        """
        # Extract etcd3.client specific args vs EtcdRegistry specific args
        client_args = {k: v for k, v in etcd_specific_config.items() if k in ['host', 'port', 'ca_cert', 'cert_key', 'cert_cert', 'timeout', 'user', 'password', 'grpc_options']}
        registry_args = {k: v for k, v in etcd_specific_config.items() if k in ['ttl', 'parent_node_id']}

        if not client_args.get("host"): # host is usually required for etcd3.client
            raise ValueError("Missing 'host' in 'registry.etcd' configuration for EtcdRegistry.")
        
        try:
            etcd_client = etcd3.client(**client_args)
        except Exception as e:
            raise ValueError(f"Failed to create etcd3.Etcd3Client with config {client_args}: {e}") from e
        
        return EtcdRegistry(etcd_client=etcd_client, **registry_args)

    def load_isek_center_registry(self, isek_center_specific_config: Dict[str, Any]) -> IsekCenterRegistry:
        """
        Loads an IsekCenterRegistry instance using its specific configuration.

        :param isek_center_specific_config: A dictionary containing parameters for
                                            :class:`~isek.node.isek_center_registry.IsekCenterRegistry`
                                            (e.g., `host`, `port`).
        :type isek_center_specific_config: typing.Dict[str, typing.Any]
        :return: An instance of :class:`~isek.node.isek_center_registry.IsekCenterRegistry`.
        :rtype: isek.node.isek_center_registry.IsekCenterRegistry
        """
        # IsekCenterRegistry takes host, port directly.
        return IsekCenterRegistry(**isek_center_specific_config)

    def load_llm(self) -> Optional[AbstractModel]:
        """
        Loads and returns a language model (LLM) instance based on the configuration.

        Uses an 'llms' dispatcher (assumed to be a dictionary or module mapping
        mode names to LLM classes) to instantiate the correct LLM type.

        :return: An instance of an :class:`~isek.llm.abstract_model.AbstractModel`
                 implementation, or `None` if no LLM is configured or if the mode is "None".
        :rtype: typing.Optional[isek.llm.abstract_model.AbstractModel]
        :raises ValueError: If the configured LLM mode is not supported or its specific
                            configuration is missing/invalid.
        """
        llm_config_section = self.get_sub_config("llm")
        if not llm_config_section:
            logger.info("No 'llm' configuration section found. LLM will not be loaded.")
            return None

        llm_mode: Optional[str] = llm_config_section.get("mode")
        if not llm_mode or llm_mode.lower() == "none":
            logger.info(f"LLM mode is '{llm_mode}'. LLM will not be loaded.")
            return None

        llm_class = llms.get(llm_mode) # Assuming llms is a dict: llms = {"openai": OpenAIModel, ...}
        if not llm_class:
            raise ValueError(f"Unsupported LLM mode: '{llm_mode}'. Not found in `llms` dispatcher.")

        specific_llm_config = llm_config_section.get(llm_mode, {})
        if not specific_llm_config and not isinstance(specific_llm_config, dict) : # Check if it's a dict
             logger.warning(f"Configuration for LLM mode '{llm_mode}' (llm.{llm_mode}) not found or not a dict. "
                           "Attempting to initialize with defaults.")
             specific_llm_config = {}

        logger.info(f"Loading LLM with mode: '{llm_mode}'.")
        try:
            return llm_class(**specific_llm_config)
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM '{llm_mode}' with config {specific_llm_config}: {e}") from e

    def load_embedding(self) -> Optional[AbstractEmbedding]:
        """
        Loads and returns an embedding model instance based on the configuration.

        Uses an 'embeddings' dispatcher (assumed to be a dictionary or module
        mapping mode names to embedding classes) to instantiate the correct type.

        :return: An instance of an :class:`~isek.embedding.abstract_embedding.AbstractEmbedding`
                 implementation, or `None` if no embedding model is configured or if the mode is "None".
        :rtype: typing.Optional[isek.embedding.abstract_embedding.AbstractEmbedding]
        :raises ValueError: If the configured embedding mode is not supported or its specific
                            configuration is missing/invalid.
        """
        embedding_config_section = self.get_sub_config("embedding")
        if not embedding_config_section:
            logger.info("No 'embedding' configuration section found. Embedding model will not be loaded.")
            return None
            
        embedding_mode: Optional[str] = embedding_config_section.get("mode")
        if not embedding_mode or embedding_mode.lower() == "none":
            logger.info(f"Embedding mode is '{embedding_mode}'. Embedding model will not be loaded.")
            return None

        embedding_class = embeddings.get(embedding_mode) # e.g., embeddings = {"openai": OpenAIEmbedding, ...}
        if not embedding_class:
            raise ValueError(f"Unsupported embedding mode: '{embedding_mode}'. Not found in `embeddings` dispatcher.")

        specific_embedding_config = embedding_config_section.get(embedding_mode, {})
        if not specific_embedding_config and not isinstance(specific_embedding_config, dict):
            logger.warning(f"Configuration for embedding mode '{embedding_mode}' (embedding.{embedding_mode}) "
                           "not found or not a dict. Attempting to initialize with defaults.")
            specific_embedding_config = {}
            
        logger.info(f"Loading embedding model with mode: '{embedding_mode}'.")
        try:
            return embedding_class(**specific_embedding_config)
        except Exception as e:
            raise ValueError(f"Failed to initialize embedding model '{embedding_mode}' with config {specific_embedding_config}: {e}") from e