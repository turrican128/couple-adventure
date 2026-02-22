import os
from dotenv import load_dotenv

load_dotenv()


def load_config() -> dict:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    fal_key = os.getenv("FAL_KEY")

    if not anthropic_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
    if not fal_key:
        raise ValueError("FAL_KEY is not set. Add it to your .env file.")

    return {
        "anthropic_api_key": anthropic_key,
        "fal_key": fal_key,
    }
