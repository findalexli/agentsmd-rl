# Task: Refactor SetTitleCallbackProcessor Polling

## Context

The OpenHands repository is cloned at `/workspace/OpenHands`. The file `openhands/app_server/event_callback/set_title_callback_processor.py` contains the `SetTitleCallbackProcessor` class, which polls an agent server to retrieve conversation titles after message events.

## Problem

The current polling implementation has several issues:

1. **Polling parameters are too aggressive.** The module uses `_TITLE_POLL_DELAYS_S = (0.25, 0.5, 1.0, 2.0)` — a tuple of backoff delays that are too short. The polling should instead use a uniform 3-second delay between attempts and make exactly 4 total attempts, configured via appropriately named module-level constants.

2. **Polling logic is inlined in `__call__`.** The retry loop is embedded directly in the `__call__` method, making it harder to test and maintain. The polling logic should be extracted into a dedicated async helper function.

3. **Failed polls are logged at `debug` level.** Transient failures during title polling are essentially invisible in production logs because `_logger.debug(...)` is used. Failed poll attempts should be logged at `warning` level instead.

## Requirements

After the refactoring, the module should satisfy all of the following:

- The old `_TITLE_POLL_DELAYS_S` constant is removed from the file
- Two new module-level constants control polling behavior: one set to `3` for the delay between attempts, and one set to `4` for the total number of attempts
- A new async helper function encapsulates all polling logic. It should accept the HTTP client, target URL, and session API key as parameters, and return either the title string or `None` (return type annotated as `str | None`)
- The helper function must use the new constants for its loop count and sleep duration
- The `__call__` method delegates polling to this new async function via `await` instead of containing inline retry logic
- Failed HTTP requests during polling are logged at `warning` level, not `debug`
- The module is valid Python syntax
- The code passes `ruff check --config dev_config/python/ruff.toml` on the modified file
- Existing unit tests at `tests/unit/app_server/test_set_title_callback_processor.py` continue to pass
