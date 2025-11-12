import unittest

from graph import find_path


class FindPathTests(unittest.TestCase):
    def test_find_path_returns_first_matching_route(self):
        adjacency = {
            "a": [("b", "left")],
            "b": [("c", "right")],
            "c": [("d", "forward")],
        }

        path = find_path(adjacency, "a", "d")

        self.assertEqual(path, ["a", "a", "left", "b", "right", "c", "forward"])

    def test_find_path_returns_none_when_unreachable(self):
        adjacency = {
            "a": [("b", "left")],
            "b": [],
        }

        path = find_path(adjacency, "a", "z")

        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
