import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=True)

api_key = os.getenv("NAVIGATOR_TOOLKIT_API_KEY")


# Testing if ENV FIle worked (ignore this)
if __name__ == "__main__":
    if api_key:

        print(f"Key found.")
        print(f"Key preview: {api_key[:5]}...{api_key[-4:]}")
        print(f"Key length: {len(api_key)} characters")
    else:
        print("FAILEd: 'NAVIGATOR_TOOLKIT_API_KEY' not found in .env or environment.")

        print(f"Looking for .env in: {os.getcwd()}")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.ai.it.ufl.edu/v1"
)