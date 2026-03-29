# Fix parse_lscpu_topology() crash on malformed lines

## Bug Description

The `parse_lscpu_topology()` function in `python/sglang/srt/utils/common.py` crashes with a `ValueError` when parsing `lscpu` output that contains malformed lines.

The current implementation uses:

```python
cpu, core, socket, node = map(int, line.strip().split(","))
```

This fails when:
- A line has fewer or more than 4 comma-separated values
- A line contains empty fields (e.g., `"0,1,,0"`)

## Expected Fix

1. **Skip malformed lines**: If a line does not have exactly 4 comma-separated fields, log a warning and skip it.
2. **Handle empty fields**: For lines with 4 fields but some empty values, default those empty fields to `0`. The CPU field (first field) must always be present as a valid integer.
3. The function should continue processing remaining lines after encountering a malformed one, rather than crashing entirely.

## File to Modify

`python/sglang/srt/utils/common.py` — the `parse_lscpu_topology` function (around line 3378).
