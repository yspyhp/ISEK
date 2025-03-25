"""encoding=utf-8"""

import os
from typing import Optional

from openai import OpenAI

from isek.embedding.abstract_embedding import AbstractEmbedding
from isek.util.logger import logger
from isek.util.tools import split_list


class OpenAIEmbedding(AbstractEmbedding):
    """
    OpenAIEmbedding
    """

    def __init__(
            self,
            dim: Optional[int],
            model_name: Optional[str] = "text-embedding-3-small",
            api_key: Optional[str] = None,
            base_url: Optional[str] = None
    ):
        super().__init__(dim)
        self.model_name = model_name
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def embedding(self, datas: list[str]) -> list[list[float]]:
        data_array = split_list(datas, 16)
        all_results = []
        for sub_datas in data_array:
            result = self.client.embeddings.create(input=sub_datas, model=self.model_name)
            all_results.extend([r.embedding for r in result.data])
        return all_results
