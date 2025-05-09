import datetime
import uuid
from typing import Dict, List, Any, Optional, Callable, TypeVar, Union
from isek.util.logger import logger # Assuming logger has a standard logging interface
import json

T = TypeVar('T')

class AgentMemory:
    """
    Manages the complete cognitive state of an agent.

    This includes working memory for recent interactions, a long-term knowledge
    store, a queue for scheduled tasks, and internal state variables that
    track the agent's status and goals.
    """
    
    def __init__(self):
        """
        Initializes the agent's memory systems.

        Sets up the core components:
        
        - ``state_variables``: A dictionary to store key-value pairs representing the agent's current state.
        - ``working_memory``: A list to store recent interactions or thoughts.
        - ``task_queue``: A dictionary to manage tasks, their status, and priority.
        - ``knowledge_store``: A dictionary to store learned information or facts.
        """
        self.logger = logger # Assuming logger is an instance of a logging object
        
        # Core memory components
        self.state_variables: Dict[str, Any] = {"is_registered": False, "goal": None}
        self.working_memory: List[str] = []
        self.task_queue: Dict[str, Dict[str, Any]] = {} # task_id -> task_details
        self.knowledge_store: Dict[str, Dict[str, str]] = {} # knowledge_id -> knowledge_details
    
    def log_operation(self, operation_name: str, details: str) -> None:
        """
        Logs a memory operation using the configured logger.

        :param operation_name: The name of the memory operation performed (e.g., "set_state_variable").
        :type operation_name: str
        :param details: Specific details about the operation (e.g., variable name and value).
        :type details: str
        """
        if self.logger:
            self.logger.debug(f"Memory: {operation_name} - {details}")
    
    def generate_timestamp(self) -> str:
        """
        Generates a current timestamp string.

        The format is "YYYY-MM-DD HH:MM:SS".

        :return: The current timestamp as a formatted string.
        :rtype: str
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_unique_id(self) -> str:
        """
        Generates a short unique ID.

        The ID is the first 8 characters of a UUID version 4.

        :return: A unique 8-character string identifier.
        :rtype: str
        """
        return str(uuid.uuid4())[:8]
    
    # --- State variable methods ---
    def set_state_variable(self, variable_name: str, value: Any) -> str:
        """
        Sets or updates a state variable in the agent's memory.

        :param variable_name: The name of the state variable to set or update.
        :type variable_name: str
        :param value: The new value for the state variable.
        :type value: typing.Any
        :return: A confirmation message indicating the variable was set.
        :rtype: str
        """
        self.state_variables[variable_name] = value
        self.log_operation("set_state_variable", f"{variable_name}: {value}")
        return f"State variable '{variable_name}' set to '{value}'"
    
    def get_state_variable(self, variable_name: str, default: T = None) -> Union[Any, T]:
        """
        Retrieves the value of a state variable.

        :param variable_name: The name of the state variable to retrieve.
        :type variable_name: str
        :param default: The default value to return if the variable_name is not found.
                        Defaults to None.
        :type default: T
        :return: The value of the state variable, or the default value if not found.
        :rtype: typing.Union[typing.Any, T]
        """
        return self.state_variables.get(variable_name, default)
    
    def get_all_state_variables(self) -> Dict[str, Any]:
        """
        Retrieves all current state variables and their values.

        :return: A dictionary containing all state variables.
        :rtype: typing.Dict[str, typing.Any]
        """
        self.log_operation("get_all_state_variables", f"count: {len(self.state_variables)}")
        return self.state_variables.copy()
    
    # --- Working memory methods ---
    def store_memory_item(self, content: str) -> str:
        """
        Adds an item to the agent's working memory.

        Working memory typically stores recent interactions or temporary thoughts.

        :param content: The string content to store in working memory.
        :type content: str
        :return: A confirmation message.
        :rtype: str
        """
        self.working_memory.append(content)
        self.log_operation("store_memory_item", f"item: {content[:50]}...") # Log truncated content
        return f"Memory item stored"
    
    def get_recent_memory_items(self, count: int = 4) -> List[str]:
        """
        Retrieves the most recent items from working memory.

        :param count: The maximum number of recent items to retrieve. Defaults to 4.
        :type count: int
        :return: A list of the most recent memory items, up to `count`.
        :rtype: typing.List[str]
        """
        if len(self.working_memory) > count:
            return self.working_memory[-count:]
        return self.working_memory.copy() # Return a copy to prevent external modification
    
    # --- Task queue methods ---
    def create_task(self, task_description: str, priority: int = 1) -> str:
        """
        Creates a new task and adds it to the task queue.

        Each task is assigned a unique ID and includes its description,
        creation timestamp, completion status, and priority.

        :param task_description: A description of the task to be performed.
        :type task_description: str
        :param priority: The priority of the task (e.g., higher number for higher priority).
                         Defaults to 1.
        :type priority: int
        :return: The unique ID of the created task.
        :rtype: str
        """
        task_id = self.generate_unique_id()
        self.task_queue[task_id] = {
            "description": task_description,
            "created_at": self.generate_timestamp(),
            "completed": False,
            "priority": priority
        }
        self.log_operation("create_task", f"id: {task_id}, task: {task_description}")
        return task_id
    
    def mark_task_completed(self, task_id: str) -> bool:
        """
        Marks a specified task in the queue as completed.

        Sets the 'completed' flag to True and records the completion timestamp.

        :param task_id: The ID of the task to mark as completed.
        :type task_id: str
        :return: `True` if the task was found and marked completed, `False` otherwise.
        :rtype: bool
        """
        if task_id in self.task_queue:
            self.task_queue[task_id]["completed"] = True
            self.task_queue[task_id]["completed_at"] = self.generate_timestamp()
            self.log_operation("mark_task_completed", f"id: {task_id}")
            return True
        self.log_operation("mark_task_completed", f"Task ID not found: {task_id}")
        return False
    
    def get_pending_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves all tasks that are currently not marked as completed.

        :return: A dictionary of pending tasks, where keys are task IDs and
                 values are dictionaries of task details.
        :rtype: typing.Dict[str, typing.Dict[str, typing.Any]]
        """
        pending = {
            task_id: task_info for task_id, task_info in self.task_queue.items() 
            if not task_info.get("completed", False)
        }
        self.log_operation("get_pending_tasks", f"count: {len(pending)}")
        return pending
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves all tasks from the queue, both pending and completed.

        :return: A dictionary of all tasks, where keys are task IDs and
                 values are dictionaries of task details.
        :rtype: typing.Dict[str, typing.Dict[str, typing.Any]]
        """
        return self.task_queue.copy() # Return a copy
    
    # --- Knowledge store methods ---
    def store_knowledge(self, topic: str, content: str) -> str:
        """
        Stores a piece of knowledge in the knowledge store.

        Each knowledge item is associated with a topic and includes the content
        and a creation timestamp.

        :param topic: The topic or title for the knowledge item.
        :type topic: str
        :param content: The actual content of the knowledge item.
        :type content: str
        :return: The unique ID of the stored knowledge item.
        :rtype: str
        """
        knowledge_id = self.generate_unique_id()
        self.knowledge_store[knowledge_id] = {
            "topic": topic,
            "content": content,
            "created_at": self.generate_timestamp()
        }
        self.log_operation("store_knowledge", f"id: {knowledge_id}, topic: {topic}")
        return knowledge_id
    
    def retrieve_knowledge(self, topic: str) -> Optional[str]:
        """
        Retrieves knowledge content associated with a specific topic.

        Searches the existing knowledge store for an item matching the given topic.

        .. note::
            The original docstring mentioned a `generator_func` parameter,
            which is not present in the method signature. This version reflects
            the current signature.

        :param topic: The topic to retrieve knowledge about.
        :type topic: str
        :return: The content of the knowledge item if found, otherwise `None`.
        :rtype: typing.Optional[str]
        """
        # Search existing knowledge
        for k_id, item in self.knowledge_store.items(): # k_id is not used here, could be `_`
            if item["topic"] == topic:
                self.log_operation("retrieve_knowledge", f"found - topic: {topic}")
                return item["content"]
        
        self.log_operation("retrieve_knowledge", f"not found - topic: {topic}")
        return None
    
    def get_all_knowledge_topics(self) -> List[str]:
        """
        Retrieves a list of all topics currently in the knowledge store.

        :return: A list of all knowledge topics.
        :rtype: typing.List[str]
        """
        return [item["topic"] for item in self.knowledge_store.values()]
    
    # --- Interaction Methods ---
    def state_interaction(self, action: str, title: str, value: Any) -> str:
        """
        Manages interactions with the agent's state variables.

        This method allows for updating, inserting (which is equivalent to updating),
        or fetching the agent's state.

        :param action: The action to perform: "update", "insert", or "fetch".
        :type action: str
        :param title: The name (key) of the state variable.
        :type title: str
        :param value: The value to set for the state variable (used for "update" and "insert").
                      Ignored for "fetch".
        :type value: typing.Any
        :return: A string confirming the action taken or providing the fetched state.
        :rtype: str
        """
        if action == "update":
            self.set_state_variable(title, value)
            return f"State updated with '{title}' as '{value}'"
        elif action == "insert": # Functionally same as update for a dict
            self.set_state_variable(title, value)
            return f"State inserted with '{title}' as '{value}'"
        elif action == "fetch":
            return f"Your state is {str(self.get_all_state_variables())}"
        else:
            self.log_operation("state_interaction", f"Unknown action: {action}")
            return "No action is taken for state interaction due to unknown action."
        
    def knowledge_interaction(self, action: str, content: str) -> str:
        """
        Manages interactions with the agent's knowledge store.

        Allows querying for existing knowledge or inserting new knowledge.

        .. todo::
            For "insert" action, the `topic` should ideally be extracted from the `content`
            or provided as a separate parameter, rather than using `content` for both.

        :param action: The action to perform: "query" or "insert".
        :type action: str
        :param content: For "query", this is the topic to search for.
                        For "insert", this is the content to store (also used as topic currently).
        :type content: str
        :return: A string confirming the action or the result of the query.
        :rtype: str
        """
        if action == "query":
           retrieved_knowledge = self.retrieve_knowledge(content) # `content` is treated as topic
           if retrieved_knowledge:
               return f"Knowledge found for '{content}': {retrieved_knowledge}"
           else:
               return f"No knowledge found for topic: '{content}'"
        elif action == "insert":
            # TODO: topic should be extracted from the content
            knowledge_id = self.store_knowledge(topic=content, content=content) # Using content as topic
            return f"Knowledge '{content[:50]}...' inserted with ID {knowledge_id} (topic: '{content[:30]}...')"
        else:
            self.log_operation("knowledge_interaction", f"Unknown action: {action}")
            return "No action is taken for knowledge interaction due to unknown action."
        
    def scheduling(self, option: str, id: Optional[str] = None, task: Optional[str] = None, finished: bool = False) -> str:
        """
        Manages the agent's task schedule.

        Allows adding new tasks, marking tasks as complete, or fetching all tasks.

        .. warning::
            The `finished` parameter is present in the signature but not currently used.
            In the "complete" option, `task_id` is used in the return message but refers to
            the local `id` parameter.

        :param option: The scheduling action: "add", "complete", or "fetch".
        :type option: str
        :param id: The ID of the task (used for "complete"). Defaults to None.
        :type id: typing.Optional[str]
        :param task: The description of the task (used for "add"). Defaults to None.
        :type task: typing.Optional[str]
        :param finished: This parameter is currently unused. Defaults to False.
        :type finished: bool
        :return: A string confirming the action or providing the fetched schedule.
        :rtype: str
        """
        if option == "add":
            if task is None:
                return "Task description cannot be None for 'add' option."
            task_id_created = self.create_task(task)
            return f"Task '{task}' added to your schedule. Task ID is {task_id_created}."
        
        elif option == "complete":
            if id is None:
                return "Task ID cannot be None for 'complete' option."
            if self.mark_task_completed(id):
                # The original code used 'task_id' here, which was not defined in this scope.
                # It should probably refer to 'id' or fetch the task description.
                # For now, let's use 'id' as the identifier.
                task_description = self.task_queue.get(id, {}).get("description", "Unknown task")
                return f"Task '{task_description}' (ID: {id}) marked as completed in your schedule."
            else:
                return f"Failed to mark task with ID '{id}' as completed (task not found)."
        
        elif option == "fetch":
            return f"Your schedule is {str(self.get_all_tasks())}"
        else:
            self.log_operation("scheduling", f"Unknown option: {option}")
            return "No action is taken for scheduling due to unknown option."