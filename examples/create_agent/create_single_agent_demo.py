import sys
import os
from isek.agent.single_agent import SingleAgent
from isek.agent.persona import Persona
from isek.llm.openai_model import OpenAIModel
from dotenv import load_dotenv


def fast_create():
    load_dotenv()
    return SingleAgent()


def statement_llm_create():
    load_dotenv()
    model = OpenAIModel(
        model_name = os.environ["OPENAI_MODEL_NAME"],
        base_url = os.environ["OPENAI_BASE_URL"],
        api_key = os.environ["OPENAI_API_KEY"]
    )
    return SingleAgent(model=model)


def custom_create():
    # create your persona
    persona_desc = {
        "name": "Custom Agent",
        "bio": "An agent for testing",
        "lore": "Be responsible for helping users conduct agent testing",
        "knowledge": "",
        "routine": ""
    }
    persona = Persona.from_json(persona_desc)
    # create your llm
    load_dotenv()
    model = OpenAIModel(
        model_name=os.environ["OPENAI_MODEL_NAME"],
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"]
    )
    return SingleAgent(persona=persona, model=model)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fast_create"
    if mode == "statement_llm_create":
        agent = statement_llm_create()
    elif mode == "custom_create":
        agent = custom_create()
    else:
        agent = fast_create()
    agent.run("Hello! What is your name?")
