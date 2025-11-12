import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMSettings:
    model_name: str
    provider: Optional[str]
    api_key: Optional[str]
    api_base: Optional[str]
    temperature: float
    timeout: int


@dataclass
class AgentSettings:
    log_level: str
    who: Optional[str]
    question: Optional[str]
    stream_response: bool
    llm: LLMSettings


def build_settings(args) -> AgentSettings:
    env_model = os.getenv("LLM_NAME")
    model_name = args.model or env_model
    if not model_name:
        raise ValueError("LLM model not configured. Set LLM_NAME in .env or pass --model.")

    temperature = (
        args.temperature
        if args.temperature is not None
        else float(os.getenv("LLM_TEMPERATURE", "0.0"))
    )
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0.")

    llm_settings = LLMSettings(
        model_name=model_name,
        provider=args.provider or os.getenv("LLM_PROVIDER"),
        api_key=args.api_key or os.getenv("LLM_API_KEY"),
        api_base=args.api_base or os.getenv("LLM_API_BASE"),
        temperature=temperature,
        timeout=int(os.getenv("LLM_TIMEOUT", "300")),
    )

    if llm_settings.provider == "ollama" and not llm_settings.api_base:
        llm_settings.api_base = "http://localhost:11434"

    return AgentSettings(
        log_level=args.loglevel or os.getenv("LOGLEVEL", "INFO"),
        who=args.who,
        question=args.question,
        stream_response=args.stream,
        llm=llm_settings,
    )
