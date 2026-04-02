# Bug: `pad_packed_tensor_dict` creates a zero-length dummy sequence when padding is unnecessary

## Context

In `areal/utils/data.py`, the function `pad_packed_tensor_dict` pads a packed dictionary of tensors (keyed by `cu_seqlens`, `max_seqlen`, and various data tensors) to a specified total length. It appends a padding sequence and updates `cu_seqlens` accordingly.

## Problem

When the batch's `total_length` already equals `pad_to_length` — i.e., no padding is actually needed — the function still appends an entry to `cu_seqlens` via `F.pad(cu_seqlens, (0, 1), value=pad_to_length)`. This creates a zero-length dummy sequence at the end of the batch.

Downstream consumers that iterate over sequences using consecutive `cu_seqlens` entries (e.g., `cu_seqlens[i]` to `cu_seqlens[i+1]`) encounter a sequence of length 0. Some operations, such as `nn.Conv1d`, raise a `RuntimeError` when given a zero-length input slice.

## Reproduction scenario

1. Construct a packed tensor dict where `cu_seqlens[-1]` (i.e., `total_length`) exactly equals `pad_to_length`.
2. Call `pad_packed_tensor_dict(data, pad_to_length)`.
3. Observe that the returned `cu_seqlens` has one more entry than the input, with the last two entries being equal (creating a zero-length segment).
4. Any code that slices tensors by consecutive `cu_seqlens` pairs and passes them to operations intolerant of empty input will crash.

## Expected behavior

When no padding is needed (`pad_length == 0`), the function should return the data unchanged without appending a spurious entry to `cu_seqlens`.

## Files to investigate

- `areal/utils/data.py` — `pad_packed_tensor_dict` function (around line 800)
