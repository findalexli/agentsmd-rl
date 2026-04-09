# Fix UTF-8 Decoding in K8s Log Stream Processing

## Problem

The `_process_log_stream` function in `python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py` has a bug when processing Kubernetes pod logs. When multi-byte UTF-8 characters are split across log chunks (which commonly happens with container log streaming), the function either:
- Raises a `UnicodeDecodeError` and crashes
- Or produces corrupted/mangled output

This happens because the current implementation uses `chunk.decode("utf-8")` on each chunk individually, which fails when a multi-byte UTF-8 sequence is split across chunk boundaries.

## Example of the Bug

If a container emits the UTF-8 ellipsis character "…" (which is 3 bytes: `e2 80 a6`), and the k8s log stream splits it between two chunks:
- Chunk 1 ends with: `\xe2` (first byte)
- Chunk 2 starts with: `\x80\xa6` (remaining bytes)

The current code crashes when trying to decode Chunk 1 alone.

## Your Task

Fix the `_process_log_stream` function to handle UTF-8 characters that span across log chunk boundaries.

**Key requirements:**
1. Use an incremental UTF-8 decoder that can buffer partial character sequences
2. Handle invalid byte sequences gracefully (replace with replacement character `` rather than crashing)
3. Maintain all existing log parsing behavior (timestamp handling, line continuations, etc.)

## Relevant Files

- **Primary file to modify**: `python_modules/libraries/dagster-k8s/dagster_k8s/pipes.py`
- The function to fix: `_process_log_stream(stream: Iterator[bytes]) -> Iterator[LogItem]`

## Tips

- Look at Python's `codecs` module for incremental decoding
- The `errors="replace"` parameter is useful for handling invalid bytes
- The fix should not change the function signature or return type
- Run `make ruff` after making changes to ensure code quality
