import datetime
import uuid
from typing import Dict, List, Any, Optional, Callable, TypeVar, Union
from isek.util.logger import logger
import json

T = TypeVar('T')

class AgentMemory:
    """
    Manages the complete cognitive state of an agent, including working memory,
    long-term knowledge, scheduled tasks, and internal state variables.
    """
    
    def __init__(self):
        """
        Initialize the agent's memory systems.
        
        Args:
        """
        self.logger = logger
        
        # Core memory components
        self.state_variables: Dict[str, Any] = {"is_registered": False, "goal": None}
        self.working_memory: List[str] = []
        self.task_queue: Dict[str, Dict[str, Any]] = {}
        self.knowledge_store: Dict[str, Dict[str, str]] = {}
    
    def log_operation(self, operation_name: str, details: str) -> None:
        """Log a memory operation if a logger is available."""
        if self.logger:
            self.logger.debug(f"Memory: {operation_name} - {details}")
    
    def generate_timestamp(self) -> str:
        """Generate a current timestamp string."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_unique_id(self) -> str:
        """Generate a unique ID for memory items."""
        return str(uuid.uuid4())[:8]
    
    # State variable methods
    def set_state_variable(self, variable_name: str, value: Any) -> str:
        """
        Set or update a state variable.
        
        Args:
            variable_name: Name of the state variable to update
            value: New value for the state variable
            
        Returns:
            str: Confirmation message
        """
        self.state_variables[variable_name] = value
        self.log_operation("set_state_variable", f"{variable_name}: {value}")
        return f"State variable '{variable_name}' set to '{value}'"
    
    def get_state_variable(self, variable_name: str, default: T = None) -> Union[Any, T]:
        """
        Get a state variable value.
        
        Args:
            variable_name: Name of the state variable to retrieve
            default: Default value if variable doesn't exist
            
        Returns:
            The variable value or default if not found
        """
        return self.state_variables.get(variable_name, default)
    
    def get_all_state_variables(self) -> Dict[str, Any]:
        """
        Get all state variables.
        
        Returns:
            Dict: All state variables and their values
        """
        self.log_operation("get_all_state_variables", f"count: {len(self.state_variables)}")
        return self.state_variables.copy()
    
    # Working memory methods
    def store_memory_item(self, content: str) -> str:
        """
        Add an item to working memory.
        
        Args:
            content: Content to store in working memory
            
        Returns:
            str: Confirmation message
        """
        self.working_memory.append(content)
        self.log_operation("store_memory_item", f"item: {content[:50]}...")
        return f"Memory item stored"
    
    def get_recent_memory_items(self, count: int = 4) -> List[str]:
        """
        Get the most recent items from working memory.
        
        Args:
            count: Maximum number of items to retrieve
            
        Returns:
            List[str]: The most recent memory items
        """
        if len(self.working_memory) > count:
            return self.working_memory[-count:]
        return self.working_memory.copy()
    
    # Task queue methods
    def create_task(self, task_description: str, priority: int = 1) -> str:
        """
        Create a new task in the task queue.
        
        Args:
            task_description: Description of the task
            priority: Task priority (higher number = higher priority)
            
        Returns:
            str: ID of the created task
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
        Mark a task as completed.
        
        Args:
            task_id: ID of the task to mark as completed
            
        Returns:
            bool: True if successful, False if task not found
        """
        if task_id in self.task_queue:
            self.task_queue[task_id]["completed"] = True
            self.task_queue[task_id]["completed_at"] = self.generate_timestamp()
            self.log_operation("mark_task_completed", f"id: {task_id}")
            return True
        return False
    
    def get_pending_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all pending (incomplete) tasks.
        
        Returns:
            Dict: Dictionary of pending tasks with their IDs as keys
        """
        pending = {
            task_id: task_info for task_id, task_info in self.task_queue.items() 
            if not task_info.get("completed", False)
        }
        self.log_operation("get_pending_tasks", f"count: {len(pending)}")
        return pending
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tasks, both pending and completed.
        
        Returns:
            Dict: Dictionary of all tasks with their IDs as keys
        """
        return self.task_queue.copy()
    
    # Knowledge store methods
    def store_knowledge(self, topic: str, content: str) -> str:
        """
        Store a knowledge item.
        
        Args:
            topic: Topic or title for the knowledge item
            content: Content of the knowledge item
            
        Returns:
            str: ID of the stored knowledge item
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
        Retrieve knowledge on a specific topic, generating it if not found.
        
        Args:
            topic: Topic to retrieve knowledge about
            generator_func: Optional function to generate knowledge if not found
            
        Returns:
            str: The knowledge content or None if not found and couldn't be generated
        """
        # Search existing knowledge
        for k_id, item in self.knowledge_store.items():
            if item["topic"] == topic:
                self.log_operation("retrieve_knowledge", f"found - topic: {topic}")
                return item["content"]
        
        self.log_operation("retrieve_knowledge", f"not found - topic: {topic}")
        return None
    
    def get_all_knowledge_topics(self) -> List[str]:
        """
        Get all knowledge topics.
        
        Returns:
            List[str]: List of all knowledge topics
        """
        return [item["topic"] for item in self.knowledge_store.values()]
    
    def state_interaction(self, action, title, value):
        """
        This is state manager. Call this function to update or add new state or milestone.
        """
        if action == "update":
            self.set_state_variable(title, value)
            return f"State updated with {title} as {value}"
        elif action == "insert":
            self.set_state_variable(title, value)
            return f"State insert with {title} as {value}"
        elif action == "fetch":
            return f"Your state is {str(self.get_all_state_variables())}"
        else:
            return "No action is taken"
        
    def knowledge_interaction(self, action, content):
        """
        This is knowledge tool. Call this function to get information.
        """
        if action == "query":
           self.retrieve_knowledge(content)
        elif action == "insert":
            # TODO: topic should be extracted from the content
            self.store_knowledge(content, content)
            return f"Knowledge {content} inserted"
        else:
            return "No action is taken"

        
    def scheduling(self, option, id = None, task=None, finished=False):
        """
        This is scheduling manager. Call this function to add new task to your schedule.
        """
        if option == "add":
            task_id = self.create_task(task)
            return f"Task {task} is added to your schedule, task id is {task_id}"
        
        elif option == "complete":
            self.mark_task_completed(id)
            return f"Task {task} is updated in your schedule, task id is {task_id}"
        
        elif option == "fetch":
            return f"Your schedule is {str(self.get_all_tasks())}"
        else:
            return "No action is taken"