# Improve &str to Digest error message

## Problem

When parsing a digest string (base58-encoded) into a Digest type, the current error message is not helpful for debugging:

```
Invalid digest length. Expected 32 bytes
```

This message doesn't tell you:
- What the actual decoded length was
- What input string caused the error
- Whether the input was too short or too long

## Task

Improve the error messages when a `Digest` cannot be created from a `&str` and centralize the parsing logic.

### Files to Modify

- `crates/sui-types/src/digests.rs` - Contains multiple digest types that parse from base58 strings

### Requirements

1. **Create a centralized helper function** `digest_from_base58(s: &str) -> anyhow::Result<[u8; 32]>` that:
   - Decodes the base58 string
   - Returns detailed error messages with actual decoded length
   - For short inputs (< 32 bytes): include the full input and actual length
   - For long inputs (> 32 bytes): include truncated input (first 32 chars) and actual length
   - Returns the decoded 32-byte array on success

2. **Refactor all digest types** to use this helper function instead of inline parsing logic:
   - `CheckpointDigest::from_str`
   - `CheckpointContentsDigest::from_str`
   - `TransactionDigest::from_str`
   - `TransactionEffectsDigest::from_str`
   - `TransactionEventsDigest::from_str`
   - `EffectsAuxDataDigest::from_str`
   - `ObjectDigest::from_str`

3. **Add unit tests** for the new helper function covering:
   - Exactly 32 bytes (success case)
   - Less than 32 bytes (error with actual length)
   - More than 32 bytes (error with actual length and truncation)

### Expected Error Message Format

For short input (31 bytes decoded from "111...1" x31):
```
Invalid digest length. Expected base58 string that decodes into 32 bytes, but [1111111111111111111111111111111] decodes into 31 bytes
```

For long input (33 bytes decoded from "111...1" x33):
```
Invalid digest length. Expected base58 string that decodes into 32 bytes, but [11111111111111111111111111111111] (truncated) decodes into 33 bytes
```

## Testing

Run the sui-types tests to verify your changes:
```bash
cargo test -p sui-types --lib
```

Make sure all tests pass and the new unit tests for `digest_from_base58` are included.
