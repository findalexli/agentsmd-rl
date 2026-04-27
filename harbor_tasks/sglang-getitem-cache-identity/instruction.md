# Fix __getitem__ object identity instability in batched request classes

## Problem

The `GenerateReqInput` and `EmbeddingReqInput` classes implement `__getitem__` to return sub-objects for batched requests. However, each call to `obj[i]` constructs and returns a **new** instance, which causes two problems:

1. **Identity instability**: `obj[0] is obj[0]` evaluates to `False`. Different parts of the code that independently access `obj[0]` get separate objects. If one caller mutates its reference, other callers holding a different reference to `obj[0]` don't see the change.

2. **LoRA ID not reflected in sub-objects**: During request processing, the LoRA path resolution step looks up a `lora_id` and assigns it to the parent request object. However, sub-objects that were already created by prior `__getitem__` calls are separate instances and don't receive this update. Downstream code holding references to those sub-objects works with stale (usually `None`) `lora_id` values.

## Expected Behavior

1. Repeated calls to `req[i]` with the same index must return the **same object instance** (i.e., `req[0] is req[0]` should be `True`).
2. After LoRA ID resolution assigns `lora_id` to the parent object, any sub-objects previously returned by `__getitem__` must also reflect the updated `lora_id`.

## Code Style Requirements

Modified files must pass `ruff`, `black`, `isort`, `pyflakes`, and `codespell` checks.
