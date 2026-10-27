"""Pure algorithms and a bounded trace recorder; no web or UI dependencies."""

from dataclasses import dataclass
from typing import Callable

MAX_ITEMS = 128
MAX_ABSOLUTE_VALUE = 1_000_000


@dataclass(frozen=True)
class Algorithm:
    title: str
    category: str
    best: str
    average: str
    worst: str
    space: str
    note: str
    pseudocode: tuple[str, ...]


CATALOG = {
    "linear": Algorithm("Linear search", "search", "O(1)", "O(n)", "O(n)", "O(1)",
        "Works on unsorted data. Returns the first matching index, or -1.",
        ("for each index i:", "    compare values[i] with target", "    if equal: return i", "return -1")),
    "binary": Algorithm("Binary search", "search", "O(1)", "O(log n)", "O(log n)", "O(1)",
        "Requires ascending input. Returns one matching index; duplicates need not return the first. Sorting cost is not included.",
        ("low = 0; high = length - 1", "while low <= high:", "    mid = (low + high) // 2", "    compare values[mid] with target", "    if equal: return mid", "    if smaller: low = mid + 1", "    otherwise: high = mid - 1", "return -1")),
    "bubble": Algorithm("Bubble sort", "sort", "O(n)", "O(n²)", "O(n²)", "O(1)",
        "Adjacent swaps move the largest remaining value right. An unchanged pass stops early. Stable.",
        ("for end from length - 1 down to 1:", "    changed = false", "    for i from 0 to end - 1:", "        compare values[i] and values[i + 1]", "        if out of order: swap; changed = true", "    if unchanged: stop")),
    "insertion": Algorithm("Insertion sort", "sort", "O(n)", "O(n²)", "O(n²)", "O(1)",
        "Insert each value into a sorted prefix. Good for small or nearly sorted inputs. Stable.",
        ("for i from 1 to length - 1:", "    key = values[i]; j = i - 1", "    while j >= 0 and values[j] > key:", "        values[j + 1] = values[j]; j -= 1", "    values[j + 1] = key")),
    "selection": Algorithm("Selection sort", "sort", "O(n²)", "O(n²)", "O(n²)", "O(1)",
        "Find the smallest remaining value, then put it at the front. This swap-based implementation is not stable.",
        ("for start from 0 to length - 2:", "    minimum = start", "    for i from start + 1 to length - 1:", "        if values[i] < values[minimum]: minimum = i", "    if minimum differs: swap with start")),
    "merge": Algorithm("Merge sort", "sort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)",
        "Recursively split and merge sorted halves. Stable. Auxiliary copies and the call stack are omitted from the main-array write counter.",
        ("sort(low, high):", "    if interval has at most one value: return", "    mid = (low + high) // 2", "    sort(low, mid); sort(mid, high)", "    copy both sorted halves", "    compare fronts; write smaller to values", "    write any remaining values")),
}


def validate_values(values: object) -> list[int]:
    if not isinstance(values, list):
        raise ValueError("Values must be a list of integers.")
    if len(values) > MAX_ITEMS:
        raise ValueError(f"Use at most {MAX_ITEMS} values.")
    if any(type(value) is not int or abs(value) > MAX_ABSOLUTE_VALUE for value in values):
        raise ValueError(f"Each value must be an integer from {-MAX_ABSOLUTE_VALUE} to {MAX_ABSOLUTE_VALUE}.")
    return values.copy()


class Recorder:
    def __init__(self, values: list[int], limit: int):
        self.values = values.copy()
        self.events: list[dict] = []
        self.limit = limit
        self.counts = {"comparisons": 0, "swaps": 0, "writes": 0}
        self.total_events = 0
        self.event("start", "Input ready. No operations yet.", 0)

    def event(self, kind: str, message: str, line: int, active=(), window=None, force=False):
        self.total_events += 1
        if len(self.events) < self.limit or force:
            self.events.append({"kind": kind, "message": message, "line": line,
                "array": self.values.copy(), "active": list(active), "window": window,
                "counts": self.counts.copy(), "sequence": self.total_events})

    def compare(self, left: int, right: int, indices: tuple[int, ...], line: int) -> int:
        self.counts["comparisons"] += 1
        result = (left > right) - (left < right)
        symbol = "=" if result == 0 else "<" if result < 0 else ">"
        self.event("compare", f"Compare {left} {symbol} {right}.", line, indices)
        return result

    def swap(self, a: int, b: int, line: int):
        self.values[a], self.values[b] = self.values[b], self.values[a]
        self.counts["swaps"] += 1
        self.counts["writes"] += 2
        self.event("swap", f"Swap positions {a} and {b}.", line, (a, b))

    def write(self, index: int, value: int, line: int):
        self.values[index] = value
        self.counts["writes"] += 1
        self.event("write", f"Write {value} at position {index}.", line, (index,))


def linear(rec: Recorder, target: int):
    for i, value in enumerate(rec.values):
        if rec.compare(value, target, (i,), 2) == 0:
            rec.event("found", f"First match at index {i}.", 3, (i,))
            return i
    return -1


def binary(rec: Recorder, target: int):
    low, high = 0, len(rec.values) - 1
    while low <= high:
        mid = (low + high) // 2
        rec.event("window", f"Search indices {low} through {high}; midpoint {mid}.", 3, (mid,), [low, high])
        relation = rec.compare(rec.values[mid], target, (mid,), 4)
        if relation == 0:
            rec.event("found", f"Match at index {mid}.", 5, (mid,))
            return mid
        if relation < 0:
            low = mid + 1
            rec.event("window", "Discard the midpoint and everything to its left.", 6, (), [low, high])
        else:
            high = mid - 1
            rec.event("window", "Discard the midpoint and everything to its right.", 7, (), [low, high])
    return -1


def bubble(rec: Recorder, _):
    for end in range(len(rec.values) - 1, 0, -1):
        changed = False
        for i in range(end):
            if rec.compare(rec.values[i], rec.values[i + 1], (i, i + 1), 4) > 0:
                rec.swap(i, i + 1, 5)
                changed = True
        rec.event("pass", f"Pass complete. Position {end} is settled.", 6, (end,))
        if not changed:
            break
    return rec.values.copy()


def insertion(rec: Recorder, _):
    for i in range(1, len(rec.values)):
        key, j = rec.values[i], i - 1
        rec.event("key", f"Hold key {key}; insert it into the prefix.", 2, (i,))
        while j >= 0 and rec.compare(rec.values[j], key, (j,), 3) > 0:
            rec.write(j + 1, rec.values[j], 4)
            j -= 1
        rec.write(j + 1, key, 5)
    return rec.values.copy()


def selection(rec: Recorder, _):
    for start in range(len(rec.values) - 1):
        minimum = start
        for i in range(start + 1, len(rec.values)):
            if rec.compare(rec.values[i], rec.values[minimum], (i, minimum), 4) < 0:
                minimum = i
        if minimum != start:
            rec.swap(start, minimum, 5)
        rec.event("pass", f"Sorted prefix now ends at index {start}.", 1, (start,))
    return rec.values.copy()


def merge(rec: Recorder, _):
    def visit(low: int, high: int):
        if high - low <= 1:
            return
        mid = (low + high) // 2
        rec.event("split", f"Split [{low}, {high}) at index {mid}.", 3, (), [low, high - 1])
        visit(low, mid)
        visit(mid, high)
        left, right = rec.values[low:mid], rec.values[mid:high]
        i = j = 0
        k = low
        while i < len(left) and j < len(right):
            if rec.compare(left[i], right[j], (), 6) <= 0:
                rec.write(k, left[i], 6)
                i += 1
            else:
                rec.write(k, right[j], 6)
                j += 1
            k += 1
        for value in left[i:] + right[j:]:
            rec.write(k, value, 7)
            k += 1
        rec.event("merge", f"Merged sorted interval [{low}, {high}).", 6, (), [low, high - 1])
    visit(0, len(rec.values))
    return rec.values.copy()


RUNNERS: dict[str, Callable] = {"linear": linear, "binary": binary, "bubble": bubble,
    "insertion": insertion, "selection": selection, "merge": merge}


def run_algorithm(name: str, values: object, target=None, trace_limit=500) -> dict:
    if not isinstance(name, str) or name not in CATALOG:
        raise ValueError("Choose a supported algorithm.")
    clean = validate_values(values)
    if type(trace_limit) is not int or not 1 <= trace_limit <= 1000:
        raise ValueError("Trace limit must be an integer from 1 to 1000.")
    spec = CATALOG[name]
    if spec.category == "search" and (type(target) is not int or abs(target) > MAX_ABSOLUTE_VALUE):
        raise ValueError("Search needs an integer target between -1000000 and 1000000.")
    if name == "binary" and any(a > b for a, b in zip(clean, clean[1:])):
        raise ValueError("Binary search requires ascending input. Use 'Sort input' first; sorting is a separate operation.")
    rec = Recorder(clean, trace_limit)
    result = RUNNERS[name](rec, target)
    message = (f"Search complete: index {result}." if result != -1 else "Target not found.") if spec.category == "search" else "Complete. The array is sorted."
    rec.event("complete", message, 0, force=True)
    return {"algorithm": name, "title": spec.title, "category": spec.category,
        "input": clean, "target": target if spec.category == "search" else None,
        "result": result, "counts": rec.counts, "events": rec.events,
        "total_events": rec.total_events, "omitted_events": rec.total_events - len(rec.events),
        "counting_note": "Comparisons count three-way key comparisons, not loop checks. Swaps count as two main-array writes. Tracing memory is excluded from algorithm space complexity."}


def compare_sorts(values: object) -> list[dict]:
    clean = validate_values(values)
    return [{key: value for key, value in run_algorithm(name, clean, trace_limit=1).items()
        if key in ("algorithm", "title", "result", "counts")}
        for name, spec in CATALOG.items() if spec.category == "sort"]
