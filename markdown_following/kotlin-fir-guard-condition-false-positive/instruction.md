# Fix False Positive DUPLICATE_BRANCH_CONDITION_IN_WHEN for Guard Conditions

## Problem

The Kotlin FIR (Frontend IR) compiler is reporting a false positive `DUPLICATE_BRANCH_CONDITION_IN_WHEN` error for valid when expressions with guard conditions (using `else if`).

Consider this code:

```kotlin
fun isInt(a: Number, b: Number) = when (a) {
    is Int -> true
    else if b is Int -> true
    else -> false
}
```

This produces a false positive error because the checker incorrectly treats `a is Int` and `b is Int` as duplicate conditions, even though they are checking **different variables**.

## Files Involved

The main file to modify is:
- `compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt`

This file contains the checker that validates when expression conditions and reports `DUPLICATE_BRANCH_CONDITION_IN_WHEN`.

## What You Need to Do

1. **Understand the issue**: The current checker tracks type checks (`is` expressions) and constant comparisons in when branches. It reports duplicates when the same type or constant appears multiple times. However, it doesn't properly distinguish between the **when subject** and other variables.

2. **Fix the logic**: Modify the checker so that it only considers a condition as a potential duplicate if it's actually checking the **when subject** (the expression in `when(expr)`). Guard conditions using `else if` that check other variables should be excluded from duplicate detection.

3. **Test the fix**: The repository has FIR analysis tests in `compiler/fir/analysis-tests/testData/resolve/when/`. After your fix, the false positive should no longer occur.

## Guidelines to Follow

- Use the FIR prefix in commit messages for FIR-related changes (e.g., "FIR: Fix false positive...")
- When running Gradle tests, use the `-q` (quiet) flag to reduce output noise
- Follow the existing code style in the checker file

## Expected Outcome

After the fix:
- The example code with `else if b is Int` should compile without `DUPLICATE_BRANCH_CONDITION_IN_WHEN` error
- Actual duplicate conditions on the same subject should still be detected correctly
- The FIR checkers module should compile without errors
