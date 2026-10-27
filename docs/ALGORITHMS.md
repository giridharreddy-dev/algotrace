# Algorithm catalog — AlgoTrace 2.0

32 implementations: 8 searches, 14 sorts and 10 array techniques.

Complexities describe this implementation, excluding trace snapshots, response copies and UI overhead. Average-case assumptions are part of each note; asterisked bounds require those notes. Hash lookups and auxiliary updates are not counted as key comparisons or main-array writes.

## Reading the labels

- **n** is the number of input values. **k** is counting sort's key-range size. **d** is radix sort's number of processed digits.
- **O(...)** describes an asymptotic upper growth bound, ignoring constant factors; it is not an exact operation count or a stopwatch measurement.
- **Extra space** means temporary algorithm storage beyond the input, with the exclusions above. Bounds refer to the code here, not every possible implementation of a named algorithm.
- **Stable sorting** preserves the order of records with equal keys. This app accepts integer keys only, so attached-record stability is an algorithm property rather than a separate record-sorting feature.
- **DP (dynamic programming)** stores reusable answers to smaller subproblems. LIS stores the best sequence length ending at each index.
- **Preprocessing** is preparation such as sorting before a search. It is a separate operation and is not hidden inside search counters.

## Searching · 8

| CLI/API identifier | Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- | --- |
| `linear` | Linear search | O(1) | O(n) | O(n) | O(1) |
| `binary` | Binary search | O(1) | O(log n) | O(log n) | O(1) |
| `jump` | Jump search | O(1) | O(√n) | O(√n) | O(1) |
| `exponential` | Exponential search | O(1) | O(log n) | O(log n) | O(1) |
| `interpolation` | Interpolation search | O(1) | O(log log n)* | O(n) | O(1) |
| `ternary` | Ternary search (sorted keys) | O(1) | O(log n) | O(log n) | O(1) |
| `fibonacci_search` | Fibonacci search | O(log n) | O(log n) | O(log n) | O(1) |
| `binary_first` | Binary search · first occurrence | O(log n) | O(log n) | O(log n) | O(1) |

### Linear search

Works on unsorted data. Returns the first matching index, or -1.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
for each index i:
    compare values[i] with target
    if equal: return i
return -1
```

### Binary search

Requires ascending input. Returns one matching index; duplicates need not return the first. Sorting cost is not included.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
low = 0; high = length - 1
while low <= high:
    mid = (low + high) // 2
    compare values[mid] with target
    if equal: return mid
    if smaller: low = mid + 1
    otherwise: high = mid - 1
return -1
```

### Jump search

Jump by √n, then scan the candidate block. Returns the first match. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
step = floor(sqrt(n)); start = 0
jump while block's last key < target
scan this block left to right
return first match, or -1
```

### Exponential search

Double the search bound, then binary-search the bracket. Returns any match. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
check the first key
double bound while key < target
binary-search the bounded interval
return a match, or -1
```

### Interpolation search

*Average assumes roughly uniform numeric keys. Estimate a probe from key values; equal endpoints are handled. Returns any match. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
low = 0; high = n - 1
check target is between endpoint keys
if endpoint keys equal: check that key
estimate probe using target's relative value
compare probe; narrow interval
return a match, or -1
```

### Ternary search (sorted keys)

Split an interval at two probes to find an exact key. This is not unimodal-function optimization. Returns any match. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
while interval is nonempty:
    select one-third and two-third probes
    compare target with both probes
    retain the only possible third
return -1 if no match
```

### Fibonacci search

Use Fibonacci-sized intervals rather than midpoint division. Returns any match. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
grow Fibonacci numbers until F >= n
probe offset + F(previous previous)
if smaller: move offset and shrink right
if larger: shrink left
check the last possible key
return match or -1
```

### Binary search · first occurrence

Keep a match and continue left to locate the first duplicate. Requires ascending input; preprocessing is excluded.

Parameter: **Target value**, passed as `target` in JSON or `--target` on the CLI.

```text
low = 0; high = n - 1; answer = -1
while low <= high:
    compare midpoint with target
    if equal: save answer and continue left
    otherwise: discard an impossible half
return answer
```

## Sorting · 14

| CLI/API identifier | Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- | --- |
| `bubble` | Bubble sort | O(n) | O(n²) | O(n²) | O(1) |
| `insertion` | Insertion sort | O(n) | O(n²) | O(n²) | O(1) |
| `selection` | Selection sort | O(n²) | O(n²) | O(n²) | O(1) |
| `merge` | Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| `quick` | Quicksort | O(n log n) | O(n log n)* | O(n²) | O(log n) |
| `heap` | Heap sort | O(n)* | O(n log n) | O(n log n) | O(1) |
| `shell` | Shell sort | O(n log n) | Gap-dependent | O(n²) | O(1) |
| `counting` | Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) |
| `radix` | Radix sort · LSD base 10 | O(d(n + 10)) | O(d(n + 10)) | O(d(n + 10)) | O(n + 10) |
| `bucket` | Bucket sort | O(n) | O(n)* | O(n²) | O(n) |
| `cocktail` | Cocktail shaker sort | O(n) | O(n²) | O(n²) | O(1) |
| `comb` | Comb sort | O(n log n) | Gap-dependent | O(n²) | O(1) |
| `gnome` | Gnome sort | O(n) | O(n²) | O(n²) | O(1) |
| `odd_even` | Odd-even transposition sort | O(n) | O(n²) | O(n²) | O(1) |

### Bubble sort

Adjacent swaps move the largest remaining value right. An unchanged pass stops early. Stable.

```text
for end from length - 1 down to 1:
    changed = false
    for i from 0 to end - 1:
        compare values[i] and values[i + 1]
        if out of order: swap; changed = true
    if unchanged: stop
```

### Insertion sort

Insert each value into a sorted prefix. Good for small or nearly sorted inputs. Stable.

```text
for i from 1 to length - 1:
    key = values[i]; j = i - 1
    while j >= 0 and values[j] > key:
        values[j + 1] = values[j]; j -= 1
    values[j + 1] = key
```

### Selection sort

Find the smallest remaining value, then put it at the front. This swap-based implementation is not stable.

```text
for start from 0 to length - 2:
    minimum = start
    for i from start + 1 to length - 1:
        if values[i] < values[minimum]: minimum = i
    if minimum differs: swap with start
```

### Merge sort

Recursively split and merge sorted halves. Stable. Auxiliary copies and the call stack are omitted from the main-array write counter.

```text
sort(low, high):
    if interval has at most one value: return
    mid = (low + high) // 2
    sort(low, mid); sort(mid, high)
    copy both sorted halves
    compare fronts; write smaller to values
    write any remaining values
```

### Quicksort

Lomuto partition with the final value as pivot. *Average assumes random input order. Smaller-part recursion bounds stack depth; equal/sorted keys can still cost quadratic work. Not stable.

```text
choose final value as pivot
scan: move keys <= pivot to the left
put pivot at its final position
recurse on the smaller partition
iterate over the larger partition
```

### Heap sort

Build a max heap; move its root to the end and restore the heap. *All-equal keys permit early-stop sifts and linear best-case work here. Not stable.

```text
build max heap from bottom to top
swap root with final unsorted value
sift the new root down
repeat for the smaller heap
```

### Shell sort

Uses gaps n//2, n//4, …, 1 with gapped insertion. Complexity depends on the gap sequence. Not stable.

```text
gap = n // 2
perform insertion sort across each gap
halve the gap
stop after gap 1
```

### Counting sort

k = max - min + 1, capped at 4096. Supports negative values by an offset. Reconstructs integer keys; it does not preserve attached-record order. Distribution work is not captured by key comparisons alone.

```text
find minimum and maximum
count each key at key - minimum
visit counts in ascending key order
write each key its recorded number of times
```

### Radix sort · LSD base 10

Stable digit buckets. Subtract the minimum to support signed integers; d is the number of digits in the shifted maximum. Auxiliary bucket work is not key comparison work.

```text
find minimum; use key - minimum for digits
for each digit, from least significant:
    distribute keys into 10 stable buckets
    flatten buckets back into the array
```

### Bucket sort

n numeric-range buckets, each sorted using insertion sort. *Average assumes uniformly distributed keys. Stable. Bucket writes are auxiliary, not main-array writes.

```text
find range; allocate n buckets
distribute keys by their numeric range
insertion-sort each bucket
flatten buckets into the main array
```

### Cocktail shaker sort

Bubble in both directions, settling a value at either end per sweep. Stable.

```text
sweep left to right, swapping inversions
reduce the right boundary
sweep right to left, swapping inversions
increase the left boundary; stop if unchanged
```

### Comb sort

Shrink a comparison gap by about 1.3; finish with adjacent passes until unchanged. Not stable. Average bounds depend on the gap policy.

```text
gap = n; changed = true
shrink gap to max(1, gap * 10 // 13)
compare and swap keys separated by gap
repeat until gap 1 has no swaps
```

### Gnome sort

Move forward when neighbors are ordered; otherwise swap and step back. Stable.

```text
position = 1
if at start or neighbors ordered: step forward
otherwise: swap neighbors; step backward
stop at the end
```

### Odd-even transposition sort

Alternate odd and even adjacent pairs until neither pass swaps anything. This implementation is sequential. Stable.

```text
repeat:
    compare and swap odd adjacent pairs
    compare and swap even adjacent pairs
stop after a complete unchanged round
```

## Array techniques · 10

| CLI/API identifier | Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- | --- |
| `kadane` | Maximum subarray · Kadane | O(n) | O(n) | O(n) | O(1) |
| `prefix_sum` | Prefix sums | O(n) | O(n) | O(n) | O(1)* |
| `running_max` | Running maximum | O(n) | O(n) | O(n) | O(1)* |
| `reverse` | Array reversal · two pointers | O(n) | O(n) | O(n) | O(1)* |
| `rotate` | Array rotation · three reversals | O(1)* | O(n) | O(n) | O(1)* |
| `deduplicate` | Remove duplicates · hash set | O(n)* | O(n)* | O(n)* | O(n) |
| `majority` | Majority element · Boyer–Moore | O(n) | O(n) | O(n) | O(1) |
| `two_sum` | Two sum · hash map | O(n)* | O(n)* | O(n)* | O(n) |
| `sliding_window` | Maximum fixed-window sum | O(n) | O(n) | O(n) | O(1) |
| `lis` | Longest increasing subsequence · DP | O(n²) | O(n²) | O(n²) | O(n) |

### Maximum subarray · Kadane

Find a nonempty contiguous subarray with maximum sum. Empty input returns sum 0 with null endpoints. Ties keep an earlier discovered optimum.

```text
start a sum at the first value
extend the previous sum or start here
update the best sum and endpoints
return sum, start and end
```

### Prefix sums

Each position becomes the sum through that index. *Mutates the working array; the returned copy and recorder snapshots are excluded.

```text
total = 0
for each value:
    total += value
    write total at this position
```

### Running maximum

Each position becomes the maximum seen so far. *Mutates the working array; result-copy and trace storage are excluded.

```text
best = first value
for each next value: compare with best
write the current best at each position
```

### Array reversal · two pointers

Swap the two endpoints and move inward. *Result-copy and trace storage are excluded.

```text
left = 0; right = n - 1
while left < right:
    swap endpoints
    left += 1; right -= 1
```

### Array rotation · three reversals

Positive positions rotate right; negative positions rotate left. Reduce positions modulo n. *Zero effective rotation needs only constant algorithm work; result-copy and trace storage are excluded.

Parameter: **Positions (right)**, passed as `target` in JSON or `--target` on the CLI.

```text
k = positions modulo n
reverse the whole array
reverse the first k values
reverse the remaining values
```

### Remove duplicates · hash set

Keep first occurrences in input order. *Expected time assumes average constant-time hashing. The chart retains input; the result is a separate list. Hash lookups are not key comparisons.

```text
seen = set(); output = []
for each value: look it up in seen
if new: remember it and append to output
return output
```

### Majority element · Boyer–Moore

Cancel unequal votes, then verify the candidate occurs more than n/2 times. Returns null when no majority exists.

```text
candidate = none; votes = 0
if no votes: choose this value
equal value adds a vote; unequal cancels one
count the candidate in a second pass
return it only if count > n // 2
```

### Two sum · hash map

Find two distinct input indices whose values add to the target. *Expected hashing time. Returns the first pair discovered or null. The input is unchanged; hash lookups are not key comparisons.

Parameter: **Target sum**, passed as `target` in JSON or `--target` on the CLI.

```text
remembered = map of value to first index
for each index i:
    look up target - values[i]
    if found: return the two indices
    otherwise remember this value
return null
```

### Maximum fixed-window sum

For window size k, add the entering value and subtract the leaving value. Requires 1 <= k <= n. Returns the best sum and its endpoints.

Parameter: **Window size (k)**, passed as `target` in JSON or `--target` on the CLI.

```text
sum the first k values
record that first window
slide: add entering key, subtract leaving key
update best sum and start
return best window
```

### Longest increasing subsequence · DP

Strictly increasing: equal values do not extend a sequence. Dynamic programming stores a length and predecessor per position. Returns a reconstructed sequence. State shows the DP table.

```text
length[i] = 1; previous[i] = none
for each position i:
    inspect each earlier j
    if values[j] < values[i]: try extending j
reconstruct a best sequence via predecessors
```
