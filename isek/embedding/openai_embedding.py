import os
from typing import Optional, List  # Changed to List for Python 3.9+ type hinting

from openai import OpenAI  # Assuming this is the official openai package

from isek.embedding.abstract_embedding import AbstractEmbedding
from isek.util.logger import logger  # Assuming logger is configured
from isek.utils.tools import split_list  # Assuming this utility function exists


class OpenAIEmbedding(AbstractEmbedding):
    """
    An implementation of :class:`~isek.embedding.abstract_embedding.AbstractEmbedding`
    that uses OpenAI's API to generate text embeddings.

    This class connects to the OpenAI API (or a compatible endpoint) to
    convert text data into numerical vector representations using specified
    OpenAI embedding models.
    """

    def __init__(
        self,
        dim: Optional[int] = None,  # Defaulting dim as it might be model-specific
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initializes the OpenAIEmbedding client.

        :param dim: The expected dimensionality of the embeddings. For some OpenAI models,
                    this can be specified (e.g., text-embedding-3-small). If `None`,
                    the model's default dimensionality will be used. The `dim` parameter
                    in the `AbstractEmbedding` superclass is initialized with this value.
        :type dim: typing.Optional[int]
        :param model_name: The name of the OpenAI embedding model to use
                           (e.g., "text-embedding-3-small", "text-embedding-ada-002").
                           Defaults to "text-embedding-3-small".
        :type model_name: str
        :param api_key: The OpenAI API key. If not provided, it will attempt to use
                        the `OPENAI_API_KEY` environment variable.
        :type api_key: typing.Optional[str]
        :param base_url: The base URL for the OpenAI API. Useful for proxying requests
                         or using compatible non-OpenAI endpoints. If `None`, the
                         default OpenAI API URL is used.
        :type base_url: typing.Optional[str]
        """
        super().__init__(dim)
        self.model_name: str = model_name
        self.client: OpenAI = OpenAI(
            base_url=base_url,
            api_key=api_key
            or os.environ.get(
                "OPENAI_API_KEY"
            ),  # Common practice to fallback to env var
        )
        logger.info(
            f"OpenAIEmbedding initialized with model: {self.model_name}, dim: {self.dim}"
        )

    def embedding(self, data_list: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text strings using the configured OpenAI model.

        The input data is split into chunks to respect API limits (e.g., batch size).
        The `dim` parameter passed during initialization might be used by some models
        to specify the output dimensionality.

        :param data_list: A list of text strings to be embedded.
        :type data_list: typing.List[str]
        :return: A list of embedding vectors. Each inner list is a list of floats
                 representing the embedding for the corresponding input string.
        :rtype: typing.List[typing.List[float]]
        :raises openai.APIError: If the OpenAI API returns an error.
        """
        if not data_list:
            return []

        # The OpenAI API documentation suggests a max batch size for embeddings,
        # e.g., 2048 for text-embedding-ada-002. `split_list(data_list, 16)` seems
        # to use a very small batch size (16). This might be intentional or
        # could be increased for efficiency if the model and API allow.
        # Let's assume `split_list` handles this appropriately.
        # For models like text-embedding-3-small, the `dimensions` parameter can be passed.
        embedding_params = {"input": [], "model": self.model_name}
        if (
            self.dim is not None and "text-embedding-3" in self.model_name
        ):  # Check if model supports dimensions
            embedding_params["dimensions"] = self.dim

        all_embeddings: List[List[float]] = []
        # Assuming split_list splits `data_list` into sub-lists for batching.
        # The original `split_list(data_list, 16)` suggests a batch size of 16.
        # OpenAI's Python library handles batching internally for some operations,
        # but for embeddings, you typically pass a list of strings.
        # The API limit on the number of input strings per request is 2048.
        # Let's adjust `split_list` or the batching logic if `16` is too small.
        # For simplicity, using the provided split_list and batch size.
        data_chunks: List[List[str]] = split_list(
            data_list, 2048
        )  # Max batch size for most models is 2048 inputs

        for chunk in data_chunks:
            if not chunk:  # Skip empty chunks
                continue
            try:
                current_params = embedding_params.copy()
                current_params["input"] = chunk

                logger.debug(
                    f"Requesting embeddings for {len(chunk)} texts with model {self.model_name} "
                    f"{f'and dim {self.dim}' if 'dimensions' in current_params else ''}."
                )

                # The `client.embeddings.create` method takes `input`, `model`, and optionally `dimensions`.
                response = self.client.embeddings.create(**current_params)

                # Process the response
                # Each item in response.data is an `Embedding` object which has an `embedding` attribute (list of floats)
                chunk_embeddings: List[List[float]] = [
                    item.embedding for item in response.data
                ]
                all_embeddings.extend(chunk_embeddings)

                logger.debug(
                    f"Received {len(chunk_embeddings)} embeddings for the current chunk."
                )

            except Exception as e:  # Catching general OpenAI API errors or other issues
                logger.error(
                    f"Error during OpenAI embedding generation for a chunk: {e}"
                )
                # Decide on error handling: re-raise, return partial, or return empty for error
                # For now, let's log and continue if possible, or re-raise if fatal.
                # If one chunk fails, it might be desirable to stop and report.
                raise  # Re-raise the exception to signal failure

        if len(all_embeddings) != len(data_list):
            logger.warning(
                f"Mismatch in number of embeddings generated ({len(all_embeddings)}) "
                f"and number of input texts ({len(data_list)})."
            )
            # This might indicate an issue with batch processing or API response.

        return all_embeddings
