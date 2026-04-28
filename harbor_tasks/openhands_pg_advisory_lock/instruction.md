# Fix: Preserve Special Characters in Uploaded Filenames

## Problem Description

The `strip_invalid_filename_characters` function in `gradio_client.utils` is too aggressive when sanitizing filenames from user uploads. It currently uses an allowlist approach, stripping out any character that is not alphanumeric or one of `.`, `_`, `-`, `,`, and space.

This causes issues when users upload files with common special characters in their names:
- **`#`** in filenames like `a#.txt` are stripped
- **`&`** ampersands like in `AAabc&3` are stripped
- **`$`** is stripped
- Parentheses `()` and brackets `[]` are stripped, breaking filenames like `[{(Hunting's Shadowsl!)}].epub`
- Unicode punctuation like Japanese `｡` and `､` are stripped

The function is called during file upload processing in the Gradio client library, and users expect their original filenames to be preserved as much as possible.

## What Should Happen

The filename sanitizer should only remove characters that are genuinely dangerous or forbidden across file systems and shell environments:

- **Path traversal characters** `/` and `\` should still be stripped (prevents directory traversal attacks)
- **Null bytes** (`\x00`) and **control characters** (`\x00-\x1f`, `\x7f`) should still be removed
- **Windows-forbidden characters** `<`, `>`, `:`, `"`, `|`, `?`, `*` should still be removed
- **Shell-dangerous characters** `` ` ``, `$`, `!`, `{`, `}` should be removed

All other characters should be preserved, including:
- `#`, `&`, `@`, `'` and other common filename characters
- Parentheses `()`, brackets `[]`
- Unicode and non-ASCII characters
- Japanese punctuation such as `｡`, `､`, `…`

## Code Location

The fix is in `client/python/gradio_client/utils.py`, in the `strip_invalid_filename_characters` function.

## Verification

After making the change, the following should hold:

1. `strip_invalid_filename_characters("abc")` returns `"abc"` (unchanged simple names)
2. `strip_invalid_filename_characters("$$AAabc&3")` returns `"AAabc&3"` (special chars preserved, `$` stripped)
3. `strip_invalid_filename_characters("a#.txt")` returns `"a#.txt"` (extension with `#` preserved)
4. `strip_invalid_filename_characters("a/b\\c.txt")` returns `"abc.txt"` (path separators still stripped)
5. The repo's linter (`ruff check`) passes on the modified file
6. The repo's formatter (`ruff format --check`) passes on the modified file
7. Existing unit tests in `client/python/test/test_utils.py` still pass (excluding the filename sanitization tests which test the old behavior)

## Code Style Requirements

- Run `ruff check client/python/gradio_client/utils.py` to verify lint compliance
- Run `ruff format --check client/python/gradio_client/utils.py` to verify formatting
- Ensure existing tests pass with `python -m pytest client/python/test/test_utils.py -v -k "not test_strip_invalid_filename_characters"`
