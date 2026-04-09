# Fix SetTitleCallbackProcessor Polling Time

## Problem

The `SetTitleCallbackProcessor` in `openhands/app_server/event_callback/set_title_callback_processor.py` is failing to fetch conversation titles reliably. The current exponential backoff (0.25, 0.5, 1.0, 2.0 seconds = ~3.75s total) is insufficient to give the conversation server time to generate a title via LLM.

## What You Need To Do

Increase the polling time to give the agent server more time to generate titles:

1. **Add configurable constants** at module level:
   - `_POLL_DELAY_S = 3` (seconds between polling attempts)
   - `_NUM_POLL_ATTEMPTS = 4` (number of attempts to poll)

2. **Extract the polling logic** into a separate async function called `_poll_for_title()`:
   - Takes parameters: `httpx_client`, `url`, `session_api_key`
   - Returns: the title string if available, or `None`
   - Should poll `_NUM_POLL_ATTEMPTS` times with `_POLL_DELAY_S` seconds between attempts
   - Change the log level from `debug` to `warning` when polling fails

3. **Refactor `__call__` method**:
   - Replace the inline polling loop with a call to `_poll_for_title()`
   - Remove the old `_TITLE_POLL_DELAYS_S` tuple constant

4. **Update the existing test**:
   - In `tests/unit/app_server/test_set_title_callback_processor.py`, the test `test_set_title_callback_processor_request_errors_return_none` currently patches `_logger.debug` - update it to patch `_logger.warning` instead to match the new logging level

## Expected Result

- Total polling time should be ~12 seconds (4 attempts × 3 seconds)
- The polling logic is extracted into a testable, reusable function
- Failed poll attempts log at warning level instead of debug
- All existing unit tests pass

## Key Files

- `openhands/app_server/event_callback/set_title_callback_processor.py` - Main file to modify
- `tests/unit/app_server/test_set_title_callback_processor.py` - Update the test that checks logging behavior

## Testing

Run the existing tests to ensure your changes work:
```bash
poetry run pytest tests/unit/app_server/test_set_title_callback_processor.py -v
```

Make sure to also run linting:
```bash
pre-commit run --config ./dev_config/python/.pre-commit-config.yaml
```
