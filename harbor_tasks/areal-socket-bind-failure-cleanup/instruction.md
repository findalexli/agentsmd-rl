# Task: areal-socket-bind-failure-cleanup

**Repository:** inclusionAI/AReaL @ commit `7cad4dac2d1f230891f201dbbfa91403e621cec1`
**PR:** 1032

---

## Overview

AReaL contains two categories of resource leaks that cause test failures. All modified files must pass the full test suite for a reward of 1; any failure yields 0.

---

## Bug 1 — Socket leak in `is_port_free()` (`areal/utils/network.py`)

### Affected function

- `is_port_free(port: int) → bool` in `areal/utils/network.py`

### Symptom

`is_port_free` creates TCP and UDP sockets and calls `bind()` on each. When `bind()` raises an `OSError`, the function returns `False` immediately — but the socket file descriptor is never closed. This leaks a file descriptor every time the port is already in use (the common failure case). Sockets that succeed are closed correctly.

### Required behavior

- When `bind()` raises `OSError` on either socket, that socket **must** be closed before returning.
- Both TCP and UDP code paths must clean up their socket on bind failure.
- Sockets that succeed must also be closed (existing behavior, not a change).

---

## Bug 2 — Traceback destruction in trainer `__exit__` methods

### Affected classes

- `RLTrainer` in `areal/trainer/rl_trainer.py`
- `SFTTrainer` in `areal/trainer/sft_trainer.py`

Both classes implement `__exit__(self, exc_type, exc_value, traceback)` as a context manager hook.

### Symptom

When an exception is propagating out of a `with RLTrainer():` or `with SFTTrainer():` block, the `__exit__` method re-raises it using `raise exc_value`. This replaces the original traceback with a new one that points at the `raise` statement inside `__exit__`, making debugging difficult because the true origin of the exception is lost.

### Required behavior

- `__exit__` must not re-raise the exception.
- It must return a falsy value (`False`, `None`, etc.) so that Python re-raises the original exception with its full traceback intact.
- Cleanup via `self.close()` must still run regardless of whether an exception is propagating.

---

## File list (all must be modified)

- `areal/utils/network.py`
- `areal/trainer/rl_trainer.py`
- `areal/trainer/sft_trainer.py`

---

## Static checks (must also pass)

All modified files must:

- Parse as valid Python (no syntax errors)
- Have no wildcard (`from x import *`) imports
- Have no bare `print()` calls used for logging
- Pass `ruff check` and `ruff format --check`
- End with a single newline and have no trailing whitespace
- Contain at least 3 real statements in `is_port_free` and each `__exit__` (not just `pass` stubs)