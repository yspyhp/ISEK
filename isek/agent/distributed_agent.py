from isek.agent.abstract_agent import AbstractAgent
from isek.node.node import Node
from isek.utils.logger import logger
import threading
from typing import Any, Dict, Optional  # Added for type hinting in docstrings

# Assuming AbstractModel and Persona are defined elsewhere and relevant for **kwargs
# from isek.llm.abstract_model import AbstractModel
# from isek.agent.persona import Persona


class DistributedAgent(AbstractAgent, Node):
    """
    Represents an agent that operates within a distributed network of nodes.

    This class extends :class:`~isek.agent.abstract_agent.AbstractAgent` with capabilities
    from :class:`~isek.node.node.Node`, allowing it to communicate and interact
    with other nodes in a peer-to-peer or distributed fashion. It uses its persona
    to define its identity and introduction within the network.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the DistributedAgent.

        This constructor first initializes the :class:`~isek.agent.abstract_agent.AbstractAgent`
        part of the agent and then initializes the :class:`~isek.node.node.Node` part.
        It sets the agent's introduction based on its persona's biography.

        :param kwargs: Keyword arguments passed to the constructors of both
                       :class:`~isek.agent.abstract_agent.AbstractAgent` (e.g., `persona`, `model`)
                       and :class:`~isek.node.node.Node`.
        :type kwargs: typing.Any
        """
        # Call AbstractAgent's constructor
        AbstractAgent.__init__(self, **kwargs)
        # Generate intro from persona
        self.intro: str = self.persona.bio
        # self.intro_vector = self.embedding.embedding_one(self.intro) # Assuming embedding is part of AbstractAgent or set via kwargs
        # Call Node's constructor
        Node.__init__(self, **kwargs)

    def build(self, daemon: bool = False) -> None:
        """
        Builds and starts the server component of the distributed agent.

        If `daemon` is `False`, the server is built and run in the current thread,
        potentially blocking further execution. If `daemon` is `True`, the server
        is started in a separate daemon thread, allowing the main program to continue.

        This method typically calls `self.build_server()` from the :class:`~isek.node.node.Node`
        base class.

        :param daemon: If `True`, run the server in a daemon thread. Defaults to `False`.
        :type daemon: bool
        """
        if not daemon:
            self.build_server()
        else:
            # Ensure build_server is suitable for threading if it has complex state
            server_thread = threading.Thread(target=self.build_server, daemon=True)
            server_thread.start()

    def build_node_id(self) -> str:
        """
        Generates the unique identifier for this node in the distributed network.

        The node ID is derived from the agent's persona name. This method
        likely overrides a method from the :class:`~isek.node.node.Node` base class.

        :return: The unique node identifier.
        :rtype: str
        """
        return self.persona.name

    def metadata(self) -> Dict[str, str]:
        """
        Provides metadata about this agent/node.

        This metadata can be shared with other nodes in the network to identify
        and describe this agent. It includes the agent's name and introduction.
        This method likely overrides a method from the :class:`~isek.node.node.Node` base class.

        :return: A dictionary containing metadata, specifically "name" and "intro".
        :rtype: typing.Dict[str, str]
        """
        return {"name": self.persona.name, "intro": self.intro}

    def on_message(self, sender: Any, message: str) -> Optional[str]:
        """
        Handles incoming messages from other nodes in the network.

        This method is a callback invoked by the :class:`~isek.node.node.Node`
        infrastructure when a message is received. It logs the message and then
        processes it using the agent's main :meth:`~isek.agent.abstract_agent.AbstractAgent.run` logic.

        :param sender: The identifier of the sending node. The exact type depends
                       on the node implementation.
        :type sender: typing.Any
        :param message: The content of the message received.
        :type message: str
        :return: The agent's response to the message, or `None` if the `run` method
                 (or its overridden version) returns `None`.
        :rtype: typing.Optional[str]
        """
        logger.info(f"[{self.persona.name}] received message from {sender}: {message}")
        # Assuming self.run from AbstractAgent returns a string or None
        return self.run(message)

    def search_partners(self, query: str) -> str:
        """
        Searches for suitable partner nodes in the network to help answer a query.

        This method is used when the agent determines it might lack the necessary
        knowledge or capabilities to handle a query on its own.
        It first retrieves a list of potential nodes based on a vector search
        (using :meth:`~isek.node.node.Node.get_nodes_by_vector`) and then uses
        the language model to select the single best-fitting partner from this list
        based on the query and the partners' introductions.

        :param query: The query or task for which partners are being sought.
        :type query: str
        :return: A string containing the name, node_id, and reason for selecting
                 the best-fitting partner, formatted as "name: XXX, node_id: XXX, Reason: XXX".
                 Returns an empty string or an error message if no suitable partner is found or
                 if the LLM call fails.
        :rtype: str
        """
        logger.info(f"[{self.persona.name}] Searching partners with query: {query}")
        # Assuming get_nodes_by_vector returns a representation of nodes that can be stringified
        nodes_info = str(self.get_nodes_by_vector(query))

        matching_node_template = f"""
            I am looking for partners to help me with a query, here are the nodes I found:
            {nodes_info}
            this is the query:
            {query}

            please return the node name and node_id of only one node that fit best with the query based on he intro of that node.
            reason always less than 10 words.

            return in the format of:
            name: XXX, node_id: XXX, Reason: XXX
        """
        # Assuming self.model.generate_text is available from AbstractAgent
        # and returns a string.
        try:
            result: str = self.model.generate_text(prompt=matching_node_template)
            return result
        except AttributeError:
            logger.error(
                f"[{self.persona.name}] Model or generate_text method not available for partner search."
            )
            return "Error: Model not available for partner search."
        except Exception as e:
            logger.error(
                f"[{self.persona.name}] Error during partner search LLM call: {e}"
            )
            return f"Error during partner search: {e}"
