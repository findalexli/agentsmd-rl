# Task: Add Log Context Fields to Enterprise Logger

## Problem

The enterprise JSON logger (`enterprise/server/logger.py`) currently only outputs `message` and `severity` (renamed from `levelname`) fields. It does not include important debugging context like:

- `module`: The module name where the log was generated
- `funcName`: The function name where the log was generated  
- `lineno`: The line number where the log was generated

This makes debugging difficult because log entries don't show where they originated in the codebase.

## Location

- **Primary file**: `enterprise/server/logger.py`
- **Target function**: `setup_json_logger()`

## Requirements

Modify the `setup_json_logger()` function to include `module`, `funcName`, and `lineno` fields in the JSON log output.

The current format string style needs to be changed to include these fields. The `JsonFormatter` from `pythonjsonlogger.json` can accept percent-style format strings like `%(fieldname)s`.

## Testing

The enterprise directory contains unit tests for the logger at `enterprise/tests/unit/test_logger.py`. These tests verify that the logger output includes the expected fields.

To run enterprise tests locally:
```bash
cd enterprise
PYTHONPATH=".:$PYTHONPATH" poetry run pytest tests/unit/test_logger.py
```

## Expected Behavior

After the fix, logging output should look like:
```json
{
  "message": "Test message",
  "severity": "INFO",
  "module": "test_logger",
  "funcName": "test_info",
  "lineno": 45
}
```

Instead of:
```json
{
  "message": "Test message",
  "severity": "INFO"
}
```
