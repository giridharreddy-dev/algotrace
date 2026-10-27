# AlgoTrace

**See why code works.** A local Python lab with **32 algorithms**: 8 searches, 14 sorts and 10 array techniques, including dynamic programming.

![AlgoTrace browser lab](docs/screenshot.jpg)

## What you can do

- Search and filter a catalog of 32 algorithms by category or name. See [the complete catalog](docs/ALGORITHMS.md).
- Step through quicksort, heapsort, radix sort, Fibonacci search, Kadane's algorithm, two sum, sliding windows, LIS and more.
- Inspect array snapshots, active indices, search intervals, pseudocode, operation counters and auxiliary working state such as DP tables.
- Play, pause, scrub or reverse through a recorded trace.
- Turn on **Prediction mode** to answer before revealing comparisons and swaps, with first-answer feedback and separate skip counts.
- Build a **two-sort comparison** with synchronized playback, a shared input and value scale, and final-frame holding for the shorter trace.
- Generate seeded random, nearly sorted, duplicate-heavy, all-equal, ascending or reverse-sorted input.
- Compare 14 sorts on exactly the same input, with explicit handling of unsupported counting-sort ranges.
- Try duplicates, negative values, empty input and reverse-sorted arrays.
- Export a run as JSON. Write a learning note, save it in browser storage or download it as Markdown.
- Run algorithms through the command line without using the browser.

## Run on Windows

Requires **Python 3.10 or newer**. There are no third-party packages, API keys or accounts to configure.

1. Extract the project folder if using the ZIP.
2. Open a terminal in the project folder, or double-click `Start-AlgoTrace.bat`.
3. Run:

```powershell
python -m algotrace serve
```

4. Open **http://127.0.0.1:8765** in a browser. Keep the terminal running.
5. Stop the server with **Ctrl+C**.

If Windows uses the Python launcher, replace `python` with `py -3`. If the port is busy:

```powershell
python -m algotrace serve --port 8766
```

The server accepts its printed `127.0.0.1` address, rather than `localhost` aliases. It binds only to loopback and is intended for a single learner on their own computer. It is not a production hosting server.

## First experiment

1. Choose Bubble sort and enter `3, 2, 1`.
2. Predict the first swap, then click **Run experiment**.
3. Step forward. The completed result should show **3 comparisons, 3 swaps and 6 main-array writes**.
4. Choose **Sort input**, run again and compare the counts.
5. Click **Compare all sorts**. Explain why fewer comparisons alone do not prove an algorithm is fastest.

All searches except linear search require ascending input. Sort explicitly before running; preprocessing is excluded from search counters. Linear search, jump search and first-occurrence binary search return the first duplicate match. The other searches return any valid match.

## More experiments

- **Kadane:** use `-2, 1, -3, 4, -1, 2, 1, -5, 4`. The maximum subarray has sum 6 at indices 3–6.
- **LIS:** use `10, 9, 2, 5, 3, 7, 101, 18`. A longest strictly increasing subsequence has length 4; several answers are valid.
- **Two sum:** use `2, 7, 11, 15` with target sum 9. The pair is at indices 0 and 1.
- **Fixed window:** use `1, 2, 3, 4` with window size 2. The best sum is 7 at indices 2–3.
- **Rotation:** use `1, 2, 3, 4, 5` with positions 2. The result is `[4, 5, 1, 2, 3]`; negative positions rotate left.

## Prediction mode

![Prediction mode pauses before revealing the next operation](docs/prediction.jpg)

1. Run an experiment, enable **Prediction mode**, then use **Next** or **Play**.
2. Before a recorded comparison or swap, playback pauses and asks about the next indices, operation or comparison relation.
3. The first choice is counted once. Feedback gives the correct answer, the recorded operation and the algorithm's strategy note.
4. Choose **Continue to step** to reveal the event. **Skip and reveal** counts a skip, not a correct answer.
5. **Restart questions** resets practice and returns to the first frame. Replaying an already answered or skipped step does not count it again.

Scrubbing is disabled while prediction mode is enabled. Turn the mode off to explore freely. Questions are generated from the trace, not a separate secure assessment service. Questions and first-answer counts stay in memory for the current run, reset on a new run or changed input, and are included in the JSON run export. They are not a rating or proof of independent mastery. Traces with omitted-event gaps are not quizzed across those gaps.

## Side-by-side playback

![Two-sort synchronized playback](docs/paired.jpg)

Choose **Left sort** and **Right sort**, then **Build comparison**. Both start from a snapshot of **Your numbers**, with the same value scale. The shared controls advance **one recorded event per algorithm per tick**; a completed trace holds its final frame while the other continues.

Events vary by implementation and include narration as well as operations. This is not a stopwatch benchmark or equal-CPU-work simulation. A capped trace shows its own warning and jumps to the final completion frame. Changing input or either comparison selector clears the old pair. An unsupported counting-sort range reports an error instead of showing a partial or misleading pair. The original 14-sort count table remains available separately.

## Reproducible input presets

Expand **Input presets**, choose a shape, size **2–32** and seed **0–4294967295**, then click **Apply preset**. The same settings reproduce the same input. **New random seed** chooses a fresh seed and writes it into the field, so it can still be copied and reused.

Nearly sorted input contains exactly one adjacent inversion of an ascending sequence. Duplicate-heavy input uses at most three distinct keys; all-equal input repeats one key. The generator is deterministic educational data generation, not cryptographic randomness. Preset size is separate from the manual input limit of 128 values. Optional preset settings do not constrain a manually entered experiment.

## Counting rules and limits

- A comparison is one explicit conceptual three-way comparison of two keys or decision quantities. Loop checks, arithmetic, hash lookups, sorted-input validation and bookkeeping are not included. Zero comparisons does not mean zero work.
- A swap increments the swap count by one and main-array writes by two. Insertion and merge use writes instead of swaps.
- Auxiliary copies, bucket/count updates, hash-map updates, DP-table updates and Python container overhead are not included in main-array writes. The working-state panel exposes important intermediate quantities without implying that these counters measure all work.
- Complexity describes the particular algorithm implementation, excluding result serialization/copies, trace snapshots and UI/server overhead. Per-algorithm space and assumption notes are listed in the catalog. Quicksort uses smaller-side recursion to bound its stack, while its fixed pivot can still incur quadratic comparisons.
- Counting sort accepts a key range of at most 4096, including signed keys. The comparison table marks wider ranges as skipped instead of failing every sort. Radix and bucket sort support the full permitted signed input range.
- Input is limited to 128 integers between -1,000,000 and 1,000,000.
- A web run retains the first 500 events and always retains the completion event. When capped, a visible warning explains the jump. Algorithms still finish, and all counters include the omitted events.
- Bar heights are normalized to the current minimum and maximum; values are printed explicitly. This is an array illustration, not a zero-baseline quantitative chart.
- Comparison tables highlight the fewest key comparisons among comparison-based sorts for this input. Distribution sorts are marked separately and are excluded from that highlighting because their key-comparison count omits substantial bucket/count work. This is not a timing benchmark or universal ranking.
- Scalar, list, object and null results are displayed as JSON for array techniques. For non-mutating techniques, the chart remains the input and the separate result/state contains the answer. Kadane's empty-input convention is sum 0 with null endpoints; sliding windows require a nonempty input and 1 <= k <= n.
- Notes live in this browser's storage. They are not synced or sent to a service. Clearing browser data removes them; download a copy if needed.

## Command line

```powershell
python -m algotrace run binary --values "1,3,5,7,9" --target 7
python -m algotrace run merge --values "12,7,19,3,15,8,2,11"
python -m algotrace run bubble --values "3,2,1" --compare
python -m algotrace list --category array
python -m algotrace run lis --values "10,9,2,5,3,7,101,18"
python -m algotrace run sliding_window --values "1,2,3,4" --target 2
python -m algotrace run rotate --values "1,2,3,4,5" --target -2
```

`--target` supplies the parameter named by the selected algorithm (target key, target sum, window size, or rotation positions). For CLI values that start with a minus sign, use `--values=-3,-1,2` to avoid option parsing ambiguity.

## Tests

```powershell
python -m unittest discover -s tests -v
```

For the new pure JavaScript helpers, an optional Node.js installation can run:

```powershell
node --test tests/test_learning.mjs
```

`Run-Tests.bat` runs the Python suite and then runs the JavaScript tests when Node.js is available. Node.js is not needed to run the application itself.

Tests cover seeded comparisons with Python's sorted output, searches against reference answers, exact operation counts, input immutability, trace caps, validation, real HTTP endpoints, static file boundaries and CLI behavior. Browser verification is recorded separately in `docs/VERIFICATION.md`.

## Project map

```text
algotrace/
  algorithms.py     # Pure algorithm implementations and trace recorder
  extra.py          # Additional search, sort and array/DP implementations
  server.py         # Small loopback-only HTTP and JSON interface
  __main__.py       # Command-line entry point
  web/
    index.html      # Browser lab
    style.css       # Responsive layout
    app.js          # Playback, input, comparison and notes
    learning.mjs    # Pure prediction, preset and paired-frame helpers
tests/              # Standard-library unittest suite
docs/               # Screenshot, learning guide and verification
```

## API

- `GET /api/catalog`: algorithm metadata and pseudocode.
- `POST /api/run`: JSON `{ "algorithm": "bubble", "values": [3,2,1] }`. Include `target` for searches or parameterized array techniques.
- `POST /api/compare`: JSON `{ "values": [3,2,1] }`, returns 14 sort summaries. A summary has a `skipped` reason when a sort's range requirement is not met.

Requests must come through the printed address. The app rejects mismatched Host/Origin headers, non-JSON POST bodies and oversized requests. These are narrow local-app protections, not a claim of a complete security audit.

## Authorship and learning

This initial implementation was built with AI assistance. It is a learning/reference project, not evidence that the owner independently wrote or mastered every part. Read `docs/LEARNING.md`, explain the existing code, and make your own documented changes before presenting it as an independent accomplishment. No solved-problem history, user metrics or test outcomes are fabricated.

## License

MIT. See `LICENSE`.
