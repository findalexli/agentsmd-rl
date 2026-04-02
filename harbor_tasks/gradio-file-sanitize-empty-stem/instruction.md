# Bug: Uploading files with special-character-only filenames raises "Invalid file type"

## Summary

When a user uploads a file whose name (before the extension) consists entirely of special characters — for example `#.txt`, `###.pdf`, or `@!$.csv` — Gradio's `gr.File` component raises an "Invalid file type" error, even though the file extension is perfectly valid.

## Where to look

The filename sanitization logic lives in `client/python/gradio_client/utils.py`, in the function `strip_invalid_filename_characters()`. This function strips characters that aren't alphanumeric or in a safe set (`.`, `_`, `-`, `,`, space).

The downstream validation function `is_valid_file()` (in `gradio/utils.py`) relies on `pathlib.Path(filename).suffix` to extract the file extension and check it against the allowed types.

## Steps to reproduce

1. Create a Gradio app with `gr.File(file_types=[".txt"])`.
2. Upload a file named `#.txt`.
3. Observe: the upload is rejected with "Invalid file type".

## Root cause hint

After sanitization strips all the special characters from the stem, the resulting filename is _just_ the extension (e.g., `.txt`). Python's `pathlib.Path` treats a filename like `.txt` as a dotfile with no extension — `Path(".txt").suffix` returns `""`. This causes the downstream file-type validation to fail.

## Expected behavior

Files with valid extensions should be accepted regardless of how their stem looks after sanitization. The sanitization step should ensure the resulting filename always has a usable stem so that the extension is preserved correctly.
