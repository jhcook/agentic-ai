# Agentic AI

This project demonstrates how to create a simple AI agent using GPT models and speech recognition. The agent listens to user input via microphone, transcribes the speech to text, and generates a response using an LLM (Large Language Model).

## Features

- **Voice Input:** Prompts the user for information using the microphone.
- **Speech Recognition:** Uses Google's speech recognition API to transcribe spoken input.
- **LLM Integration:** Sends transcribed text to a GPT model (via [LiteLLM](https://github.com/BerriAI/litellm)) and returns a generated response.
- **Logging:** Logs function calls, return values, and exceptions to a rotating log file.
- **Environment Configuration:** Uses a `.env` file for API keys and log level.

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/agentic-ai.git
cd agentic-ai
```

### 2. Install dependencies

Make sure you have [Homebrew](https://brew.sh/) installed.

```sh
brew install python@3.11
brew install portaudio
python3.11 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the sample file and adjust it to match the LLM you want to use:

```sh
cp .env.example .env
```

Key variables:

- `LOGLEVEL` – default logging level.
- `LLM_NAME` – LiteLLM model identifier (e.g., `openai/gpt-4o-mini`, `gemini/gemini-1.5-pro`, `ollama/mistral:7b`).
- `LLM_PROVIDER` – provider hint (`openai`, `gemini`, `ollama`, etc.).
- `LLM_API_KEY` – API key or token (use `ollama` for local Ollama).
- `LLM_API_BASE` – override base URL (set to `http://localhost:11434` for Ollama, blank for OpenAI).
- `LLM_TEMPERATURE`, `LLM_TIMEOUT` – default generation settings.
- `OPENAI_API_KEY` – optional compatibility key for tooling that still expects it.

Any of these can be overridden at runtime with CLI flags such as `--model`, `--provider`, `--api-key`, `--api-base`, `--temperature`, `--who`, `--question`, or `--stream`.

### 4. Run the agent

```sh
./agent.py --model ollama/mistral:7b --provider ollama --stream
```

If you already populated `.env`, flags are optional. Use `./agent.py --help` to see the full list of overrides.

### 5. Run tests and static analysis

```sh
venv/bin/python -m unittest discover -s tests
venv/bin/python -m pyright
```

## File Structure

- `agent.py` — CLI entry point that wires modules together.
- `cli.py` — Argument parser definition.
- `settings.py` — Environment/CLI configuration loader.
- `llm_client.py` — LiteLLM wrapper responsible for routing and streaming output.
- `speech_service.py` — Microphone capture and transcription logic.
- `utils.py` — Utility functions and decorators (e.g., logging).
- `logging_config.py` — Centralized logging configuration.
- `graph.py` — Example DFS helper used by the exercises/tests.
- `.env` — Environment variables (not committed to git).
- `log/` — Directory for log files (ignored by git).
- `requirements.txt` — Python dependencies.

## Requirements

- Python 3.11+
- [PortAudio](http://www.portaudio.com/) (for microphone input)
- See `requirements.txt` for Python packages.

## Troubleshooting

- **Microphone not working:** Ensure your microphone is connected and accessible. You may need to grant microphone permissions.
- **No response from LLM:** Check your `.env` file for a valid `OPENAI_API_KEY`.
- **Logs not appearing:** Ensure the `log/` directory exists and is writable.

## Security

- **API Keys:** Never commit your `.env` file or API keys to version control.
- **Logs:** Log files may contain sensitive information. Handle them appropriately.

## To Be Continued

Further improvements and features will be added. Contributions are welcome!
