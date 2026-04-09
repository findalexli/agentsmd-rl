# Strip form feeds from indentation in `dedent_to`

## Problem

When Ruff applies an autofix that adjusts indentation (e.g., removing an empty `finally` clause via RUF072), it can produce a **syntax error** in the output if the code being fixed is preceded by a form feed character (`\x0c`).

For example, applying `ruff check --fix --preview --select RUF072` to a Python file where a `try` block is preceded by a form feed results in malformed output because the form feed is incorrectly treated as part of the indentation.

## Expected Behavior

Form feeds at the start of a line in Python do not contribute to indentation. The `dedent_to` function in the text-wrapping utilities should handle this correctly so that autofixes produce valid Python regardless of leading form feeds.

## Files to Look At

- `crates/ruff_python_trivia/src/textwrap.rs` — contains the `dedent_to` function that computes indentation adjustments for fix edits
