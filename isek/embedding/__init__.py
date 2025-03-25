from .openai_embedding import OpenAIEmbedding

__all__ = [
    "OpenAIEmbedding",
    "embeddings"
]


embeddings = {
    "openai": OpenAIEmbedding
}
