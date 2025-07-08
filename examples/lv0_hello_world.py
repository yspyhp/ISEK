from isek.agent.isek_agent import IsekAgent
from isek.models.openai.openai import OpenAIModel

agent = IsekAgent(name='MyAgent', model=OpenAIModel())
agent.print_response('Hello, world!')