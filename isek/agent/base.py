from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional, Union
from uuid import uuid4

from isek.memory.memory import Memory, UserMemory
from isek.models.base import Model, SimpleMessage
from isek.tools.toolkit import Toolkit
from isek.utils.log import log, LoggerManager


@dataclass
class AgentCard:
    """Metadata about an agent for discovery and identification purposes."""

    name: str
    description: str
    capabilities: List[str]
    tools: List[str]
    model_type: str


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations in ISEK.

    This class defines the interface that all agent implementations must follow.
    Agents are intelligent entities that can process messages, use tools, maintain memory,
    and interact with language models to provide responses.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        agent_id: Optional[str] = None,
        model: Optional[Model] = None,
        memory: Optional[Memory] = None,
        tools: Optional[List[Toolkit]] = None,
        description: Optional[str] = None,
        success_criteria: Optional[str] = None,
        instructions: Optional[Union[str, List[str], Callable]] = None,
        debug_mode: bool = False,
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent name
            agent_id: Agent UUID (autogenerated if not set)
            model: Model for this Agent
            memory: Agent memory
            tools: Tools provided to the Model
            description: A description of the Agent
            success_criteria: Success criteria for the task
            instructions: List of instructions for the agent
            debug_mode: Enable debug logs
        """
        self.name = name
        self.agent_id = agent_id or str(uuid4())
        self.model = model
        self.memory = memory
        self.tools = tools or []
        self.description = description
        self.success_criteria = success_criteria
        self.instructions = instructions
        self.debug_mode = debug_mode

        # Set debug mode
        if self.debug_mode:
            LoggerManager.set_level("DEBUG")
            log.debug(
                f"Agent initialized: {self.name or 'Unnamed'} (ID: {self.agent_id})"
            )

    @abstractmethod
    def run(
        self, message: str, user_id: str = "default", session_id: Optional[str] = None
    ) -> str:
        """
        Run the agent with a message and return the response.

        Args:
            message: The input message for the agent to process
            user_id: Identifier for the user making the request
            session_id: Optional session identifier for conversation tracking

        Returns:
            str: The agent's response

        Raises:
            NotImplementedError: If the concrete class doesn't implement this method
        """
        pass

    @abstractmethod
    def get_agent_card(self) -> AgentCard:
        """
        Get metadata about the agent for discovery and identification purposes.

        Returns:
            AgentCard: A card containing agent metadata

        Raises:
            NotImplementedError: If the concrete class doesn't implement this method
        """
        pass

    def _store_conversation(
        self, user_id: str, session_id: str, user_message: str, agent_response: str
    ) -> None:
        """
        Store the conversation in memory.

        Args:
            user_id: The user identifier
            session_id: The session identifier
            user_message: The user's message
            agent_response: The agent's response
        """
        if not self.memory:
            return

        # Store user memory
        user_memory = UserMemory(
            memory=f"User: {user_message}\nAgent: {agent_response}",
            topics=["conversation"],
        )
        self.memory.add_user_memory(user_memory, user_id)

        # Store run
        run_data = {
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": str(uuid4()),  # Simple timestamp for now
        }
        self.memory.add_run(session_id, run_data)

        if self.debug_mode:
            log.debug(
                f"Stored conversation in memory for user {user_id}, session {session_id}"
            )

    def _build_system_message(self) -> str:
        """
        Build the system message from agent configuration.

        Returns:
            str: The system message for the agent
        """
        parts = []

        if self.description:
            parts.append(f"Description: {self.description}")

        if self.success_criteria:
            parts.append(f"Success Criteria: {self.success_criteria}")

        if self.instructions:
            if isinstance(self.instructions, str):
                parts.append(f"Instructions: {self.instructions}")
            elif isinstance(self.instructions, list):
                parts.append("Instructions:")
                for instruction in self.instructions:
                    parts.append(f"- {instruction}")
            elif callable(self.instructions):
                parts.append(f"Instructions: {self.instructions()}")

        return "\n".join(parts) if parts else "You are a helpful AI assistant."

    def _prepare_tools_parameter(self) -> Optional[List[dict]]:
        """
        Prepare tools parameter for model calls.

        Returns:
            Optional[List[dict]]: Tools parameter for the model, or None if no tools
        """
        if not self.tools:
            return None

        tools_param = []
        for toolkit in self.tools:
            for func in toolkit.functions.values():
                tools_param.append({"type": "function", "function": func.to_dict()})

        return tools_param

    def _prepare_messages(
        self, message: str, user_id: str, system_message: Optional[str] = None
    ) -> List[SimpleMessage]:
        """
        Prepare messages for model calls.

        Args:
            message: The user message
            user_id: The user identifier
            system_message: Optional custom system message

        Returns:
            List[SimpleMessage]: List of messages for the model
        """
        messages = []

        # Add system message
        if system_message:
            messages.append(SimpleMessage(role="system", content=system_message))
        else:
            built_system_message = self._build_system_message()
            if (
                built_system_message
                and built_system_message != "You are a helpful AI assistant."
            ):
                messages.append(
                    SimpleMessage(role="system", content=built_system_message)
                )

        # Add memory context
        memory_context = self._get_memory_context(user_id)
        if memory_context:
            messages.append(
                SimpleMessage(
                    role="system", content=f"Previous context:\n{memory_context}"
                )
            )

        # Add user message
        messages.append(SimpleMessage(role="user", content=message))

        return messages

    def _get_memory_context(self, user_id: str) -> Optional[str]:
        """
        Get relevant memory context for the user.

        Args:
            user_id: The user identifier

        Returns:
            Optional[str]: Memory context as a string, or None if no memory available
        """
        if not self.memory:
            return None

        memories = self.memory.get_user_memories(user_id)
        if not memories:
            return None

        # For now, include all memories (in a real implementation, you might want to filter by relevance)
        memory_texts = []
        for memory in memories:
            memory_texts.append(f"- {memory.memory}")

        return "Previous interactions:\n" + "\n".join(memory_texts)

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.

        Returns:
            List[str]: List of tool names
        """
        if not self.tools:
            return []

        tool_names = []
        for toolkit in self.tools:
            tool_names.extend(toolkit.functions.keys())
        return tool_names

    def has_memory(self) -> bool:
        """
        Check if the agent has memory capabilities.

        Returns:
            bool: True if the agent has memory, False otherwise
        """
        return self.memory is not None

    def has_tools(self) -> bool:
        """
        Check if the agent has tools.

        Returns:
            bool: True if the agent has tools, False otherwise
        """
        return self.tools is not None and len(self.tools) > 0

    def has_model(self) -> bool:
        """
        Check if the agent has a model.

        Returns:
            bool: True if the agent has a model, False otherwise
        """
        return self.model is not None

    def __repr__(self) -> str:
        return f"BaseAgent(name='{self.name}', id='{self.agent_id}')"

    def __str__(self) -> str:
        return f"Agent '{self.name or 'Unnamed'}' (ID: {self.agent_id})"
