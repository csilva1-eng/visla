import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=True)

api_key = os.getenv("NAVIGATOR_TOOLKIT_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.ai.it.ufl.edu/v1"
)