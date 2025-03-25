from isek.llm.openai_model import OpenAIModel
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    model = OpenAIModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    text = "Do androids dream of electric sheep?"
    response = model.generate_text(text)
    print(f"Bot: {response}")

if __name__ == "__main__": 
    main()
