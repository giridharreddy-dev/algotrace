"""Additional algorithms. Each runner uses the same recorder protocol."""

from math import isqrt


def definitions(A):
    def search(title, average, worst, note, code, best="O(1)"):
        return A(title, "search", best, average, worst, "O(1)", note + " Requires ascending input; preprocessing is excluded.", tuple(code), sorted_input=True)
    def sort(title, best, average, worst, space, note, code, family="comparison"):
        return A(title, "sort", best, average, worst, space, note, tuple(code), family=family)
    def array(title, time, space, note, code, parameter=None, default=3, best=None):
        return A(title, "array", best or time, time, time, space, note, tuple(code), parameter=parameter, parameter_default=default)
    return {
        "jump": search("Jump search", "O(√n)", "O(√n)", "Jump by √n, then scan the candidate block. Returns the first match.",
            ["step = floor(sqrt(n)); start = 0", "jump while block's last key < target", "scan this block left to right", "return first match, or -1"]),
        "exponential": search("Exponential search", "O(log n)", "O(log n)", "Double the search bound, then binary-search the bracket. Returns any match.",
            ["check the first key", "double bound while key < target", "binary-search the bounded interval", "return a match, or -1"]),
        "interpolation": search("Interpolation search", "O(log log n)*", "O(n)", "*Average assumes roughly uniform numeric keys. Estimate a probe from key values; equal endpoints are handled. Returns any match.",
            ["low = 0; high = n - 1", "check target is between endpoint keys", "if endpoint keys equal: check that key", "estimate probe using target's relative value", "compare probe; narrow interval", "return a match, or -1"]),
        "ternary": search("Ternary search (sorted keys)", "O(log n)", "O(log n)", "Split an interval at two probes to find an exact key. This is not unimodal-function optimization. Returns any match.",
            ["while interval is nonempty:", "    select one-third and two-third probes", "    compare target with both probes", "    retain the only possible third", "return -1 if no match"]),
        "fibonacci_search": search("Fibonacci search", "O(log n)", "O(log n)", "Use Fibonacci-sized intervals rather than midpoint division. Returns any match.",
            ["grow Fibonacci numbers until F >= n", "probe offset + F(previous previous)", "if smaller: move offset and shrink right", "if larger: shrink left", "check the last possible key", "return match or -1"], best="O(log n)"),
        "binary_first": search("Binary search · first occurrence", "O(log n)", "O(log n)", "Keep a match and continue left to locate the first duplicate.",
            ["low = 0; high = n - 1; answer = -1", "while low <= high:", "    compare midpoint with target", "    if equal: save answer and continue left", "    otherwise: discard an impossible half", "return answer"], best="O(log n)"),
        "quick": sort("Quicksort", "O(n log n)", "O(n log n)*", "O(n²)", "O(log n)", "Lomuto partition with the final value as pivot. *Average assumes random input order. Smaller-part recursion bounds stack depth; equal/sorted keys can still cost quadratic work. Not stable.",
            ["choose final value as pivot", "scan: move keys <= pivot to the left", "put pivot at its final position", "recurse on the smaller partition", "iterate over the larger partition"]),
        "heap": sort("Heap sort", "O(n)*", "O(n log n)", "O(n log n)", "O(1)", "Build a max heap; move its root to the end and restore the heap. *All-equal keys permit early-stop sifts and linear best-case work here. Not stable.",
            ["build max heap from bottom to top", "swap root with final unsorted value", "sift the new root down", "repeat for the smaller heap"]),
        "shell": sort("Shell sort", "O(n log n)", "Gap-dependent", "O(n²)", "O(1)", "Uses gaps n//2, n//4, …, 1 with gapped insertion. Complexity depends on the gap sequence. Not stable.",
            ["gap = n // 2", "perform insertion sort across each gap", "halve the gap", "stop after gap 1"]),
        "counting": sort("Counting sort", "O(n + k)", "O(n + k)", "O(n + k)", "O(k)", "k = max - min + 1, capped at 4096. Supports negative values by an offset. Reconstructs integer keys; it does not preserve attached-record order. Distribution work is not captured by key comparisons alone.",
            ["find minimum and maximum", "count each key at key - minimum", "visit counts in ascending key order", "write each key its recorded number of times"], "distribution"),
        "radix": sort("Radix sort · LSD base 10", "O(d(n + 10))", "O(d(n + 10))", "O(d(n + 10))", "O(n + 10)", "Stable digit buckets. Subtract the minimum to support signed integers; d is the number of digits in the shifted maximum. Auxiliary bucket work is not key comparison work.",
            ["find minimum; use key - minimum for digits", "for each digit, from least significant:", "    distribute keys into 10 stable buckets", "    flatten buckets back into the array"], "distribution"),
        "bucket": sort("Bucket sort", "O(n)", "O(n)*", "O(n²)", "O(n)", "n numeric-range buckets, each sorted using insertion sort. *Average assumes uniformly distributed keys. Stable. Bucket writes are auxiliary, not main-array writes.",
            ["find range; allocate n buckets", "distribute keys by their numeric range", "insertion-sort each bucket", "flatten buckets into the main array"], "distribution"),
        "cocktail": sort("Cocktail shaker sort", "O(n)", "O(n²)", "O(n²)", "O(1)", "Bubble in both directions, settling a value at either end per sweep. Stable.",
            ["sweep left to right, swapping inversions", "reduce the right boundary", "sweep right to left, swapping inversions", "increase the left boundary; stop if unchanged"]),
        "comb": sort("Comb sort", "O(n log n)", "Gap-dependent", "O(n²)", "O(1)", "Shrink a comparison gap by about 1.3; finish with adjacent passes until unchanged. Not stable. Average bounds depend on the gap policy.",
            ["gap = n; changed = true", "shrink gap to max(1, gap * 10 // 13)", "compare and swap keys separated by gap", "repeat until gap 1 has no swaps"]),
        "gnome": sort("Gnome sort", "O(n)", "O(n²)", "O(n²)", "O(1)", "Move forward when neighbors are ordered; otherwise swap and step back. Stable.",
            ["position = 1", "if at start or neighbors ordered: step forward", "otherwise: swap neighbors; step backward", "stop at the end"]),
        "odd_even": sort("Odd-even transposition sort", "O(n)", "O(n²)", "O(n²)", "O(1)", "Alternate odd and even adjacent pairs until neither pass swaps anything. This implementation is sequential. Stable.",
            ["repeat:", "    compare and swap odd adjacent pairs", "    compare and swap even adjacent pairs", "stop after a complete unchanged round"]),
        "kadane": array("Maximum subarray · Kadane", "O(n)", "O(1)", "Find a nonempty contiguous subarray with maximum sum. Empty input returns sum 0 with null endpoints. Ties keep an earlier discovered optimum.",
            ["start a sum at the first value", "extend the previous sum or start here", "update the best sum and endpoints", "return sum, start and end"]),
        "prefix_sum": array("Prefix sums", "O(n)", "O(1)*", "Each position becomes the sum through that index. *Mutates the working array; the returned copy and recorder snapshots are excluded.",
            ["total = 0", "for each value:", "    total += value", "    write total at this position"]),
        "running_max": array("Running maximum", "O(n)", "O(1)*", "Each position becomes the maximum seen so far. *Mutates the working array; result-copy and trace storage are excluded.",
            ["best = first value", "for each next value: compare with best", "write the current best at each position"]),
        "reverse": array("Array reversal · two pointers", "O(n)", "O(1)*", "Swap the two endpoints and move inward. *Result-copy and trace storage are excluded.",
            ["left = 0; right = n - 1", "while left < right:", "    swap endpoints", "    left += 1; right -= 1"]),
        "rotate": array("Array rotation · three reversals", "O(n)", "O(1)*", "Positive positions rotate right; negative positions rotate left. Reduce positions modulo n. *Zero effective rotation needs only constant algorithm work; result-copy and trace storage are excluded.",
            ["k = positions modulo n", "reverse the whole array", "reverse the first k values", "reverse the remaining values"], "Positions (right)", 3, best="O(1)*"),
        "deduplicate": array("Remove duplicates · hash set", "O(n)*", "O(n)", "Keep first occurrences in input order. *Expected time assumes average constant-time hashing. The chart retains input; the result is a separate list. Hash lookups are not key comparisons.",
            ["seen = set(); output = []", "for each value: look it up in seen", "if new: remember it and append to output", "return output"]),
        "majority": array("Majority element · Boyer–Moore", "O(n)", "O(1)", "Cancel unequal votes, then verify the candidate occurs more than n/2 times. Returns null when no majority exists.",
            ["candidate = none; votes = 0", "if no votes: choose this value", "equal value adds a vote; unequal cancels one", "count the candidate in a second pass", "return it only if count > n // 2"]),
        "two_sum": array("Two sum · hash map", "O(n)*", "O(n)", "Find two distinct input indices whose values add to the target. *Expected hashing time. Returns the first pair discovered or null. The input is unchanged; hash lookups are not key comparisons.",
            ["remembered = map of value to first index", "for each index i:", "    look up target - values[i]", "    if found: return the two indices", "    otherwise remember this value", "return null"], "Target sum", 20),
        "sliding_window": array("Maximum fixed-window sum", "O(n)", "O(1)", "For window size k, add the entering value and subtract the leaving value. Requires 1 <= k <= n. Returns the best sum and its endpoints.",
            ["sum the first k values", "record that first window", "slide: add entering key, subtract leaving key", "update best sum and start", "return best window"], "Window size (k)", 3),
        "lis": array("Longest increasing subsequence · DP", "O(n²)", "O(n)", "Strictly increasing: equal values do not extend a sequence. Dynamic programming stores a length and predecessor per position. Returns a reconstructed sequence. State shows the DP table.",
            ["length[i] = 1; previous[i] = none", "for each position i:", "    inspect each earlier j", "    if values[j] < values[i]: try extending j", "reconstruct a best sequence via predecessors"]),
    }


def _binary_range(r, target, low, high, line=3, first=False):
    answer = -1
    while low <= high:
        mid = (low + high) // 2
        r.event("window", f"Probe index {mid} in [{low}, {high}].", line, (mid,), [low, high])
        relation = r.compare(r.values[mid], target, (mid,), line)
        if relation == 0:
            answer = mid
            if not first:
                return answer
            high = mid - 1
        elif relation < 0:
            low = mid + 1
        else:
            high = mid - 1
    return answer


def jump(r, target):
    n = len(r.values)
    if not n:
        return -1
    step, start = max(1, isqrt(n)), 0
    while start < n:
        end = min(start + step, n) - 1
        r.event("jump", f"Check block [{start}, {end}].", 2, (end,), [start, end])
        if r.compare(r.values[end], target, (end,), 2) >= 0:
            for i in range(start, end + 1):
                relation = r.compare(r.values[i], target, (i,), 3)
                if relation == 0:
                    return i
                if relation > 0:
                    return -1
            return -1
        start += step
    return -1


def exponential(r, target):
    if not r.values:
        return -1
    if r.compare(r.values[0], target, (0,), 1) == 0:
        return 0
    bound = 1
    while bound < len(r.values):
        if r.compare(r.values[bound], target, (bound,), 2) >= 0:
            break
        r.event("expand", f"Double the bound from {bound} to {bound * 2}.", 2, (bound,))
        bound *= 2
    return _binary_range(r, target, bound // 2, min(bound, len(r.values) - 1))


def interpolation(r, target):
    low, high = 0, len(r.values) - 1
    while low <= high:
        if r.compare(target, r.values[low], (low,), 2) < 0 or r.compare(target, r.values[high], (high,), 2) > 0:
            break
        if r.compare(r.values[low], r.values[high], (low, high), 3) == 0:
            return low if r.compare(r.values[low], target, (low,), 3) == 0 else -1
        probe = low + (target - r.values[low]) * (high - low) // (r.values[high] - r.values[low])
        r.event("probe", f"Value-based interpolation estimates index {probe}.", 4, (probe,), [low, high])
        relation = r.compare(r.values[probe], target, (probe,), 5)
        if relation == 0:
            return probe
        if relation < 0:
            low = probe + 1
        else:
            high = probe - 1
    return -1


def ternary(r, target):
    low, high = 0, len(r.values) - 1
    while low <= high:
        a, b = low + (high - low) // 3, high - (high - low) // 3
        left = r.compare(r.values[a], target, (a,), 3)
        if left == 0:
            return a
        right = r.compare(r.values[b], target, (b,), 3)
        if right == 0:
            return b
        if left > 0:
            high = a - 1
        elif right < 0:
            low = b + 1
        else:
            low, high = a + 1, b - 1
        r.event("window", f"Retain [{low}, {high}].", 4, (), [low, high])
    return -1


def fibonacci_search(r, target):
    n = len(r.values)
    if not n:
        return -1
    a, b = 0, 1
    f = a + b
    while f < n:
        a, b, f = b, f, b + f
    offset = -1
    while f > 1:
        i = min(offset + a, n - 1)
        relation = r.compare(r.values[i], target, (i,), 2)
        if relation < 0:
            f, b, a, offset = b, a, b - a, i
        elif relation > 0:
            f, b, a = a, b - a, a - (b - a)
        else:
            return i
        r.event("fibonacci", f"Remaining Fibonacci span {f}; offset {offset}.", 3 if relation < 0 else 4, state={"span": f, "offset": offset})
    if b and offset + 1 < n and r.compare(r.values[offset + 1], target, (offset + 1,), 5) == 0:
        return offset + 1
    return -1


def binary_first(r, target):
    return _binary_range(r, target, 0, len(r.values) - 1, first=True)


def quick(r, _):
    def partition(low, high):
        pivot, boundary = r.values[high], low
        r.event("pivot", f"Pivot {pivot} at index {high}.", 1, (high,), [low, high])
        for i in range(low, high):
            if r.compare(r.values[i], pivot, (i, high), 2) <= 0:
                if i != boundary:
                    r.swap(i, boundary, 2)
                boundary += 1
        if boundary != high:
            r.swap(boundary, high, 3)
        return boundary
    def visit(low, high):
        while low < high:
            pivot = partition(low, high)
            if pivot - low < high - pivot:
                visit(low, pivot - 1)
                low = pivot + 1
            else:
                visit(pivot + 1, high)
                high = pivot - 1
    visit(0, len(r.values) - 1)
    return r.values.copy()


def heap(r, _):
    def sift(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and r.compare(r.values[child], r.values[child + 1], (child, child + 1), 3) < 0:
                child += 1
            if r.compare(r.values[root], r.values[child], (root, child), 3) >= 0:
                break
            r.swap(root, child, 3)
            root = child
    for root in range(len(r.values) // 2 - 1, -1, -1):
        sift(root, len(r.values))
    for end in range(len(r.values) - 1, 0, -1):
        r.swap(0, end, 2)
        sift(0, end)
    return r.values.copy()


def shell(r, _):
    gap = len(r.values) // 2
    while gap:
        r.event("gap", f"Gapped insertion with gap {gap}.", 1, state={"gap": gap})
        for i in range(gap, len(r.values)):
            key, j = r.values[i], i
            while j >= gap and r.compare(r.values[j - gap], key, (j - gap,), 2) > 0:
                r.write(j, r.values[j - gap], 2)
                j -= gap
            r.write(j, key, 2)
        gap //= 2
    return r.values.copy()


def _range(r):
    low = high = r.values[0]
    for i, value in enumerate(r.values[1:], 1):
        if r.compare(value, low, (i,), 1) < 0:
            low = value
        if r.compare(value, high, (i,), 1) > 0:
            high = value
    return low, high


def counting(r, _):
    if not r.values:
        return []
    low, high = _range(r)
    counts = [0] * (high - low + 1)
    for i, value in enumerate(r.values):
        counts[value - low] += 1
        r.event("count", f"Count key {value}: {counts[value - low]} occurrence(s).", 2, (i,), state={"key": value, "frequency": counts[value - low], "range_size": len(counts)})
    index = 0
    for key, frequency in enumerate(counts):
        for _ in range(frequency):
            r.write(index, key + low, 4)
            index += 1
    return r.values.copy()


def radix(r, _):
    if not r.values:
        return []
    low, high = _range(r)
    place = 1
    while (high - low) // place:
        buckets = [[] for _ in range(10)]
        for i, value in enumerate(r.values):
            digit = ((value - low) // place) % 10
            buckets[digit].append(value)
            r.event("bucket", f"Key {value} enters digit bucket {digit} at place {place}.", 3, (i,), state={"digit_place": place, "bucket_sizes": [len(b) for b in buckets]})
        for i, value in enumerate(value for bucket in buckets for value in bucket):
            r.write(i, value, 4)
        place *= 10
    return r.values.copy()


def bucket(r, _):
    n = len(r.values)
    if not n:
        return []
    low, high = _range(r)
    buckets = [[] for _ in range(n)]
    for i, value in enumerate(r.values):
        index = (value - low) * n // (high - low + 1)
        buckets[index].append(value)
        r.event("bucket", f"Key {value} enters range bucket {index}.", 2, (i,), state={"bucket": index, "values": buckets[index].copy()})
    for index, group in enumerate(buckets):
        for i in range(1, len(group)):
            key, j = group[i], i - 1
            while j >= 0 and r.compare(group[j], key, (), 3) > 0:
                group[j + 1] = group[j]
                j -= 1
            group[j + 1] = key
            r.event("bucket_sort", f"Insertion-sort inside bucket {index}.", 3, state={"bucket": index, "values": group.copy()})
    for i, value in enumerate(value for group in buckets for value in group):
        r.write(i, value, 4)
    return r.values.copy()


def cocktail(r, _):
    low, high, changed = 0, len(r.values) - 1, True
    while low < high and changed:
        changed = False
        for i in range(low, high):
            if r.compare(r.values[i], r.values[i + 1], (i, i + 1), 1) > 0:
                r.swap(i, i + 1, 1)
                changed = True
        if not changed:
            break
        high -= 1
        changed = False
        for i in range(high, low, -1):
            if r.compare(r.values[i - 1], r.values[i], (i - 1, i), 3) > 0:
                r.swap(i - 1, i, 3)
                changed = True
        low += 1
    return r.values.copy()


def comb(r, _):
    gap, changed = len(r.values), True
    while gap > 1 or changed:
        gap, changed = max(1, gap * 10 // 13), False
        r.event("gap", f"Compare with gap {gap}.", 2, state={"gap": gap})
        for i in range(len(r.values) - gap):
            if r.compare(r.values[i], r.values[i + gap], (i, i + gap), 3) > 0:
                r.swap(i, i + gap, 3)
                changed = True
    return r.values.copy()


def gnome(r, _):
    i = 1
    while i < len(r.values):
        if i == 0 or r.compare(r.values[i - 1], r.values[i], (i - 1, i), 2) <= 0:
            i += 1
        else:
            r.swap(i - 1, i, 3)
            i -= 1
    return r.values.copy()


def odd_even(r, _):
    changed = True
    while changed:
        changed = False
        for parity in (1, 0):
            for i in range(parity, len(r.values) - 1, 2):
                if r.compare(r.values[i], r.values[i + 1], (i, i + 1), 2 if parity else 3) > 0:
                    r.swap(i, i + 1, 2 if parity else 3)
                    changed = True
    return r.values.copy()


def kadane(r, _):
    if not r.values:
        return {"sum": 0, "start": None, "end": None}
    current = best = r.values[0]
    start = best_start = best_end = 0
    for i in range(1, len(r.values)):
        if r.compare(r.values[i], current + r.values[i], (i,), 2) > 0:
            current, start = r.values[i], i
        else:
            current += r.values[i]
        if r.compare(current, best, (i,), 3) > 0:
            best, best_start, best_end = current, start, i
        r.event("sum", f"Best sum so far: {best}.", 3, (i,), [start, i], state={"current_sum": current, "best_sum": best, "best_interval": [best_start, best_end]})
    return {"sum": best, "start": best_start, "end": best_end}


def prefix_sum(r, _):
    total = 0
    for i in range(len(r.values)):
        total += r.values[i]
        r.state = {"running_sum": total}
        r.write(i, total, 4)
    return r.values.copy()


def running_max(r, _):
    if not r.values:
        return []
    best = r.values[0]
    for i in range(len(r.values)):
        if i and r.compare(r.values[i], best, (i,), 2) > 0:
            best = r.values[i]
        r.state = {"maximum_so_far": best}
        r.write(i, best, 3)
    return r.values.copy()


def _reverse(r, low, high, line):
    while low < high:
        r.swap(low, high, line)
        low, high = low + 1, high - 1


def reverse(r, _):
    _reverse(r, 0, len(r.values) - 1, 3)
    return r.values.copy()


def rotate(r, positions):
    if not r.values:
        return []
    k = positions % len(r.values)
    r.event("rotation", f"Rotate right by {k} after reducing modulo length.", 1, state={"positions_mod_n": k})
    if k:
        _reverse(r, 0, len(r.values) - 1, 2)
        _reverse(r, 0, k - 1, 3)
        _reverse(r, k, len(r.values) - 1, 4)
    return r.values.copy()


def deduplicate(r, _):
    seen, output = set(), []
    for i, value in enumerate(r.values):
        fresh = value not in seen
        if fresh:
            seen.add(value)
            output.append(value)
        r.event("lookup", f"{'Keep new' if fresh else 'Skip repeated'} key {value}.", 3 if fresh else 2, (i,), state={"unique_output": output.copy()})
    return output


def majority(r, _):
    candidate, votes = None, 0
    for i, value in enumerate(r.values):
        if votes == 0:
            candidate, votes = value, 1
        elif r.compare(value, candidate, (i,), 3) == 0:
            votes += 1
        else:
            votes -= 1
        r.event("vote", f"Candidate {candidate}, vote balance {votes}.", 3, (i,), state={"candidate": candidate, "votes": votes})
    count = 0
    for i, value in enumerate(r.values):
        if r.compare(value, candidate, (i,), 4) == 0:
            count += 1
        r.event("verify", f"Verify candidate: {count} occurrence(s) so far.", 4, (i,), state={"candidate": candidate, "occurrences": count, "required_more_than": len(r.values) // 2})
    return {"value": candidate, "count": count} if count > len(r.values) // 2 else None


def two_sum(r, target):
    seen = {}
    for i, value in enumerate(r.values):
        needed = target - value
        r.event("lookup", f"Look for complement {needed} before index {i}.", 3, (i,), state={"needed": needed, "remembered_keys": list(seen)})
        if needed in seen:
            return {"indices": [seen[needed], i], "values": [needed, value]}
        seen.setdefault(value, i)
    return None


def sliding_window(r, k):
    current = sum(r.values[:k])
    best, start = current, 0
    r.event("window", f"Initial window sum: {current}.", 2, (), [0, k - 1], state={"current_sum": current, "best_sum": best})
    for end in range(k, len(r.values)):
        current += r.values[end] - r.values[end - k]
        if r.compare(current, best, (end,), 4) > 0:
            best, start = current, end - k + 1
        r.event("window", f"Window [{end-k+1}, {end}] sums to {current}.", 3, (end - k, end), [end - k + 1, end], state={"current_sum": current, "best_sum": best, "best_start": start})
    return {"sum": best, "start": start, "end": start + k - 1}


def lis(r, _):
    n = len(r.values)
    lengths, previous = [1] * n, [-1] * n
    for i in range(n):
        for j in range(i):
            if r.compare(r.values[j], r.values[i], (j, i), 4) < 0 and lengths[j] + 1 > lengths[i]:
                lengths[i], previous[i] = lengths[j] + 1, j
            r.event("dp", f"Best increasing subsequence ending at {i} has length {lengths[i]}.", 4, (j, i), state={"lengths": lengths.copy(), "previous": previous.copy()})
    if not n:
        return {"length": 0, "sequence": [], "indices": []}
    index = max(range(n), key=lambda i: lengths[i])
    indices = []
    while index != -1:
        indices.append(index)
        index = previous[index]
    indices.reverse()
    r.event("reconstruct", f"Reconstruct indices {indices}.", 5, indices, state={"lengths": lengths.copy(), "indices": indices})
    return {"length": len(indices), "sequence": [r.values[i] for i in indices], "indices": indices}


EXTRA_RUNNERS = {name: globals()[name] for name in (
    "jump", "exponential", "interpolation", "ternary", "fibonacci_search", "binary_first",
    "quick", "heap", "shell", "counting", "radix", "bucket", "cocktail", "comb", "gnome", "odd_even",
    "kadane", "prefix_sum", "running_max", "reverse", "rotate", "deduplicate", "majority", "two_sum", "sliding_window", "lis")}
