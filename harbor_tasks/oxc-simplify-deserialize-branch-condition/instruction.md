# Simplify Branch Condition in deserializeStr

The raw transfer deserializer in OXC has a function `deserializeStr` that extracts strings from a raw buffer. The current implementation uses two separate variables (`sourceIsAscii` and `firstNonAsciiPos`) to track whether bytes are ASCII. This redundancy makes the branch condition more complex than necessary.

## The Problem

The branch condition in `deserializeStr` computes ASCII tracking separately in two places, but the information is ultimately redundant. When the source is entirely ASCII, `firstNonAsciiPos` already equals the boundary. When there are non-ASCII bytes, `firstNonAsciiPos` marks the first such byte. The current condition `pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos)` can be reduced to a simpler form that doesn't require a separate ASCII flag variable.

## Expected Outcome

The deserializer should still correctly handle:
1. ASCII-only source text (fast path for all strings)
2. Source text with non-ASCII characters (fast path only for strings in ASCII prefix)
3. Empty strings
4. UTF-8 decoding for strings containing non-ASCII bytes

The code generator at `tasks/ast_tools/src/generators/raw_transfer.rs` produces JavaScript deserializer files. The generated files are located at:
- `apps/oxlint/src-js/generated/deserialize.js`
- `napi/parser/src-js/generated/deserialize/*.js` (8 files)

These generated files have "DO NOT EDIT DIRECTLY" headers, but for this task you may modify them directly to implement the fix.

## Note on Test Requirements

The test suite checks for specific patterns in the modified files. The patterns include exact variable declarations and condition forms. Reviewing the test file at `tests/test_outputs.py` will clarify what patterns the tests expect.