from isek.agent.isek.agent import Agent
from isek.models.openai import OpenAIModel
from isek.models.base import SimpleMessage
import dotenv
dotenv.load_dotenv()

agent = Agent(
    name="My Agent",
    model=OpenAIModel(model_id="gpt-4o-mini"),
    description="A helpful assistant",
    instructions=["Be polite", "Provide accurate information"],
    success_criteria="User gets a helpful response",
    debug_mode=True
)

response = agent.run("hello")
# print(response)
