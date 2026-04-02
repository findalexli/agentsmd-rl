# SizeDict missing merge/union operator support

## Problem

The `SizeDict` dataclass in `src/transformers/image_utils.py` implements several dict-like dunder methods (`__getitem__`, `__setitem__`, `__contains__`, `__eq__`, `__iter__`, etc.) but is missing support for the merge operator (`|`).

Downstream libraries (e.g., vLLM) use the `|` operator to merge size configurations. When they do something like:

```python
base_size = SizeDict(height=10, width=20)
override = {"longest_edge": 30}
merged = base_size | override
```

This raises a `TypeError` because `SizeDict` doesn't define `__or__`.

Similarly, merging a plain dict with a `SizeDict` on the right side also fails:

```python
base = {"longest_edge": 20}
sd = SizeDict(height=10, width=20)
merged = base | sd  # TypeError
```

## Expected Behavior

- `SizeDict | dict` should return a `SizeDict` with all fields merged
- `SizeDict | SizeDict` should return a `SizeDict` with all fields merged
- `dict | SizeDict` should return a plain `dict` with all entries merged (matching Python's convention where the left operand's type wins)
- `SizeDict | <unsupported type>` should return `NotImplemented`

## Relevant Files

- `src/transformers/image_utils.py` — the `SizeDict` class (near the end of the file)
