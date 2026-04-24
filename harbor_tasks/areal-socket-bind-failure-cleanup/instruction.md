# Task: areal-socket-bind-failure-cleanup

**Repository:** inclusionAI/AReaL @ commit `7cad4dac2d1f230891f201dbbfa91403e621cec1`
**PR:** 1032

---

## Overview

AReaL contains two categories of resource leaks that cause test failures. All modified files must pass the full test suite for a reward of 1; any failure yields 0.

---

## Bug 1 — Socket leak when port binding fails

### Symptom

The codebase contains a utility function that checks whether a network port is available by attempting to bind to it with both TCP and UDP sockets. When the bind operation fails (because the port is already in use), the function returns `False` immediately — but the socket file descriptor is never closed. This leaks a file descriptor every time the port is already in use (the common failure case).

### Required behavior

- When a bind operation raises an `OSError`, the socket must be closed before returning.
- Both TCP and UDP code paths must clean up their socket on bind failure.
- Sockets that bind successfully must also be closed (existing behavior, not a change).
- The function should continue to return `True` if the port is free, `False` otherwise.

---

## Bug 2 — Traceback destruction in trainer context managers

### Symptom

Two trainer classes in the codebase implement context manager `__exit__` methods. When an exception is propagating out of a `with` block using these trainers, the `__exit__` method re-raises the exception using `raise exc_value`. This replaces the original traceback with a new one that points at the `raise` statement inside `__exit__`, making debugging difficult because the true origin of the exception is lost.

### Required behavior

- `__exit__` must not re-raise the exception manually.
- It must return a falsy value (`False`, `None`, etc.) so that Python re-raises the original exception with its full traceback intact.
- Cleanup operations must still run regardless of whether an exception is propagating.

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
- Contain at least 3 real statements in the fixed functions (not just `pass` stubs)
