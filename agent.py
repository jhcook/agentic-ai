#!/usr/bin/env python3
"""
Agent script to listen to user input, transcribe it, and generate a response
using an LLM.

This script uses the SpeechRecognition library to capture audio input,
transcribes it using Google's speech recognition service, and then sends the
transcribed text to an LLM (like OpenAI's GPT) to generate a response.

Features:
    - Prompts the user for two pieces of information via microphone input.
    - Transcribes spoken input to text using Google's speech recognition API.
    - Sends the transcribed text to a language model (LLM) for generating a response.
    - Logs function calls, return values, and exceptions to a rotating log file.
    - Handles common errors gracefully, including audio recognition and remote disconnections.

Usage:
    python agent.py

Environment:
    - Requires a .env file with OPENAI_API_KEY set for LLM access.
    - Logging is configured via logging_config.py and writes to log/agent.log.

Dependencies:
    - speech_recognition
    - python-dotenv
    - litellm
    - logging_config (local module)
    - utils (local module)
"""

import os, time
import logging
from logging_config import setup_logging

setup_logging()

from utils import log_to_file

from dotenv import load_dotenv

import speech_recognition as sr
from http.client import RemoteDisconnected

from functools import wraps

from litellm import completion, Router, APIConnectionError
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()
os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
logger = logging.getLogger(__name__)

@log_to_file()
def listen_and_transcribe(message: str = "Please speak...") -> str:
    """
    Listen to microphone input and transcribe speech to text.

    Args:
        message (str): Prompt message to display to the user.

    Returns:
        str: Transcribed text from audio input, or None if transcription fails.

    Raises:
        sr.UnknownValueError: If speech is unintelligible.
        sr.RequestError: If there is an API error with the recognition service.
        RemoteDisconnected: If the remote server disconnects.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print(f"🎙️ {message}")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    for attempt in range(1, 4):  # Retry up to 3 times
        try:
            text = recognizer.recognize_google(audio)
            logging.info(f"Transcribed text: {text}")
            print(f"📝 You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            break  # No point retrying if audio is unintelligible
        except sr.RequestError as e:
            print(f"⚠️ Could not request results; {e}")
            break
        except RemoteDisconnected:
            print(f"🔁 Attempt {attempt}/3: Remote server disconnected.")
            if attempt == 3:
                print("❌ Failed after 3 retries.")
                break

@log_to_file()
def generate_response(messages: List[Dict]) -> str:
    """
    Generate a response from the LLM based on the provided messages.

    Args:
        messages (List[Dict]): List of message dicts for the LLM conversation.

    Returns:
        str: The LLM's response content, or an error message if the call fails.
    """
    router = Router(model_list=[
        {
            "model_name": "ollama/gpt-oss:20b",
            "litellm_params": {
                "model": "ollama/gpt-oss:20b",
                "api_key": "ollama",
                "api_base": "http://localhost:11434",
                "timeout": 300,
                "stream_timeout": 300
            }
        }
    ])
    try: 
        resp = router.completion(
            model="ollama/gpt-oss:20b",
            messages=messages,
            api_key="ollama",
            stream=True,
            timeout=300
        )
        response_text = ""
        for chunk in resp:
            if isinstance(chunk, dict):
                if not chunk.get("response") and chunk.get("thinking"):
                    continue
                content = chunk.get("response", "")
                if content is None:
                    content = ""
            else:
                try:
                    content = chunk.choices[0].delta.get("content", "")
                except AttributeError:
                    content = chunk["choices"][0]["delta"].get("content", "")
                if content is None:
                    content = ""
            print(content, end="", flush=True)
            response_text += content
        print()
        return response_text
    except APIConnectionError as e:
        logger.error(f"APIConnectionError: {e}")
        return f"APIConnectionError: {e}"
    except ValueError as e:
        return f"Value Error: {e}"

def main():
    """
    Main function to run the agent script.

    Prompts the user for two pieces of information, sends them to the LLM,
    and prints the generated response.
    """

    who_are_we = listen_and_transcribe("Who do you want to speak to?")
    what_is_the_problem = listen_and_transcribe("What is the problem?")

    if not who_are_we or not what_is_the_problem:
        print("❌ Missing input. Please try again.")
        return

    messages = [
        {"role": "system", "content": f"you are {who_are_we}"},
        {"role": "system", "content": "answer in on paragraph with no more than 5 sentences"},
        {"role": "user", "content": f"{what_is_the_problem}"}
    ]

    logging.debug(f"Messages: {messages}")

    response = generate_response(messages)
    print(response)

if __name__ == "__main__":
    try:
        main()
        time.sleep(1)  # Allow time for logger to flush
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
