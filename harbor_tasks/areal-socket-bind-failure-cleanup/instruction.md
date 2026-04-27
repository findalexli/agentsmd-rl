# Task: areal-socket-bind-failure-cleanup

**Repository:** inclusionAI/AReaL @ commit `7cad4dac2d1f230891f201dbbfa91403e621cec1`
**PR:** 1032

---

## Overview

AReaL contains two categories of resource management bugs that need to be fixed. All modified files must pass the full test suite for a reward of 1; any failure yields 0.

---

## Bug 1 — Socket file descriptor leaks in network utilities

### Symptom

The port availability checking logic in `areal/utils/network.py` leaks socket file descriptors. When ports are already in use (the common failure case), sockets are allocated but never properly released. Over time, under heavy port-scanning workloads, this exhausts the OS file descriptor limit.

### Required behavior

- All allocated sockets must be properly closed regardless of whether operations succeed or fail.
- Both TCP and UDP code paths must ensure proper socket cleanup.
- The port-checking logic should continue to return `True` if the port is free, `False` otherwise.

---

## Bug 2 — Lost exception tracebacks in trainer context managers

### Symptom

The trainer classes in `areal/trainer/rl_trainer.py` and `areal/trainer/sft_trainer.py` implement context manager protocols. When an exception occurs inside a `with` block using these trainers, the original traceback is destroyed and replaced with one that points to the trainer's internal code. This makes debugging training failures very difficult because developers cannot see where the error actually originated.

### Required behavior

- The context manager protocol must preserve the original exception's full traceback.
- Python's default exception propagation mechanism should be used rather than manual exception handling that destroys traceback information.
- Cleanup operations (like resource release) must still run regardless of whether an exception is propagating.

---

## Files that must be modified

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
