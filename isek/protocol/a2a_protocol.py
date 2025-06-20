import asyncio
from typing import Any
from typing import Optional
from uuid import uuid4

import httpx
import uvicorn
from a2a.client import A2AClient
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.apps.jsonrpc import JSONRPCApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
)
from a2a.utils import new_agent_text_message

from isek.protocol.protocol import Protocol
from isek.squad.default_squad import DefaultSquad
from isek.squad.squad import Squad


class DefaultAgentExecutor(AgentExecutor):
    def __init__(self, url: str, squad: Squad):
        self.url = url
        self.squad = squad

    def get_a2a_agent_card(self) -> AgentCard:
        squad_card = self.squad.get_squad_card()
        return AgentCard(
            name=squad_card.name,
            description=f"bio:{squad_card.bio}\nlore:{squad_card.lore}\nknowledge:{squad_card.knowledge}",
            url=self.url,
            version="1.0.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=AgentCapabilities(streaming=True),
            skills=[],
            # supportsAuthenticatedExtendedCard=True,
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = self.squad.run(prompt=context.message)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")


class A2AProtocol(Protocol):
    def __init__(
        self,
        a2a_application: Optional[JSONRPCApplication] = None,
        host: str = "localhost",
        port: int = 8080,
        squad: Optional[Squad] = None,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            port=port,
            squad=squad,
            **kwargs,
        )

        if a2a_application:
            self.url = a2a_application.agent_card.url
            self.a2a_application = a2a_application
        else:
            self.url = f"http://{host}:{port}/"
            self.a2a_application = self.build_a2a_application()

    def bootstrap_server(self):
        uvicorn.run(self.a2a_application.build(), host="0.0.0.0", port=self.port)

    def stop_server(self) -> None:
        pass

    def send_message(self, target_address, message):
        httpx_client = httpx.AsyncClient()
        client = A2AClient(httpx_client=httpx_client, url=target_address)
        send_message_payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = asyncio.run(client.send_message(request))
        return response.model_dump(mode="json", exclude_none=True)["result"]["parts"][
            0
        ]["text"]

    def build_a2a_application(self) -> JSONRPCApplication:
        if not self.squad or not isinstance(self.squad, Squad):
            return self.default_a2a_application()
        else:
            agent_executor = DefaultAgentExecutor(self.url, self.squad)
            request_handler = DefaultRequestHandler(
                agent_executor=agent_executor,
                task_store=InMemoryTaskStore(),
            )

            return A2AStarletteApplication(
                agent_card=agent_executor.get_a2a_agent_card(),
                http_handler=request_handler,
            )

    def default_a2a_application(self):
        if not self.squad:
            self.squad = DefaultSquad()
        agent_executor = DefaultAgentExecutor(self.url, self.squad)
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )

        return A2AStarletteApplication(
            agent_card=agent_executor.get_a2a_agent_card(), http_handler=request_handler
        )
