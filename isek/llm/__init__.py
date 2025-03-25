from .openai_model import OpenAIModel

__all__ = [
    "OpenAIModel",
    "llms"
]


llms = {
    "openai": OpenAIModel
}
