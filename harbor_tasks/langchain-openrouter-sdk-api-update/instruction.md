# Fix langchain-openrouter SDK Compatibility

## Problem

The `langchain-openrouter` package fails to import after the `openrouter` SDK was upgraded to version 0.8.0 or higher. The SDK renamed several message classes in its `openrouter.components` module. The package code references the old class names, causing `ImportError` or `AttributeError` at import time or when processing messages with file content blocks.

## Discovery

The old class names in use come from `openrouter.components` — they no longer exist in the installed SDK version. You must discover what the current class names are by inspecting the actual `openrouter.components` module in the environment (e.g., `python -c "from openrouter import components; print([x for x in dir(components) if 'Message' in x])"` or similar introspection).

The SDK version requirement in `pyproject.toml` (`openrouter>=0.7.11`) must be updated to allow `>=0.8.0`.

## Expected Outcome

After the fix:
1. `from langchain_openrouter.chat_models import ChatOpenRouter, _wrap_messages_for_sdk` succeeds without `ImportError`
2. The message wrapping logic returns SDK message objects (not plain dicts) when wrapping file-block content, for all roles: user, system, assistant, tool, developer
3. All repo unit tests pass: `uv run --group test pytest tests/unit_tests/test_chat_models.py -v`
4. Lint and type checks pass: `make lint_package`, `make lint_tests`, `make type`

## Scope

The changes are localized to:
- `langchain_openrouter/chat_models.py` — update the message class references in the SDK wrapping code
- `pyproject.toml` — update the `openrouter` dependency lower bound to `>=0.8.0`
- `tests/unit_tests/test_chat_models.py` — if the old class names appear there, update them too

Do not add new message types or change the wrapping logic — only update the class names it references.