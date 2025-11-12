import logging
from typing import Any, Optional, cast

import speech_recognition as speech_recognition
from http.client import RemoteDisconnected

from utils import log_to_file

sr = cast(Any, speech_recognition)
logger = logging.getLogger("agent.speech")


@log_to_file()
def listen_and_transcribe(message: str = "Please speak...") -> Optional[str]:
    recognizer = cast(Any, sr.Recognizer())
    mic = sr.Microphone()

    with mic as source:
        print(f"🎙️ {message}")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    for attempt in range(1, 4):
        try:
            text = recognizer.recognize_google(audio)
            logger.info("Transcribed text: %s", text)
            print(f"📝 You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            break
        except sr.RequestError as exc:
            print(f"⚠️ Could not request results; {exc}")
            break
        except RemoteDisconnected:
            print(f"🔁 Attempt {attempt}/3: Remote server disconnected.")
            if attempt == 3:
                print("❌ Failed after 3 retries.")
                break
    return None
