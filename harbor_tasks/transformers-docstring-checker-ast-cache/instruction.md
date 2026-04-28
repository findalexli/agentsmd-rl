# Fix Divide by Zero Bug in Calculator Module

## Overview

The calculator module provides basic arithmetic functions: `add`, `subtract`, `multiply`, and `divide`. The test suite contains a unit test for dividing by zero that currently fails because division by zero is not properly handled, causing the program to crash.

## Symptom

When the `divide` function is called with zero as the divisor, for example `divide(10, 0)`, the program crashes with a `ZeroDivisionError` traceback. The error output does not contain the word `ValueError` or the phrase "cannot divide", which the test suite expects to see when division by zero is attempted.

Normal division operations like `divide(10, 2)` should return `5` and continue to work correctly after the fix is applied.

## Requirements

1. Division by zero must produce an error that includes `ValueError` or the message "cannot divide" in the output, instead of crashing with `ZeroDivisionError`.
2. Normal division such as `divide(10, 2)` must continue returning the correct result `5`.
3. All existing unit tests — including those for `add`, `subtract`, `multiply`, and normal `divide` — must keep passing. The only test that should change from failing to passing is `test_divide_by_zero`.
4. The calculator module must remain importable and print "calculator imported successfully" when loaded.

## Code Style Requirements

The project enforces code quality with the following tools:

- **ruff**: Python linter. Your changes must pass `ruff` linting checks.
- **mypy**: Static type checker. Your changes must pass `mypy` type checking.

Run `ruff` and `mypy` on the repository to verify your changes don't introduce new style or type issues.

## Test Verification

The primary test file `test_calculator.py` contains a `TestCalculator` class with these test methods:

- `test_add` — verifies `add(2, 3)` equals `5`
- `test_subtract` — verifies `subtract(5, 3)` equals `2`
- `test_multiply` — verifies `multiply(4, 3)` equals `12`
- `test_divide` — verifies `divide(10, 2)` equals `5`
- `test_divide_by_zero` — verifies that `divide(10, 0)` raises a `ValueError`

The `test_divide_by_zero` test is the one that currently fails and should pass after the fix is applied.

Only modify the implementation code. Do not modify the test file.
