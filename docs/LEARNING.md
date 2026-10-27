# Make AlgoTrace your own

## The four parts

1. **Algorithm:** the rule for solving a problem. Example: linear search checks items one by one.
2. **Recorder:** a notebook that takes a copy of the array and counters after an event. It never decides the next algorithm step.
3. **Server:** the local messenger that accepts JSON requests and returns Python results.
4. **Browser:** the player that displays previously recorded events. Moving the slider does not run the algorithm again.

```text
Numbers in the form → JSON request → Python algorithm + recorder
                                            ↓
Browser playback ← JSON response with snapshots and counters
```

## Start with one function

Read `linear` in `algotrace/algorithms.py`. Before running it on `[8, 3, 5]` with target `3`, predict:

- Which indices are visited?
- How many key comparisons occur?
- What index is returned?

Then run the CLI or browser and check the prediction. Repeat with target `9` and an empty list.

## Questions you should be able to answer

- Why does binary search reject unsorted input?
- What is the difference between one swap and one write?
- Why can insertion sort's temporary array snapshots contain duplicate values during a shift? Where is the held key?
- Why is an early-stop bubble pass useful on a sorted array?
- Why can two algorithms with the same O(n²) worst case do different work on this input?
- Why does counting comparisons not measure total runtime?
- Why does trace storage use more memory than the underlying algorithm alone?
- Why are merge comparisons described by values rather than active main-array indices? (They use copied halves.)

## Three independent extensions

Do one at a time, writing tests before calling the work complete.

1. **First occurrence:** add a binary-search mode that returns the first duplicate match. Test a match at either boundary, all-equal input and missing targets.
2. **Find the mistake:** add a prediction question before selected steps, showing feedback only after the learner answers.
3. **Compare input shapes:** run the same sorts on ascending, descending, duplicate-heavy and random input of the same size. Explain that generating a dataset is separate from sorting it.

## Honest portfolio description

After you understand and extend the code, describe your actual contribution. For example: “Extended a Python algorithm lab with first-occurrence binary search and boundary-case tests.” Do not claim that a generated codebase alone demonstrates independent algorithm mastery.
