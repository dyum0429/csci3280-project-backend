import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_PATH")  # Path to Google Cloud JSON key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")