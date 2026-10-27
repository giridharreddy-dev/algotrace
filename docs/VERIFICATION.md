# Verification — AlgoTrace 2.1, 28 October 2026

Environment: Windows, Python 3.14.3, a local in-app browser, and Node.js for JavaScript syntax checking. No third-party Python packages are required.

## Automated results

`python -m unittest discover -s tests -v`: **33 test methods passed**.

- All 32 catalog identifiers have distinct implementations, metadata and pseudocode. Categories contain 8 searches, 14 sorts and 10 array techniques.
- All sorts matched Python's `sorted` on seeded examples. Additional exhaustive small-array checks cover duplicates and negative keys. Boundary tests cover 128 items and extreme signed keys; counting sort's bounded range is tested separately.
- All eight searches matched reference expectations on exhaustive small sorted arrays with duplicate keys, plus empty, boundary and large-equal cases. First-occurrence searches specifically return the first matching index.
- Kadane's maximum sum, majority element, two sum, fixed-window sums and LIS were checked against independent brute-force or enumeration references.
- Prefix sums, running maxima, reversal, signed rotation and deduplication were checked against reference results.
- Exact counters, caller-list immutability, trace caps, state-snapshot independence, active indices and pseudocode line ranges passed.
- Real HTTP requests exercised all 32 algorithms, the catalog, assets, comparison endpoint, malformed JSON, invalid parameters, body-size limits, Host/Origin checks and the static file allowlist.
- Wide-range sort comparison returns a counting-sort skip reason while still completing the other 13 algorithms.
- CLI checks cover search, empty sort comparison, invalid input, category listing and parameterized array operations.

`node --check algotrace/web/app.js`: passed.

## Learning features — 2.1.0

- **33 Python tests and 13 JavaScript tests passed.** The updated Windows `Run-Tests.bat` was executed through CMD, ran both suites and returned exit code 0.
- JavaScript helpers test deterministic preset generation, shape properties, invalid seeds/sizes, prediction choice generation and grading, capped-event gaps, paired tick alignment and shorter-trace holding.
- The new local `/learning.mjs` asset was included in the HTTP asset checks. Application JavaScript syntax and Python compilation checks passed.
- In the browser, prediction mode stopped at the first comparison while the counters remained at zero. An incorrect first answer gave the right indices and explanation without credit; a correct next answer earned one credit; a skip increased only the skip counter.
- Replaying answered/skipped events did not increase the score again. Restart reset the practice and trace position. Automatic playback paused at a prediction question. Disabling prediction mode restored ordinary scrubbing.
- Two applications of Seeded random / size 12 / seed 77 produced the identical input. All-equal and nearly sorted presets produced their expected shapes. Size 33 produced an explanatory error. Invalid optional preset settings did not block a manually entered run.
- Bubble sort and merge sort on `[3, 2, 1]` both displayed `[1, 2, 3]`. At shared tick 10 of 14, bubble sort held its completion frame while merge sort displayed event 10. Final counters matched the reference values.
- Paired automatic playback advanced, pause stopped it, and changing the input cleared the old comparison. Empty paired input completed as `[]` on both sides. An unsupported counting-sort range displayed a side-specific error and recovered when the selection changed.
- Saved version-1 demo notes remained available. No browser error-level logs were reported during the learning-feature checks.
- All 32 algorithms were rerun through the updated interface in ordinary playback mode; every run completed and displayed its expected result representation. `BROWSER-CHECKS.json` now records this version-2.1 regression pass.
- The exported JSON was downloaded and parsed; its practice object accurately contained one correct first answer out of one attempt and no skips from the demonstration run.
- Prediction choices, feedback and stacked comparison cards were inspected at 390 pixels wide, with no document-level horizontal overflow. Desktop paired charts were inspected at 1280 × 900. Temporary viewport overrides were reset afterward.

This practice score is local first-answer feedback, not an assessment rating. Paired ticks align recorded events, not time or equal units of CPU work.

## Browser results for version 2

- All 32 options were selected, run and scrubbed to completion through the normal UI on `[1, 2, 2, 3, 5]`. Searches used target 2; parameterized array techniques used their displayed defaults. The captured results are in `BROWSER-CHECKS.json`.
- All 14 sorts displayed `[1, 2, 2, 3, 5]`; search results were valid duplicate-match indices; array results rendered correctly as lists, objects or null.
- Category filtering and algorithm search worked. A nonexistent query displayed zero matches and disabled Run; clearing/replacing the query recovered normally.
- Kadane's example `[-2, 1, -3, 4, -1, 2, 1, -5, 4]` displayed sum 6 at indices 3–6, with the working state showing the best interval.
- Comparing `[-1000000, 0, 1000000]` displayed 14 rows: counting sort was skipped with its range explanation; the other 13 completed. Distribution sorts were marked separately and excluded from comparison-only winner highlighting.
- The existing saved demo note survived the version update.
- No browser error-level logs were reported during this inspection.

## Retained version 1 checks

Playback, pause, reverse stepping, JSON export, saved-note refresh persistence, the visible large-trace truncation warning, empty sorting input and the 390-pixel layout were checked in version 1. Version 2's changed controls and working-state panel were additionally inspected at desktop and narrow widths before publication. This is not a complete cross-browser or accessibility audit.

## Scope

This is an educational local application. It is not validated as a production hosting server, and tests do not establish the owner's independent mastery. Operation counters intentionally omit loop conditions, arithmetic, hash lookups and auxiliary-table updates. Complexity excludes tracing, serialization and result-copy overhead. Notes remain in local browser storage.

## Blue-and-white theme — 2.0.1

- Replaced the palette in all form, trace, state, comparison and navigation styles; updated the logo and typography.
- Inspected the narrow layout and the desktop breakpoint at a 1280 × 800 viewport, then reset the viewport override.
- Verified a trace's blue active bars and playback controls, and completed a 14-sort comparison with no browser error-level logs.
- Algorithm implementations were not changed for this visual update. The 33-test algorithm/API/CLI results above are retained; the backend suite was not rerun for a stylesheet-only behavior change.
