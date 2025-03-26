import os
from isek.agent.distributed_agent import DistributedAgent
from isek.llm.openai_model import OpenAIModel
from isek.node.isek_center_registry import IsekCenterRegistry
from dotenv import load_dotenv


def main():
    load_dotenv()
    model = OpenAIModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    registry = IsekCenterRegistry()
    Infy_agent = DistributedAgent(model=model)
    Infy_agent.build(daemon=True)
    Infy_agent.run_cli()

if __name__ == "__main__":
    main()
    
