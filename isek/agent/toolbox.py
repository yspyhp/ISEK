import json
import inspect
from isek.agent.persona import Persona
from isek.util.logger import logger
from typing import List, Dict, Callable, Any, Optional, Union

class ToolBox:
    def __init__(self, persona: Persona = None) -> None:
        """
        Initialize a tool manager for an agent.
        
        Args:
        """
        self.logger = logger
        self.persona = persona
        # Tool containers
        self.all_tools: Dict[str, Callable] = {}
        
        # Tool metadata
        self.tool_descriptions: Dict[str, str] = {}
        self.tool_schemas: Dict[str, Dict] = {}
    
    def _log(self, message: str) -> None:
        """Log a message if logger is available."""
        if self.logger:
            self.logger.info(message)
    
    def register_tool(self, func: Callable) -> None:
        """
        Register a new tool function.
        
        Args:
            func: The function to register as a tool
            category: Tool category ("action" or "reasoning")
        """
        name = func.__name__
        
        # Store the function in appropriate containers
        self.all_tools[name] = func
        
        
        # Generate and store the schema
        self.tool_schemas[name] = self._function_to_schema(func)
        
        # Store metadata
        self.tool_descriptions[name] = (func.__doc__ or "").strip()
        
        self._log(f"[{self.persona.name}] Tool: added - {name} ")
    
    def register_tools(self, tools: List[Callable]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.register_tool(tool)
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool function by name."""
        return self.all_tools.get(name)
    
    def get_tool_names(self) -> List[str]:
        """Get a list of tool names, optionally filtered by category."""
        return list(self.all_tools.keys())
    
    def get_tool_schemas(self, category: Optional[str] = None) -> List[Dict]:
        """Get tool schemas, optionally filtered by category."""
        return [self.tool_schemas[name] for name in self.all_tools]
    
    def execute_tool_call(self, tool_call, **extra_kwargs) -> str:
        """
        Execute a tool call based on LLM response.
        
        Args:
            tool_call: Tool call object from LLM response
            extra_kwargs: Additional kwargs to pass to the tool function
        
        Returns:
            str: Result of the tool execution
        """
        name = tool_call.function.name
        
        if name not in self.all_tools:
            error_msg = f"Tool {name} not found"
            self._log(f"Tool: error - {error_msg}")
            return error_msg
        
        try:
            func = self.all_tools[name]
            args = json.loads(tool_call.function.arguments)
            
            # Merge any extra kwargs
            for key, value in extra_kwargs.items():
                args[key] = value
                
            self._log(f"[{self.persona.name}][Tool] executing {name}({args})")
            result = func(**args)
            return result
        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            self._log(f"[{self.persona.name}][Tool] error - {error_msg}")
            return error_msg
    
    def _function_to_schema(self, func: Callable) -> Dict:
        """
        Convert a function to a tool schema for LLM API.
        
        Args:
            func: The function to convert
        
        Returns:
            dict: Schema for the function
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }

        try:
            signature = inspect.signature(func)
        except ValueError as e:
            raise ValueError(
                f"Failed to get signature for function {func.__name__}: {str(e)}"
            )

        parameters = {}
        for param in signature.parameters.values():
            try:
                param_type = type_map.get(param.annotation, "string")
            except KeyError as e:
                raise KeyError(
                    f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
                )
            parameters[param.name] = {"type": param_type}

        required = [
            param.name
            for param in signature.parameters.values()
            if param.default == inspect._empty
        ]

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": (func.__doc__ or "").strip(),
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                },
            },
        }
