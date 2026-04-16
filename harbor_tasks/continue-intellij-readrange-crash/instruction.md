# Fix StringIndexOutOfBoundsException in IntelliJIde readRangeInFile

## The Problem

The Continue IntelliJ extension crashes with `StringIndexOutOfBoundsException` when reading file ranges. This happens when:

- A file is very small (e.g., a temp file or a few characters)
- The extension requests a range that extends beyond the file's actual size

The crash occurs when `substring()` is called with indices that exceed the string's length or when array access goes beyond bounds.

## Impact

- The background process silently breaks
- Chat context is disrupted
- No error is visible to the user

## Relevant Files

- `extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt` — contains the `readRangeInFile` function
- The `Range` type has `start(line, character)` and `end(line, character)` fields

## What You Need to Do

Fix the `readRangeInFile` function so it never throws `StringIndexOutOfBoundsException`, regardless of how small the target file is or how large the requested range is.

**You must use Kotlin's `coerceIn` stdlib function** to safely clamp all indices to valid bounds before accessing the file contents. The fix requires at least two `coerceIn` calls in this function.

## How to Verify Your Fix

1. The Kotlin code compiles: `./gradlew compileKotlin` in the intellij extension directory
2. Unit tests pass (if any exist): `./gradlew test`
3. The fix handles edge cases: empty files, single-char files, ranges requesting more lines/characters than exist
4. After the fix, the source code contains `coerceIn` at least twice in the `readRangeInFile` function