import io
import logging
import unittest

from utils import log_to_file


class LogToFileTests(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("utils")
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        self.original_propagate = self.logger.propagate
        self.logger.propagate = False

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.logger.propagate = self.original_propagate

    def test_log_to_file_logs_arguments_and_return_value(self):
        @log_to_file()
        def add(a, b):
            return a + b

        result = add(2, 3)

        self.assertEqual(result, 5)
        logs = self.stream.getvalue()
        self.assertIn("Calling add", logs)
        self.assertIn("add returned 5", logs)

    def test_log_to_file_logs_exceptions(self):
        @log_to_file()
        def explode():
            raise ValueError("boom")

        with self.assertRaises(ValueError):
            explode()

        logs = self.stream.getvalue()
        self.assertIn("Exception in explode", logs)


if __name__ == "__main__":
    unittest.main()
