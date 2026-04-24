# Bug: Uploading files with special-character-only filenames raises "Invalid file type"

## Summary

When a user uploads a file whose name (before the extension) consists entirely of special characters — for example `#.txt`, `###.pdf`, or `@!$.csv` — Gradio's file upload raises an "Invalid file type" error, even though the file extension is perfectly valid.

## Steps to reproduce

1. Create a Gradio app with a file upload that accepts `.txt` files.
2. Upload a file named `#.txt`.
3. Observe: the upload is rejected with "Invalid file type".

## Expected behavior

- Files with valid extensions should be accepted regardless of how their stem looks after sanitization.
- The filename sanitization should never produce a bare dotfile (e.g., `.txt`, `.pdf`, `.csv`) when the original filename had a valid extension.
- For filenames where some stem characters survive sanitization (e.g., `a#.txt`, `1#2.csv`, `hello#world.py`), only the invalid characters should be removed.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
