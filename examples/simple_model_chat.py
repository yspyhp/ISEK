from isek.llm.openai_model import OpenAIModel
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    model = OpenAIModel(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    text = "Do androids dream of electric sheep?"
    response = model.generate_text(text)
    print(f"Bot: {response}")

if __name__ == "__main__": 
    main()
