import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


SYSTEM_PROMPT = (
    "You are a helpful travel planning assistant. "
    "Help users create practical itineraries, suggest places to visit, food, transport, "
    "and budget-friendly options. "
    "When relevant, organize the answer by day, estimate costs in USD, "
    "highlight assumptions clearly, and keep the plan realistic and concise."
)


def _load_openai_config() -> tuple[str, str]:
    load_dotenv()
    return (
        os.getenv("OPENAI_API_KEY", ""),
        os.getenv("DEFAULT_MODEL", "gpt-4o"),
    )


def _validate_api_key(api_key: str) -> None:
    if not api_key or "your_openai_api_key_here" in api_key:
        raise ValueError("OPENAI_API_KEY is missing or still uses the placeholder value.")


def run_chatbot(prompt: str) -> Dict[str, Any]:
    api_key, model_name = _load_openai_config()
    _validate_api_key(api_key)

    provider = OpenAIProvider(model_name=model_name, api_key=api_key)
    logger.log_event("CHATBOT_START", {"model": model_name, "prompt": prompt})
    result = provider.generate(prompt, system_prompt=SYSTEM_PROMPT)
    tracker.track_request(
        provider=result["provider"],
        model=model_name,
        usage=result["usage"],
        latency_ms=result["latency_ms"],
    )
    logger.log_event(
        "CHATBOT_END",
        {
            "model": model_name,
            "latency_ms": result["latency_ms"],
            "usage": result["usage"],
        },
    )
    return result
