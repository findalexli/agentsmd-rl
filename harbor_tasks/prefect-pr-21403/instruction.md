# Prefect ProcessPoolTaskRunner Bug Fix

## Issue

GitHub Issue: https://github.com/PrefectHQ/prefect/issues/21401

When a `ProcessPoolTaskRunner` is deserialized in a subprocess (via cloudpickle during nested task submission), the `_subprocess_message_processor_factories` private attribute can intermittently be absent. This causes an `AttributeError` when `flow.task_runner.duplicate()` is called.

## Symptom

The error manifests as:
```
AttributeError: 'ProcessPoolTaskRunner' object has no attribute '_subprocess_message_processor_factories'
```

This occurs during `hydrated_context()` when it calls `flow.task_runner.duplicate()` in a subprocess context.

## Expected Behavior

The `duplicate()` method should gracefully handle the case where `_subprocess_message_processor_factories` is missing, returning a `ProcessPoolTaskRunner` with `subprocess_message_processor_factories` property returning an empty tuple `()`.

## Files to Examine

- `src/prefect/task_runners.py` — The `ProcessPoolTaskRunner` class implementation
  - The `duplicate()` method around line 755
  - The `subprocess_message_processor_factories` property getter around line 763

## Reproduction

```python
from prefect.task_runners import ProcessPoolTaskRunner

runner = ProcessPoolTaskRunner(max_workers=4)
del runner._subprocess_message_processor_factories  # Simulate deserialization

# This should NOT raise AttributeError
duplicate_runner = runner.duplicate()

assert isinstance(duplicate_runner, ProcessPoolTaskRunner)
assert duplicate_runner.subprocess_message_processor_factories == ()
```

## Test Verification

After implementing the fix, verify that:
1. `duplicate()` does not raise `AttributeError` when `_subprocess_message_processor_factories` is missing
2. The duplicated runner's `subprocess_message_processor_factories` property returns `()`
3. `duplicate()` still correctly preserves existing factories when they are present

## Notes

- The bug is intermittent and may not reproduce consistently
- The fix should be defensive rather than addressing a confirmed root cause in the serialization path
- Consider whether a warning log would help surface underlying deserialization issues
