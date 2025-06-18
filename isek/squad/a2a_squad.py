from abc import abstractmethod

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCard,
)
from a2a.utils import new_agent_text_message

from isek.squad.squad import Squad


class A2ASquad(Squad, AgentExecutor):
    def __init__(self, a2a_agent_card: AgentCard):
        self.a2a_agent_card = a2a_agent_card
        self.squad_card = self.convert(a2a_agent_card)

    @abstractmethod
    def run(self, prompt):
        pass

    @abstractmethod
    def get_squad_card(self) -> dict:
        pass

    def convert(self, a2a_agent_card: AgentCard):
        return {}

    def get_a2a_agent_card(self):
        return self.a2a_agent_card


class DefaultAgentExecutor(AgentExecutor):
    def __init__(self, squad: Squad):
        self.squad = squad

    def get_a2a_agent_card(self):
        return

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = self.squad.run(prompt=context.message)
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
