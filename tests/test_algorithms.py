import json
import random
import unittest

from algotrace.algorithms import CATALOG, compare_sorts, run_algorithm


class AlgorithmTests(unittest.TestCase):
    def test_sorts_against_python_on_seeded_inputs(self):
        rng = random.Random(2028)
        cases = [[], [1], [2, 2, 2], [3, -2, 0, 3], list(range(20)), list(range(20, -1, -1))]
        cases += [[rng.randint(-30, 30) for _ in range(rng.randint(0, 40))] for _ in range(100)]
        for name, spec in CATALOG.items():
            if spec.category != "sort":
                continue
            for values in cases:
                with self.subTest(algorithm=name, values=values):
                    original = values.copy()
                    result = run_algorithm(name, values)
                    self.assertEqual(result["result"], sorted(values))
                    self.assertEqual(values, original, "The caller's list must not be mutated")
                    self.assertEqual(result["events"][-1]["array"], sorted(values))
                    self.assertEqual(result["events"][-1]["counts"], result["counts"])

    def test_searches_match_reference(self):
        rng = random.Random(7)
        for _ in range(100):
            values = [rng.randint(-8, 8) for _ in range(rng.randint(0, 35))]
            for target in (-20, -1, 0, 5, 20):
                expected = values.index(target) if target in values else -1
                self.assertEqual(run_algorithm("linear", values, target)["result"], expected)
                ordered = sorted(values)
                result = run_algorithm("binary", ordered, target)["result"]
                if target in ordered:
                    self.assertEqual(ordered[result], target)
                    self.assertGreaterEqual(result, 0)
                else:
                    self.assertEqual(result, -1)

    def test_known_operation_counts(self):
        expected = {
            "bubble": {"comparisons": 3, "swaps": 3, "writes": 6},
            "insertion": {"comparisons": 3, "swaps": 0, "writes": 5},
            "selection": {"comparisons": 3, "swaps": 1, "writes": 2},
            "merge": {"comparisons": 3, "swaps": 0, "writes": 5},
        }
        for name, counts in expected.items():
            self.assertEqual(run_algorithm(name, [3, 2, 1])["counts"], counts)
        self.assertEqual(run_algorithm("bubble", [1, 2, 3, 4])["counts"]["comparisons"], 3)
        self.assertEqual(run_algorithm("linear", [1, 2, 3], 2)["counts"]["comparisons"], 2)
        self.assertEqual(run_algorithm("binary", [1, 2, 3], 2)["counts"]["comparisons"], 1)

    def test_trace_cap_keeps_complete_final_result_and_counts(self):
        values = list(range(128, 0, -1))
        limited = run_algorithm("bubble", values, trace_limit=2)
        self.assertEqual(len(limited["events"]), 3)
        self.assertEqual(limited["events"][-1]["kind"], "complete")
        self.assertEqual(limited["result"], sorted(values))
        self.assertEqual(limited["counts"]["comparisons"], 8128)
        self.assertEqual(limited["counts"]["swaps"], 8128)
        self.assertEqual(limited["omitted_events"], limited["total_events"] - 3)

    def test_trace_snapshots_are_independent_and_counts_monotonic(self):
        result = run_algorithm("insertion", [4, 2, 1, 3])
        self.assertEqual(result["events"][0]["array"], [4, 2, 1, 3])
        for before, after in zip(result["events"], result["events"][1:]):
            self.assertIsNot(before["array"], after["array"])
            self.assertLess(before["sequence"], after["sequence"])
            for key in before["counts"]:
                self.assertLessEqual(before["counts"][key], after["counts"][key])
        json.dumps(result)

    def test_binary_requires_sorted_input(self):
        with self.assertRaisesRegex(ValueError, "ascending"):
            run_algorithm("binary", [2, 1], 1)
        self.assertEqual(run_algorithm("binary", [], 1)["result"], -1)

    def test_invalid_values_and_targets(self):
        for invalid in (None, "1,2", [True], [1.5], ["2"], [1000001], [0] * 129, [float("nan")]):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                run_algorithm("bubble", invalid)
        for invalid in (None, True, 1.2, "3", 1000001):
            with self.subTest(target=invalid), self.assertRaises(ValueError):
                run_algorithm("linear", [1, 2], invalid)
        for invalid in (None, [], "missing"):
            with self.assertRaises(ValueError):
                run_algorithm(invalid, [1])
        for invalid in (True, 0, 1001, "2"):
            with self.assertRaises(ValueError):
                run_algorithm("bubble", [], trace_limit=invalid)

    def test_comparison_runs_share_input_and_agree(self):
        values = [8, -3, 8, 0]
        results = compare_sorts(values)
        self.assertEqual(len(results), 4)
        self.assertEqual({tuple(result["result"]) for result in results}, {tuple(sorted(values))})
        self.assertEqual(values, [8, -3, 8, 0])
        self.assertTrue(all("events" not in result for result in results))


if __name__ == "__main__":
    unittest.main()
