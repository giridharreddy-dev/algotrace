# Changes

## 2.1.0 — 28 October 2026

- Added prediction questions before recorded comparisons/swaps, first-answer feedback, separate skips, replay protection and practice data in JSON exports.
- Added synchronized playback for any two supported sorts, shared input/value scales, independent trace-cap warnings and final-frame holding.
- Added six reproducible input presets with visible seed and size controls, including nearly sorted, duplicate-heavy and all-equal data.
- Added pure JavaScript learning helpers and 13 Node test cases, served as a local module without a new runtime dependency.
- Kept saved notes compatible, added keyboard focus handling for questions, and prevented optional preset constraints from blocking manual experiments.

## 2.0.1 — 28 October 2026

- Replaced the sage/cream/orange palette with white panels, navy text and blue accents throughout the browser interface.
- Improved text contrast, active-step emphasis and focus indicators; simplified the logo and removed decorative serif typography.
- Reorganized the stylesheet into readable sections and reusable color tokens. Algorithm behavior is unchanged.

## 2.0.0 — 28 October 2026

- Expanded from 6 to 32 algorithms: 8 searches, 14 sorts and 10 array techniques.
- Added category filtering, algorithm-name search and a CLI catalog command.
- Added working-state snapshots for DP tables, search spans, candidates, buckets and sums.
- Supported structured array results, parameter labels, negative rotations and strict input preconditions.
- Expanded sort comparison to 14 algorithms, separated distribution sorts from comparison-only highlighting, and explained unsupported counting-sort ranges.
- Added exhaustive and brute-force reference tests, complete catalog documentation and recorded browser runs for all 32 algorithms.
- Preserved the existing local-note storage format and the bounded trace recorder.

## 1.0.0 — 28 October 2026

- Initial offline Python lab with two searches, four sorts, trace playback, comparisons, notes, CLI and tests.
