# Fix Calculator Bug

## Overview

This project contains a simple Python calculator module with basic arithmetic operations. The module has two functions: `add()` and `multiply()`, both located in `src/calculator.py`. Each function accepts two integer arguments and returns a result.

## The Problem

The `add()` function is producing incorrect results. Given the following inputs, the function returns wrong values:

- `add(2, 3)` returns `-1` (expected `5`)
- `add(-3, 5)` returns `-8` (expected `2`)
- `add(10, -4)` returns `14` (expected `6`)
- `add(100, 200)` returns `-100` (expected `300`)

The `multiply()` function works correctly and returns the expected product of its inputs:

- `multiply(3, 4)` returns `12`
- `multiply(-2, 5)` returns `-10`

## Expected Behavior

The `add()` function should return the arithmetic sum of its two arguments for all integer inputs. For any integers `a` and `b`, `add(a, b)` should equal `a + b`.

## Requirements

1. Fix the `add()` function so it returns the correct sum for all integer inputs
2. All existing functions must retain their docstrings
3. The module must remain importable without errors
4. The `multiply()` function must continue to work correctly and not be affected by the fix
5. Python source files must have valid syntax
