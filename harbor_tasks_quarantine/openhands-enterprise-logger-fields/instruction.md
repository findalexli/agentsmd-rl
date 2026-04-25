# Task: Add Log Context Fields to Enterprise Logger

## Problem

The enterprise JSON logger (`enterprise/server/logger.py`) currently only outputs `message` and `severity` fields. It does not include important debugging context like:

- `module`: The source module name where the log was generated
- `funcName`: The function name where the log was generated
- `lineno`: The line number where the log was generated

This makes debugging difficult because log entries don't show where they originated in the codebase.

## Requirements

Modify the logger to include `module`, `funcName`, and `lineno` fields in the JSON log output.

The expected output format is:
```json
{
  "message": "Test message",
  "severity": "INFO",
  "module": "test_outputs",
  "funcName": "my_test_function",
  "lineno": 45
}
```

The fields must be:
- `message`: The log message string
- `severity`: The log level (renamed from `levelname`)
- `module`: The source module name (when logging from tests, this should be `test_outputs`)
- `funcName`: The function name where the log was emitted (should be `my_test_function`, `comprehensive_test`, `error_test_function`, or `extra_fields_test` depending on which test function is calling the logger)
- `lineno`: A positive integer indicating the source line number

## Testing

The enterprise directory contains unit tests for the logger at `enterprise/tests/unit/test_logger.py`. These tests verify that the logger output includes the expected fields.

To run enterprise tests locally:
```bash
cd enterprise
PYTHONPATH=".:$PYTHONPATH" poetry run pytest tests/unit/test_logger.py
```

The fix should also pass the project's linting, type checking, and existing unit tests.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
