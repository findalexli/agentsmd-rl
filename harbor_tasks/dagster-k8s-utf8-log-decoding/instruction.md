# Fix UTF-8 Decoding in dagster-k8s Log Stream Processing

## Problem

The dagster-k8s library in the Dagster repository at `/workspace/dagster` has a bug in its Kubernetes pod log stream processing. When Kubernetes returns log data as a stream of byte chunks, multi-byte UTF-8 characters can be split across chunk boundaries. The current code decodes each chunk independently, causing a `UnicodeDecodeError` when it encounters an incomplete UTF-8 byte sequence at a chunk boundary.

## Expected Behavior

The log stream processor parses Kubernetes-formatted log lines (RFC timestamp followed by a space and the message content) and yields `LogItem` objects with `timestamp` and `log` fields. It must correctly reassemble and decode UTF-8 multi-byte characters even when their bytes are distributed across multiple chunks.

The following scenarios must all work:

1. **Ellipsis split across two chunks**: Stream yields `b"2024-03-22T02:17:29.885548Z hello " + b"\xe2"` then `b"\x80\xa6 world\n"`. Expected: one `LogItem` with `timestamp="2024-03-22T02:17:29.885548Z"` and `log="hello … world"`.

2. **Ellipsis split across three chunks**: The ellipsis character (U+2026, encoded as bytes `e2 80 a6`) arriving one byte per chunk. Expected: `log="start … end"` with timestamp `"2024-03-22T02:17:29.885548Z"`.

3. **Multiple characters split differently**: Euro sign (€, bytes `e2 82 ac`) split after two bytes, then em dash (—, bytes `e2 80 94`) starting in the same chunk as the Euro's final byte. Expected: `log="price: €, note— end"`.

4. **CJK character split**: "中" (bytes `e4 b8 ad`) split after two bytes. Expected: `log="中 test"` with timestamp `"2024-03-22T02:17:29.885548Z"`.

5. **Incomplete UTF-8 at stream end**: Stream yields `b"2024-03-22T02:17:29.885548Z hello " + b"\xe2\x80"` with no trailing newline and no final byte. Expected: the incomplete sequence is handled gracefully using Unicode replacement character `U+FFFD` (�) or discarded, without raising an exception.

6. **Multiple lines with split characters**: Two consecutive log lines (timestamps `"2024-03-22T02:17:29.885548Z"` and `"2024-03-22T02:17:30.885548Z"`), each with a split UTF-8 character, produce two separate `LogItem` objects. Expected: first has `log="line1 …"`, second has `log="line2 €"`.

7. **Single-chunk logs unchanged**: Log lines arriving in complete, non-split chunks must continue to work as before, including multi-line logs.

8. **Continuation lines with UTF-8**: A continuation chunk (no timestamp prefix) containing a UTF-8 character appended to the current log. Example: second chunk `b"\xe2\x80\xa6 continuation\n"` yields `log="start … continuation"`.

## Validation

After making changes, run:

```bash
cd /workspace/dagster
python -m pytest python_modules/libraries/dagster-k8s/dagster_k8s_tests/unit_tests/ -v --tb=short
```

Also run `make ruff` to format the code per the repository's standards.
