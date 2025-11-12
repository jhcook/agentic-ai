import logging
from typing import Any, Dict, Iterable, List, Optional, cast

from litellm.exceptions import APIConnectionError
from litellm.router import Router

from settings import LLMSettings


class LLMClient:
    def __init__(self, config: LLMSettings):
        self.config = config
        self.logger = logging.getLogger("agent.llm")

    def _router(self) -> Router:
        params: Dict[str, Any] = {
            "model": self.config.model_name,
            "timeout": self.config.timeout,
            "stream_timeout": self.config.timeout,
        }
        if self.config.api_key:
            params["api_key"] = self.config.api_key
        if self.config.api_base:
            params["api_base"] = self.config.api_base
        if self.config.provider:
            params["custom_llm_provider"] = self.config.provider

        return Router(
            model_list=[
                {
                    "model_name": self.config.model_name,
                    "litellm_params": params,
                }
            ]
        )

    def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        router = self._router()
        try:
            resp: Iterable[Any] = router.completion(
                model=self.config.model_name,
                messages=messages,
                stream=True,
                timeout=self.config.timeout,
                temperature=self.config.temperature,
            )
            response_text = ""
            for chunk in resp:
                chunk_data = cast(Any, chunk)
                if isinstance(chunk_data, dict):
                    if not chunk_data.get("response") and chunk_data.get("thinking"):
                        continue
                    content = str(chunk_data.get("response") or "")
                else:
                    try:
                        content = str(chunk_data.choices[0].delta.get("content") or "")
                    except AttributeError:
                        content = str(chunk_data["choices"][0]["delta"].get("content") or "")

                if stream and content:
                    print(content, end="", flush=True)
                response_text += content

            if stream and response_text:
                print()
            return response_text
        except APIConnectionError as exc:
            self.logger.error("APIConnectionError: %s", exc)
            return f"APIConnectionError: {exc}"
        except ValueError as exc:
            return f"Value Error: {exc}"
