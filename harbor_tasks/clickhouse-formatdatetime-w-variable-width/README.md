# ClickHouse formatDateTime %W Formatter Bug Fix Task

## Summary

This is a benchmark task for fixing a bug in ClickHouse's `formatDateTime` function where the `%W` formatter (weekday name) was not correctly treated as a variable-width formatter under all conditions.

## Bug Description

The `%W` formatter produces weekday names (Monday, Tuesday, etc.) which have variable lengths (6-9 characters). The bug caused it to only be recognized as variable-width when `formatdatetime_parsedatetime_m_is_month_name` setting was enabled. With other settings, it was incorrectly treated as fixed-width.

## Fix Location

- **File**: `src/Functions/formatDateTime.cpp`
- **Function**: `containsOnlyFixedWidthMySQLFormatters`

## Fix Summary

1. Remove 'W' from `variable_width_formatter_M_is_month_name` array (keep only 'M')
2. Add unconditional check for `variable_width_formatter` immediately after `throwLastCharacterIsPercentException()`
3. Remove the redundant `else` branch that previously checked `variable_width_formatter`

## Task Structure

```
/workspace/task/
├── environment/
│   └── Dockerfile          # Docker image definition
├── solution/
│   └── solve.sh            # Script to apply the gold patch
├── tests/
│   ├── test.sh             # Test runner (standardized)
│   └── test_outputs.py     # Test implementations
├── eval_manifest.yaml      # Evaluation configuration
├── instruction.md          # Agent-facing instructions
├── task.toml               # Task metadata
└── README.md               # This file
```

## Validation Results

| Test | NOP (base) | GOLD (fixed) |
|------|------------|--------------|
| test_fix_applied_correctly | ❌ FAIL | ✅ PASS |
| test_no_redundant_else_branch | ✅ PASS | ✅ PASS |
| test_variable_width_formatter_is_unconditional | ❌ FAIL | ✅ PASS |
| test_unconditional_check_structure | ❌ FAIL | ✅ PASS |
| test_function_logic_correct | ❌ FAIL | ✅ PASS |

**Reward**: 0 (base) → 1 (fixed)

## Agent Configuration Rules

From the ClickHouse repository:
- Use Allman-style braces (opening brace on new line)
- Never use sleep to fix race conditions
- Do not delete existing tests
- Follow existing code patterns

## Source

- **PR**: ClickHouse/ClickHouse#102099 (backport of #101847)
- **Base Commit**: `3af0650babfe30f3c9da6de6e392ddccebb9b103`
- **Merge Commit**: `2898d96b3cc67585b4a9e042e687c0718b320f17`
