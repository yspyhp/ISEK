"""encoding=utf-8"""

import time
import os
import json
from isek.util.logger import logger
from isek.llm.abstract_model import AbstractModel
from isek.util.tools import function_to_schema, load_json_from_chat_response
from typing import Union, List, Optional, Dict, Callable
from openai import OpenAI





class OpenAIModel(AbstractModel):
    """
    OpenAIModel
    """

    def __init__(
            self,
            model_name: Optional[str] = "gpt-4o-mini",
            api_key: Optional[str] = None,
            base_url: Optional[str] = None
    ):
        super().__init__()
        self.model_name = model_name or "gpt-4o-mini"
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def generate_json(self, prompt, system_messages=None, retry=3, check_json_def=None):
        for i in range(retry):
            try:
                response = self.create(messages=[{'role': 'user', 'content': prompt}],
                                       systems=system_messages)
                response_content = response.choices[0].message.content
                try:
                    json_result = json.loads(response_content)
                except:
                    json_result = load_json_from_chat_response(response_content)
                if check_json_def:
                    check_json_def(json_result)
                return json_result
            except:
                logger.exception(f"Request model[{self.model_name}] generate_json call fail {i} times")
        raise RuntimeError("call ernie bot error over 3 times")

    def generate_text(self, prompt, system_messages=None, retry=3):
        for i in range(retry):
            try:
                response = self.create(messages=[{'role': 'user', 'content': prompt}], systems=system_messages)
                return response.choices[0].message.content
            except:
                logger.exception(f"Request model[{self.model_name}] generate_text call fail {i} times")
        raise RuntimeError("call ernie bot error over 3 times")

    def create(
            self,
            messages: Union[List[Dict]],
            systems: Optional[List[Dict]],
            tool_schemas: List[Dict] = None
    ):
        try:
            messages = (systems if systems else []) + messages

            logger.debug(f"Request model[{self.model_name}] messages: {messages}")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tool_schemas
            )
            cost_seconds = time.time() - start_time
            logger.debug(f"Request model[{self.model_name}] time taken[{cost_seconds:.2f}s] response[{response}]")
            return response
        except Exception as e:
            logger.exception(f"Request model[{self.model_name}] error.")
            raise e
