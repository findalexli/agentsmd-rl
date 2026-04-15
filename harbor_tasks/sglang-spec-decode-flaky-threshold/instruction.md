# Flaky standalone speculative decoding GSM8K accuracy test

## Problem

The standalone speculative decoding test (`test_standalone_speculative_decoding.py`) is flaky in CI. The `test_gsm8k` method in both `TestStandaloneSpeculativeDecodingBase` and `TestStandaloneV2SpeculativeDecodingBase` intermittently fails with an error like:

```
AssertionError: 0.7 not greater than 0.7
```

This happens when the GSM8K accuracy score lands exactly on the threshold boundary. Across multiple CI runs, scores in the 0.69–0.74 range have been observed, and the current strict `>` comparison rejects scores that equal the threshold exactly.

## Expected Behavior

The test should use a comparison that accepts scores equal to the threshold. The threshold must be set to a value that accommodates the observed score floor of approximately 0.69 — meaning the threshold itself must be no higher than 0.69 to ensure scores at that level are not rejected. Both the V1 and V2 speculative decoding test base classes need the same fix.

## Files to Look At

- `test/registered/spec/test_standalone_speculative_decoding.py` — contains the `TestStandaloneSpeculativeDecodingBase` and `TestStandaloneV2SpeculativeDecodingBase` classes with their `accuracy_threshold` class attribute and `test_gsm8k` method