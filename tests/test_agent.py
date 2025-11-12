import io
import types
import unittest
from contextlib import redirect_stdout
from http.client import RemoteDisconnected
from unittest.mock import MagicMock, patch

import cli
import speech_service
from llm_client import LLMClient
from settings import LLMSettings
from speech_service import listen_and_transcribe


class ParseArgsTests(unittest.TestCase):
    def test_parse_args_defaults(self):
        with patch("sys.argv", ["agent.py"]):
            args = cli.parse_args()

        self.assertEqual(args.loglevel, "INFO")
        self.assertIsNone(args.model)
        self.assertFalse(args.stream)
        self.assertIsNone(args.temperature)
        self.assertIsNone(args.provider)
        self.assertIsNone(args.api_key)
        self.assertIsNone(args.api_base)
        self.assertIsNone(args.who)
        self.assertIsNone(args.question)

    def test_parse_args_overrides(self):
        cli_args = [
            "agent.py",
            "--loglevel",
            "DEBUG",
            "--model",
            "gpt-test",
            "--provider",
            "custom",
            "--api-key",
            "secret",
            "--api-base",
            "https://base",
            "--who",
            "scientist",
            "--question",
            "What is AI?",
            "--stream",
            "--temperature",
            "1.2",
        ]
        with patch("sys.argv", cli_args):
            args = cli.parse_args()

        self.assertEqual(args.loglevel, "DEBUG")
        self.assertEqual(args.model, "gpt-test")
        self.assertEqual(args.provider, "custom")
        self.assertEqual(args.api_key, "secret")
        self.assertEqual(args.api_base, "https://base")
        self.assertEqual(args.who, "scientist")
        self.assertEqual(args.question, "What is AI?")
        self.assertTrue(args.stream)
        self.assertEqual(args.temperature, 1.2)


class DummyChunk:
    def __init__(self, content):
        self.choices = [types.SimpleNamespace(delta={"content": content})]


class GenerateResponseTests(unittest.TestCase):
    def setUp(self):
        router_patcher = patch("llm_client.Router")
        self.addCleanup(router_patcher.stop)
        self.mock_router_cls = router_patcher.start()
        self.mock_router = MagicMock()
        self.mock_router_cls.return_value = self.mock_router

        config = LLMSettings(
            model_name="gpt-test",
            provider="provider-x",
            api_key="key-123",
            api_base="https://example-base",
            temperature=0.25,
            timeout=15,
        )
        self.client = LLMClient(config)

    def test_generate_response_concatenates_chunks_and_calls_router(self):
        messages = [{"role": "user", "content": "hello"}]
        self.mock_router.completion.return_value = [
            {"response": "Hello"},
            {"thinking": "internal"},
            DummyChunk(" world"),
            DummyChunk(None),
        ]

        result = self.client.generate_response(messages)

        expected_params = {
            "model": "gpt-test",
            "timeout": 15,
            "stream_timeout": 15,
            "api_key": "key-123",
            "api_base": "https://example-base",
            "custom_llm_provider": "provider-x",
        }
        self.mock_router_cls.assert_called_once_with(
            model_list=[{"model_name": "gpt-test", "litellm_params": expected_params}]
        )
        self.mock_router.completion.assert_called_once_with(
            model="gpt-test",
            messages=messages,
            stream=True,
            timeout=15,
            temperature=0.25,
        )
        self.assertEqual(result, "Hello world")

    def test_generate_response_prints_when_streaming_enabled(self):
        messages = [{"role": "user", "content": "stream please"}]
        self.mock_router.completion.return_value = [
            {"response": "Hi"},
            {"response": "!"},
        ]

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = self.client.generate_response(messages, stream=True)

        self.assertEqual(result, "Hi!")
        self.assertEqual(buffer.getvalue(), "Hi!\n")

    def test_generate_response_handles_api_connection_error(self):
        from litellm.exceptions import APIConnectionError

        self.mock_router.completion.side_effect = APIConnectionError(
            "down", "provider-x", "gpt-test"
        )

        result = self.client.generate_response([{"role": "user", "content": "hello"}])

        self.assertIn("APIConnectionError", result)

    def test_generate_response_handles_value_error(self):
        self.mock_router.completion.side_effect = ValueError("bad params")

        result = self.client.generate_response([{"role": "user", "content": "hello"}])

        self.assertEqual(result, "Value Error: bad params")


class ListenAndTranscribeTests(unittest.TestCase):
    @staticmethod
    def _setup_microphone(mock_microphone_cls):
        source = MagicMock(name="source")
        mock_microphone = MagicMock()
        mock_microphone.__enter__.return_value = source
        mock_microphone.__exit__.return_value = None
        mock_microphone_cls.return_value = mock_microphone
        return source

    @patch("builtins.print")
    @patch("speech_service.sr.Microphone")
    @patch("speech_service.sr.Recognizer")
    def test_listen_and_transcribe_success(self, mock_recognizer_cls, mock_microphone_cls, _mock_print):
        source = self._setup_microphone(mock_microphone_cls)
        mock_recognizer = MagicMock()
        mock_recognizer_cls.return_value = mock_recognizer
        mock_audio = MagicMock(name="audio")
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.return_value = "transcribed text"

        result = listen_and_transcribe("Say something")

        self.assertEqual(result, "transcribed text")
        mock_recognizer.adjust_for_ambient_noise.assert_called_once_with(source)
        mock_recognizer.listen.assert_called_once_with(source)
        mock_recognizer.recognize_google.assert_called_once_with(mock_audio)

    @patch("builtins.print")
    @patch("speech_service.sr.Microphone")
    @patch("speech_service.sr.Recognizer")
    def test_listen_and_transcribe_unknown_value_error(self, mock_recognizer_cls, mock_microphone_cls, _mock_print):
        self._setup_microphone(mock_microphone_cls)
        mock_recognizer = MagicMock()
        mock_recognizer_cls.return_value = mock_recognizer
        mock_recognizer.listen.return_value = MagicMock()
        mock_recognizer.recognize_google.side_effect = speech_service.sr.UnknownValueError()

        result = listen_and_transcribe()

        self.assertIsNone(result)
        self.assertEqual(mock_recognizer.recognize_google.call_count, 1)

    @patch("builtins.print")
    @patch("speech_service.sr.Microphone")
    @patch("speech_service.sr.Recognizer")
    def test_listen_and_transcribe_retries_on_remote_disconnected(self, mock_recognizer_cls, mock_microphone_cls, _mock_print):
        self._setup_microphone(mock_microphone_cls)
        mock_recognizer = MagicMock()
        mock_recognizer_cls.return_value = mock_recognizer
        mock_recognizer.listen.return_value = MagicMock()
        mock_recognizer.recognize_google.side_effect = [
            RemoteDisconnected("down"),
            RemoteDisconnected("down"),
            RemoteDisconnected("down"),
        ]

        result = listen_and_transcribe()

        self.assertIsNone(result)
        self.assertEqual(mock_recognizer.recognize_google.call_count, 3)


if __name__ == "__main__":
    unittest.main()
