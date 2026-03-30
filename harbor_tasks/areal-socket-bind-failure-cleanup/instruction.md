There are two small but impactful bugs in AReaL:

**1. Socket leak in `is_port_free()` (`areal/utils/network.py`)**

The `is_port_free()` function creates a socket and calls `sock.bind()`. If `bind()` succeeds, the socket is closed. But if `bind()` fails (raises `OSError`), the except block returns `False` without closing the socket, leaking the file descriptor. This applies to both the TCP and UDP checks in the function.

The socket should always be closed regardless of whether `bind()` succeeds or fails.

**2. Broken traceback in trainer `__exit__` methods (`areal/trainer/rl_trainer.py` and `areal/trainer/sft_trainer.py`)**

Both `RLTrainer.__exit__` and `SFTTrainer.__exit__` have `raise exc_value` in their exception handling path. Using `raise exc_value` explicitly re-raises the exception but replaces the original traceback with one that points at the `raise` statement itself. This makes debugging difficult because the full original traceback is lost.

The correct pattern for context manager `__exit__` methods that want to propagate exceptions is to return `False` (or any falsy value), which tells Python to re-raise the original exception with its full original traceback intact.
