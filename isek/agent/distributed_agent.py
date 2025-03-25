from isek.agent.abstract_agent import AbstractAgent
from isek.node.node import Node
from isek.util.logger import logger
import threading


class DistributedAgent(AbstractAgent, Node):

    def __init__(
            self,
            **kwargs
    ):
        # 调用 AbstractAgent 的构造方法
        AbstractAgent.__init__(self, **kwargs)
        # 生成 intro
        self.intro = self.persona.bio
        # self.intro_vector = self.embedding.embedding_one(self.intro)
        # 调用 Node 的构造方法
        Node.__init__(self, **kwargs)

    def build(self, daemon=False):
        if not daemon:
            self.build_server()
        else:
            termination_thread = threading.Thread(target=self.build_server, daemon=True)
            termination_thread.start()

    def build_node_id(self) -> str:
        return self.persona.name

    def metadata(self):
        return {
            "name": self.persona.name,
            "intro": self.intro
        }

    def on_message(self, sender, message):
        logger.info(f"[{self.persona.name}] received message from {sender}: {message}")

        return self.run(message)

    def search_partners(self, query: str) -> str:
        """
        in case of lacking knowledge to answer the query, search for partners based on the query,
        Args:
            query: str
        Returns: partner name and node_id
        """
        logger.info(f"[{self.persona.name}] Searching partners with query: {query}")
        nodes = str(self.get_nodes_by_vector(query))
        # 前期node少，用语意理解来匹配 后期vector来匹配
        
        matching_node_template = f"""
            I am looking for partners to help me with a query, here are the nodes I found:
            {nodes}
            this is the query:
            {query}

            please return the node name and node_id of only one node that fit best with the query based on he intro of that node.
            reason always less than 10 words.

            return in the format of:
            name: XXX, node_id: XXX, Reason: XXX

        """
        result = self.model.generate_text(prompt=matching_node_template)
        return result