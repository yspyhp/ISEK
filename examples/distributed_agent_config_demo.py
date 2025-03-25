import os
import time
from isek.isek_config import IsekConfig
from isek.llm import OpenAIModel
from dotenv import load_dotenv


def main():
    load_dotenv()
    model = OpenAIModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    sylana_config = IsekConfig("examples/sylana/sylana_config.yaml")
    sylana_agent = sylana_config.load_agent()
    sylana_agent.model = model
    sylana_agent.build(daemon=True)

    dobby_config = IsekConfig("examples/dobby/dobby_config.yaml")
    dobby_agent = dobby_config.load_agent()
    sylana_agent.model = model
    dobby_agent.build(daemon=True)

    time.sleep(5)
    hello = f"Hello! My name is {sylana_agent.persona.name}"
    print(f"{sylana_agent.persona.name}: {hello}")

    response = sylana_agent.send_message(dobby_agent.node_id, hello)
    print(f"{dobby_agent.persona.name}: {response}")


if __name__ == '__main__':
    main()
