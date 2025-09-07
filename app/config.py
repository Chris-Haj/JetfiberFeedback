import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB settings - just use the URL directly
    MONGODB_URL = os.getenv("MONGODB_URL")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "feedbacks")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "customer_feedback")
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("openai_key")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Validate required settings
    if not OPENAI_API_KEY:
        raise ValueError("openai_key is required in .env file")
    if not MONGODB_URL:
        raise ValueError("MONGODB_URL is required in .env file")

settings = Settings()