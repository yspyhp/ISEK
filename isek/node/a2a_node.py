from typing import Any, Optional

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.apps.jsonrpc import JSONRPCApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from isek.node.node_v2 import Node
from isek.node.registry import Registry
from isek.squad.a2a_squad import DefaultAgentExecutor
from isek.squad.squad import Squad


class A2ANode(Node):
    def __init__(
        self,
        a2a_application: Optional[JSONRPCApplication] = None,
        host: str = "localhost",
        port: int = 8080,
        node_id: Optional[str] = None,
        registry: Optional[Registry] = None,
        squad: Optional[Squad] = None,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            port=port,
            node_id=node_id,
            registry=registry,
            squad=squad,
            **kwargs,
        )
        if a2a_application:
            self.a2a_application = a2a_application
        else:
            self.a2a_application = self.build_a2a_application()
        # todo: squad to a2a_application if a2a_application is None

    def bootstrap_server(self):
        uvicorn.run(self.a2a_application.build(), host="0.0.0.0", port=self.port)

    def stop_server(self) -> None:
        pass

    def build_a2a_application(self) -> JSONRPCApplication:
        if not self.squad or not isinstance(self.squad, Squad):
            return self.default_a2a_application()
        else:
            request_handler = DefaultRequestHandler(
                agent_executor=DefaultAgentExecutor(self.squad),
                task_store=InMemoryTaskStore(),
            )

            self.a2a_application = A2AStarletteApplication(
                agent_card=self.squad.get_a2a_agent_card(), http_handler=request_handler
            )
        return self.a2a_application
        # skill = AgentSkill(
        #     id="hello_world",
        #     name="Returns hello world",
        #     description="just returns hello world",
        #     tags=["hello world"],
        #     examples=["hi", "hello world"],
        # )
        # # --8<-- [end:AgentSkill]
        #
        # extended_skill = AgentSkill(
        #     id="super_hello_world",
        #     name="Returns a SUPER Hello World",
        #     description="A more enthusiastic greeting, only for authenticated users.",
        #     tags=["hello world", "super", "extended"],
        #     examples=["super hi", "give me a super hello"],
        # )
        #
        # # --8<-- [start:AgentCard]
        # # This will be the public-facing agent card
        # public_agent_card = AgentCard(
        #     name="Hello World Agent",
        #     description="Just a hello world agent",
        #     url="http://0.0.0.0:9999/",
        #     version="1.0.0",
        #     defaultInputModes=["text"],
        #     defaultOutputModes=["text"],
        #     capabilities=AgentCapabilities(streaming=True),
        #     skills=[skill],  # Only the basic skill for the public card
        #     supportsAuthenticatedExtendedCard=True,
        # )
        # # --8<-- [end:AgentCard]
        #
        # # This will be the authenticated extended agent card
        # # It includes the additional 'extended_skill'
        # specific_extended_agent_card = public_agent_card.model_copy(
        #     update={
        #         "name": "Hello World Agent - Extended Edition",  # Different name for clarity
        #         "description": "The full-featured hello world agent for authenticated users.",
        #         "version": "1.0.1",  # Could even be a different version
        #         # Capabilities and other fields like url, defaultInputModes, defaultOutputModes,
        #         # supportsAuthenticatedExtendedCard are inherited from public_agent_card unless specified here.
        #         "skills": [
        #             skill,
        #             extended_skill,
        #         ],  # Both skills for the extended card
        #     }
        # )
        #
        # request_handler = DefaultRequestHandler(
        #     # agent_executor=HelloWorldAgentExecutor(),
        #     task_store=InMemoryTaskStore(),
        # )

        # server = A2AStarletteApplication(
        #     agent_card=public_agent_card,
        #     http_handler=request_handler,
        #     extended_agent_card=specific_extended_agent_card,
        # )
        # return None
