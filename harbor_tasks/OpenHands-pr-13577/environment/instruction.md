# Fix SetTitleCallbackProcessor Polling Time

## Problem

The `SetTitleCallbackProcessor` in `openhands/app_server/event_callback/set_title_callback_processor.py` is broken - it polls for conversation titles before they are actually ready from the agent server.

The current exponential backoff (`0.25, 0.5, 1.0, 2.0` = ~3.75s total) is insufficient to give the conversation server time to generate a title via LLM.

## What Needs to Change

In `openhands/app_server/event_callback/set_title_callback_processor.py`:

1. **Increase polling time**: Change from the current exponential backoff to use:
   - A constant delay of 3 seconds between attempts (`_POLL_DELAY_S = 3`)
   - 4 total attempts (`_NUM_POLL_ATTEMPTS = 4`)
   - This gives ~12 seconds total for title generation

2. **Extract polling logic**: Move the title polling loop into a separate async function called `_poll_for_title()` that:
   - Takes `httpx_client`, `url`, and `session_api_key` parameters
   - Returns the title string if found, or `None` if not found after all attempts
   - Handles HTTP errors gracefully

3. **Change log level**: When polling fails, the error should be logged at `warning` level instead of `debug` level to make these issues more visible.

The `__call__` method should be simplified to call this new `_poll_for_title()` function.

## Testing

After your changes:
- The unit tests in `tests/unit/app_server/test_set_title_callback_processor.py` should pass
- The pre-commit hooks should pass (run `pre-commit run --config ./dev_config/python/.pre-commit-config.yaml`)
