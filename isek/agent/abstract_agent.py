from abc import ABC, abstractmethod
from isek.llm.openai_model import OpenAIModel
from isek.embedding.openai_embedding import OpenAIEmbedding
from isek.llm.abstract_model import AbstractModel
from isek.embedding.abstract_embedding import AbstractEmbedding
from typing import Optional, List, Callable
from isek.agent.persona import Persona
from isek.agent.memory import AgentMemory
from isek.agent.toolbox import ToolBox
import time
# add logging
from isek.util.logger import LoggerManager, logger


class AbstractAgent(ABC):
    def __init__(
            self,
            persona: Persona = None,
            model: Optional[AbstractModel] = None,
            tools: List[Callable] = None,
            heartbeat: bool = False,
            **kwargs
    ) -> None:
        self.persona = persona or Persona.default()
        self.model = model or OpenAIModel()
        self.memory_manager = AgentMemory()
        self.tool_manager = ToolBox(persona=self.persona)
        # Register action tools
        if tools:
            self.tool_manager.register_tools(tools)

    @abstractmethod
    def build(self, daemon=False):
        pass

    def run(self, input : str = None) -> None:
        """
        Args:
            input:
                user instructions or environment signals, such as text, image, file, web page, etc.
        Returns:
            None
        """
        logger.info(f"[{self.persona.name}] ++++++++++Cycle Started++++++++++")
        response = self.response(input)
        logger.info(f"[{self.persona.name}][Response]: {response}")
        logger.info(f"[{self.persona.name}] ----------Cycle Ended------------")
        
        return response
    
    def hearbeat(self):
        """
        This is a heartbeat function. Call this function when you want to keep the agent alive.
        """
        self.run()
        
    def run_cli(self):
        while True:
            time.sleep(0.2)
            text = input("Enter your command: ")
            if text == "exit":
                break
            self.run(text)
            
    def response(self, input: str) -> str:
        """
        Response to the input
        Args:
            input: user instructions or environment signals, such as text, image, file, web page, etc.
        Returns:
            str: response to the input
        """
        if input is not None and input != "":
            logger.info(f"[{self.persona.name}][Trigger: Input]: {input}")
        else:
            logger.info(f"[{self.persona.name}][Trigger: Heartbeat]")
        self.memory_manager.store_memory_item("User:" + input)
        # Build template for action phase
        template = self._build_templates()
        messages = []
        
        # Setup available tools for action phase
        tools = self.tool_manager.get_tool_names()
        tool_schemas = self.tool_manager.get_tool_schemas()
        
        # Main action loop
        while True:
            # Get AI completion with tool calling
            response = self.model.create(
                messages=[{"role": "system", "content": template}] + messages,
                systems=[],
                tool_schemas=tool_schemas or None,
            ).choices[0].message
            messages.append(response)
            
            # Process text response
            if response.content:
                self.memory_manager.store_memory_item("Agent:" + response.content)
                
            # Check if we're done with tool calls
            if not response.tool_calls:
                return response.content

            # Handle tool calls
            for tool_call in response.tool_calls:
                result = self.tool_manager.execute_tool_call(tool_call=tool_call)
                result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
                messages.append(result_message)
                
    def _build_templates(self):
        """Build templates for the action phase."""
        # Get recent memory items
        recent_memory = self.memory_manager.get_recent_memory_items()
        # state = self.memory_manager.get_all_state_variables()
        # tasks = self.memory_manager.get_pending_tasks()
       
        # Return all templates as a dictionary
        routine=""
        if "routine" in self.persona.__dict__:
            routine = self.persona.routine
        
        templates = {
            "persona": f'''       
                "You Name is:
                "{self.persona.name}"
                "You are a {self.persona.bio}"
                "Your mission is to {self.persona.lore}"
                "You have the following knowledge: {self.persona.knowledge}"
            ''',
            "system": f'''
                "You have the freedom to reason and act to help you achieve your goal."
                "try your best to use tools to improve responses quality."
                "please be concise and clear in your responses."
                "in most cases, you should only provide one or two sentence."
                "in rare cases, you may provide a longer response." 
            ''',
            "routine": f'''
            "{routine}"
            ''',
            "tool": f'''
                "You have the following tools available: {self.tool_manager.get_tool_names()}"
            ''',
            
            "closing": f'''
                response base on the following conversation: 
                {recent_memory}
            '''
        }
        # add all the templates together
        template = ""
        for key in templates:
            template += templates[key]
        return template
        
    def decompose_task(self, command):
        """
        This is message decomposer. Call this function when you want to decompose a task to a list of subtasks.
        """
        task_decomposer_template = f"""
        As a Task Decomposer, your objective is to divide the given task into high level subtasks.
        You have been provided with the following objective:
        {command}

        Please format the subtasks as a python list with 3 or less tasks, each tasks contains less than 10 words, as demonstrated below, output nothing else:
        ["Subtask 1", "Subtask 2", "Subtask 3"]
        
        Each subtask should be concise, concrete, and achievable.
        Ensure that the task plan is created without asking any questions.
        Be specific and clear.
        """
        response = self.model.create(
                messages=[{"role": "system", "content": task_decomposer_template}],
                systems=[],
                tool_schemas= None,
            ).choices[0].message

        # parse the response to get the subtasks

        subtasks = eval(response.content)

        # for subtask in subtasks:
        #   self.memory_manager.create_task(subtask)
        logger.info(f"[{self.persona.name}] Subtasks: {subtasks}")
        return str(subtasks) 
