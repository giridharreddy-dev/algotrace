"""Independent reference checks for the expanded catalog, including brute force."""
import itertools
import json
import random
import unittest

from algotrace.algorithms import CATALOG, RUNNERS, compare_sorts, run_algorithm


class ExpandedCatalogTests(unittest.TestCase):
    def test_catalog_has_32_distinct_runners(self):
        self.assertEqual(len(CATALOG), 32)
        self.assertEqual(set(CATALOG), set(RUNNERS))
        self.assertEqual(len({spec.title for spec in CATALOG.values()}), 32)
        self.assertEqual({category: sum(spec.category == category for spec in CATALOG.values())
            for category in ("search", "sort", "array")}, {"search": 8, "sort": 14, "array": 10})

    def test_all_searches_exhaustive_small_sorted_arrays(self):
        cases = [list(case) for n in range(6) for case in itertools.combinations_with_replacement(range(-2, 3), n)]
        cases += [[], [1000000], [-1000000, 0, 1000000], [3] * 128, list(range(128))]
        for name, spec in CATALOG.items():
            if spec.category != "search":
                continue
            for values in cases:
                for target in (-1000000, -3, -2, -1, 0, 1, 2, 3, 127, 128, 1000000):
                    with self.subTest(algorithm=name, values=values, target=target):
                        answer = run_algorithm(name, values, target, trace_limit=2)["result"]
                        if target not in values:
                            self.assertEqual(answer, -1)
                        elif name in ("linear", "jump", "binary_first"):
                            self.assertEqual(answer, values.index(target))
                        else:
                            self.assertGreaterEqual(answer, 0)
                            self.assertLess(answer, len(values))
                            self.assertEqual(values[answer], target)

    def test_all_sorted_searches_reject_unsorted_values(self):
        for name, spec in CATALOG.items():
            if spec.sorted_input:
                with self.subTest(algorithm=name), self.assertRaisesRegex(ValueError, "ascending"):
                    run_algorithm(name, [5, 1, 3], 3)

    def test_sorts_exhaustive_and_extreme_signed_inputs(self):
        rng = random.Random(412)
        cases = [list(case) for n in range(5) for case in itertools.product((-1, 0, 1), repeat=n)]
        cases += [[rng.randint(-1000000, 1000000) for _ in range(50)] for _ in range(20)]
        cases += [list(range(128)), list(range(128, 0, -1)), [1000000] * 128, [-1000000, 1000000, 0]]
        for name, spec in CATALOG.items():
            if spec.category != "sort":
                continue
            for values in cases:
                if name == "counting" and values and max(values) - min(values) > 4095:
                    continue
                with self.subTest(algorithm=name, values=values):
                    self.assertEqual(run_algorithm(name, values, trace_limit=2)["result"], sorted(values))

    def test_counting_range_boundary_and_comparison_skip(self):
        self.assertEqual(run_algorithm("counting", [-2048, 2047])["result"], [-2048, 2047])
        with self.assertRaisesRegex(ValueError, "4096"):
            run_algorithm("counting", [-2048, 2048])
        rows = compare_sorts([-1000000, 1000000])
        self.assertEqual(len(rows), 14)
        skipped = [row for row in rows if "skipped" in row]
        self.assertEqual([row["algorithm"] for row in skipped], ["counting"])
        self.assertTrue(all(row["result"] == [-1000000, 1000000] for row in rows if "skipped" not in row))
        self.assertEqual({row["algorithm"] for row in rows if row["family"] == "distribution"}, {"radix", "counting", "bucket"})

    def test_array_transforms_against_references(self):
        rng = random.Random(42)
        for _ in range(100):
            values = [rng.randint(-8, 8) for _ in range(rng.randrange(20))]
            original = values.copy()
            self.assertEqual(run_algorithm("prefix_sum", values)["result"], list(itertools.accumulate(values)))
            self.assertEqual(run_algorithm("running_max", values)["result"], [max(values[:i + 1]) for i in range(len(values))])
            self.assertEqual(run_algorithm("reverse", values)["result"], values[::-1])
            self.assertEqual(run_algorithm("deduplicate", values)["result"], list(dict.fromkeys(values)))
            for k in (-100, -3, 0, 1, 3, 100):
                offset = k % len(values) if values else 0
                expected = values[-offset:] + values[:-offset] if offset else values
                self.assertEqual(run_algorithm("rotate", values, k)["result"], expected)
            self.assertEqual(values, original)

    def test_kadane_against_brute_force(self):
        for n in range(6):
            for case in itertools.product((-2, 0, 3), repeat=n):
                values = list(case)
                result = run_algorithm("kadane", values, trace_limit=2)["result"]
                if not values:
                    self.assertEqual(result, {"sum": 0, "start": None, "end": None})
                    continue
                expected = max(sum(values[i:j + 1]) for i in range(n) for j in range(i, n))
                self.assertEqual(result["sum"], expected)
                self.assertEqual(sum(values[result["start"]:result["end"] + 1]), expected)

    def test_majority_against_frequency_counts(self):
        for n in range(7):
            for values in itertools.product((0, 1, 2), repeat=n):
                values = list(values)
                actual = run_algorithm("majority", values, trace_limit=2)["result"]
                expected = next((value for value in set(values) if values.count(value) > n // 2), None)
                if expected is None:
                    self.assertIsNone(actual)
                else:
                    self.assertEqual(actual, {"value": expected, "count": values.count(expected)})

    def test_two_sum_against_pair_enumeration(self):
        rng = random.Random(96)
        for _ in range(150):
            values = [rng.randint(-10, 10) for _ in range(rng.randrange(15))]
            target = rng.randint(-20, 20)
            exists = any(values[i] + values[j] == target for i in range(len(values)) for j in range(i + 1, len(values)))
            result = run_algorithm("two_sum", values, target)["result"]
            self.assertEqual(result is not None, exists)
            if exists:
                i, j = result["indices"]
                self.assertLess(i, j)
                self.assertEqual(values[i] + values[j], target)
                self.assertEqual(result["values"], [values[i], values[j]])
        self.assertIsNone(run_algorithm("two_sum", [3], 6)["result"])
        self.assertEqual(run_algorithm("two_sum", [3, 3], 6)["result"]["indices"], [0, 1])

    def test_window_sums_against_brute_force(self):
        rng = random.Random(2)
        for _ in range(50):
            values = [rng.randint(-10, 10) for _ in range(rng.randint(1, 20))]
            for k in range(1, len(values) + 1):
                sums = [sum(values[i:i + k]) for i in range(len(values) - k + 1)]
                result = run_algorithm("sliding_window", values, k, trace_limit=2)["result"]
                self.assertEqual(result, {"sum": max(sums), "start": sums.index(max(sums)), "end": sums.index(max(sums)) + k - 1})

    def test_lis_against_subsequence_enumeration(self):
        rng = random.Random(71)
        cases = [[], [2, 2, 2], [5, 4, 3], [1, 2, 3], [10, 9, 2, 5, 3, 7, 101, 18]]
        cases += [[rng.randint(-3, 3) for _ in range(rng.randrange(9))] for _ in range(100)]
        for values in cases:
            sequences = [[values[i] for i in range(len(values)) if mask & (1 << i)] for mask in range(1 << len(values))]
            expected = max(len(seq) for seq in sequences if all(a < b for a, b in zip(seq, seq[1:])))
            result = run_algorithm("lis", values)["result"]
            self.assertEqual(result["length"], expected)
            self.assertEqual(result["sequence"], [values[i] for i in result["indices"]])
            self.assertTrue(all(a < b for a, b in zip(result["sequence"], result["sequence"][1:])))
            self.assertTrue(all(a < b for a, b in zip(result["indices"], result["indices"][1:])))

    def test_new_parameter_errors(self):
        for name in ("rotate", "two_sum", "sliding_window"):
            for invalid in (None, True, "2", 1.2, 1000001):
                with self.subTest(algorithm=name, parameter=invalid), self.assertRaises(ValueError):
                    run_algorithm(name, [1, 2, 3], invalid)
        for values, k in (([], 1), ([1, 2], 0), ([1, 2], -1), ([1, 2], 3)):
            with self.assertRaisesRegex(ValueError, "Window size"):
                run_algorithm("sliding_window", values, k)

    def test_trace_state_schema_for_every_algorithm(self):
        for name, spec in CATALOG.items():
            values = [1, 2, 2, 3, 5] if spec.sorted_input else [3, -1, 2, 3, 0]
            target = 2 if spec.category == "search" else spec.parameter_default if spec.parameter else None
            result = run_algorithm(name, values, target, trace_limit=20)
            with self.subTest(algorithm=name):
                self.assertEqual(result["events"][-1]["kind"], "complete")
                self.assertEqual(result["events"][-1]["counts"], result["counts"])
                for event in result["events"]:
                    self.assertLessEqual(event["line"], len(spec.pseudocode))
                    self.assertGreaterEqual(event["line"], 0)
                    self.assertTrue(all(0 <= index < len(event["array"]) for index in event["active"]))
                    self.assertIsInstance(event["state"], dict)
                json.dumps(result)

    def test_working_states_do_not_alias_later_steps(self):
        result = run_algorithm("lis", [3, 1, 2, 4])
        states = [event["state"]["lengths"] for event in result["events"] if "lengths" in event["state"]]
        self.assertEqual(states[0], [1, 1, 1, 1])
        self.assertEqual(states[-1], [1, 1, 2, 3])
        self.assertIsNot(states[0], states[-1])


if __name__ == "__main__":
    unittest.main()
