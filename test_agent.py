import unittest, time
from agent import generate_response

class AgentTests(unittest.TestCase):
    def test_generate_response(self):
        messages = [
            {"role": "system", "content": "you are a helpful assistant"},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        response = generate_response(messages)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        time.sleep(2)  # Allow time for logger to flush

if __name__ == "__main__":
    unittest.main()
