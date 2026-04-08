import unittest

from algorithms import STRATEGY_REGISTRY


class AlgorithmsTestCase(unittest.TestCase):
    def test_all_algorithms_find_same_occurrences(self):
        text = "abracadabra abra abracadabra"
        pattern = "abra"
        expected = [0, 7, 12, 17, 24]
        for strategy in STRATEGY_REGISTRY.values():
            with self.subTest(strategy=strategy.name):
                result = strategy.search(text, pattern)
                self.assertEqual(result["occurrences"], expected)
                self.assertGreaterEqual(result["comparisons"], 0)

    def test_empty_pattern_returns_empty_occurrences(self):
        for strategy in STRATEGY_REGISTRY.values():
            with self.subTest(strategy=strategy.name):
                result = strategy.search("abc", "")
                self.assertEqual(result["occurrences"], [])
                self.assertEqual(result["comparisons"], 0)

    def test_pattern_greater_than_text(self):
        for strategy in STRATEGY_REGISTRY.values():
            with self.subTest(strategy=strategy.name):
                result = strategy.search("abc", "abcdef")
                self.assertEqual(result["occurrences"], [])

    def test_overlapping_occurrences(self):
        expected = [0, 1, 2, 3]
        for strategy in STRATEGY_REGISTRY.values():
            with self.subTest(strategy=strategy.name):
                result = strategy.search("aaaaaa", "aaa")
                self.assertEqual(result["occurrences"], expected)

    def test_step_by_step_returns_explanation(self):
        for strategy in STRATEGY_REGISTRY.values():
            with self.subTest(strategy=strategy.name):
                steps = strategy.search_step_by_step("banana", "ana")
                self.assertTrue(len(steps) > 0)
                self.assertIn("description", steps[0])


if __name__ == "__main__":
    unittest.main()
