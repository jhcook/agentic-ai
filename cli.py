import argparse
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agentic AI Command-Line Interface")
    parser.add_argument(
        "--loglevel",
        type=str,
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument("--model", type=str, help="The LLM model to use.")
    parser.add_argument("--provider", type=str, help="LLM provider (e.g., openai, ollama).")
    parser.add_argument("--api-key", type=str, help="API key to use for the LLM request.", dest="api_key")
    parser.add_argument("--api-base", type=str, help="Custom API base URL for the provider.", dest="api_base")
    parser.add_argument("--who", type=str, help="Who do you want to ask the question?")
    parser.add_argument("--question", type=str, help="The question you are asking.")
    parser.add_argument("--stream", action="store_true", help="Stream the LLM response in real-time.", default=False)
    parser.add_argument("--temperature", type=float, help="Temperature for the LLM response.")
    return parser


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)
