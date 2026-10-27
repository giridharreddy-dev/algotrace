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
- Why can radix sort do substantial work without many key comparisons?
- Why does first-occurrence binary search keep searching after a match?
- Why does Kadane's algorithm work on an all-negative input without returning an empty subarray?
- What does `lengths[i]` mean in LIS, and why do duplicate keys not extend it?

## Three independent extensions

Do one at a time, writing tests before calling the work complete.

1. **Last occurrence:** extend the existing first-occurrence binary search to return the last duplicate match. Test either boundary, all-equal input and missing targets.
2. **Explain the mistake:** extend the existing prediction mode with one targeted misconception explanation for each incorrect choice.
3. **Compare input shapes:** extend the existing presets with a summary chart that compares the same sorts on several input shapes at the same size. Keep dataset generation separate from sorting.

## Honest portfolio description

After you understand and extend the code, describe your actual contribution. For example: “Extended a Python algorithm lab with first-occurrence binary search and boundary-case tests.” Do not claim that a generated codebase alone demonstrates independent algorithm mastery.
