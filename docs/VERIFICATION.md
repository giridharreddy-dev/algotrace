# Verification — 28 October 2026

Environment: Windows, Python 3.14.3, a local in-app browser, and Node.js for a JavaScript syntax check. No third-party Python dependency was installed.

## Automated results

`python -m unittest discover -s tests -v`: **16 test methods passed**.

- All four sorts matched Python's `sorted` on 106 inputs each (424 sort cases): empty, singleton, duplicates, negatives, ascending, descending and seeded random arrays.
- Linear and binary searches matched reference expectations over 1,000 search cases. Linear returns the first match; binary returns a valid match or -1.
- Exact operation counters were checked on a known three-value example.
- A 128-value descending bubble-sort input completed with 8,128 comparisons and 8,128 swaps even when its recorded trace was capped.
- Input validation, caller-list immutability, independent trace snapshots and monotonic counters passed.
- Real HTTP requests tested assets, catalog, run/compare, malformed input, body size, Host/Origin checks and the static allowlist.
- CLI checks covered successful search, sort comparison with empty input and an invalid unsorted binary-search request.

`node --check algotrace/web/app.js`: passed.

## Browser checks

- Initial lab rendered with all six algorithm choices, input, counters, chart and pseudocode.
- Bubble sort on `[3, 2, 1]`: stepping displayed the first comparison; the final frame displayed `[1, 2, 3]`, 3 comparisons, 3 swaps and 6 writes.
- Four-sort comparison displayed the expected counts for that same input.
- Binary search rejected `[3, 2, 1]` and explained the ascending-input requirement.
- After explicitly sorting to `[1, 2, 3]`, target 2 returned index 1 with one comparison.
- A note explicitly labeled “Demo note” was saved and restored after refresh.
- Play advanced through multiple events; pause stopped it. Range navigation reached the final frame.
- JSON run export downloaded successfully; its parsed result and 54 recorded events matched the default eight-value example.
- A large reverse input showed 15,884 omitted intermediate events and retained the correct final sorted array and complete counts.
- Empty input completed as `[]`.
- A 390-pixel-wide viewport was inspected. Playback controls wrap to fit; there was no document-level horizontal overflow. The viewport was reset afterward.
- No browser error-level logs were reported during inspection.

## Scope

These checks validate this educational implementation. They do not establish production hosting readiness, cross-browser compatibility, a full accessibility audit, or independent mastery by the owner. Notes use local browser storage; no account or cross-device sync exists.
