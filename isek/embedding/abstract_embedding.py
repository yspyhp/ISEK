from abc import ABC, abstractmethod
from typing import Optional, List # Changed to List for Python 3.9+ type hinting


class AbstractEmbedding(ABC):
    """
    Abstract base class for text embedding models.

    This class defines the common interface for various embedding implementations,
    ensuring they can be used interchangeably where an embedding mechanism is required.
    Subclasses must implement the `embedding` method.
    """

    def __init__(self, dim: Optional[int] = None):
        """
        Initializes the AbstractEmbedding model.

        :param dim: The dimensionality of the embedding vectors produced by this model.
                    This is optional and might not be known or fixed for all models at
                    initialization. Defaults to None.
        :type dim: typing.Optional[int]
        """
        self.dim: Optional[int] = dim

    def embedding_one(self, data: str) -> List[float]:
        """
        Generates an embedding for a single string of text.

        This is a convenience method that wraps the :meth:`embedding` method
        for a single input.

        :param data: The single string of text to embed.
        :type data: str
        :return: A list of floats representing the embedding vector for the input text.
        :rtype: typing.List[float]
        :raises IndexError: If the underlying :meth:`embedding` method returns an empty list.
        """
        embeddings = self.embedding([data])
        if not embeddings:
            # This case should ideally not happen if embedding() correctly processes a single item list
            raise ValueError("Embedding method returned an empty list for a single input.")
        return embeddings[0]

    @abstractmethod
    def embedding(self, datas: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text strings.

        This method must be implemented by concrete subclasses to perform
        the actual embedding generation.

        :param datas: A list of text strings to be embedded.
        :type datas: typing.List[str]
        :return: A list of embedding vectors. Each inner list is a list of floats
                 representing the embedding for the corresponding input string.
        :rtype: typing.List[typing.List[float]]
        """
        pass