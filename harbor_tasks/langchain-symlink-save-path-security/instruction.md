# Fix symlink handling in deprecated prompt save path

## Problem

The `save()` method in the LangChain prompt classes has a security vulnerability involving symlink handling. A symlink with an allowed extension (`.json`, `.yaml`, `.yml`) can point to a file with a dangerous extension (`.py`), and the `save()` method will write data to the target file because it validates the symlink's extension rather than the actual target's extension.

## Symptom

When calling `prompt.save(symlink_path)` where `symlink_path` is a symlink named `output.json` that points to a file named `malicious.py`:

- **Current behavior**: The method checks the symlink name's extension (`.json`), considers it valid, and writes to the target `.py` file
- **Expected behavior**: The method should detect the actual target extension (`.py`), reject the save, and raise a `ValueError` containing the message `"must be json or yaml"`

The same bypass works with `.yaml` and `.yml` symlinks pointing to `.py` files.

## File to modify

- `libs/core/langchain_core/prompts/base.py`

## Testing

After your fix:

- Creating a symlink `output.json` -> `malicious.py` and calling `prompt.save(symlink)` should raise `ValueError` with `"must be json or yaml"` in the message, and the `malicious.py` file should NOT be created
- The same should hold for `.yaml` -> `.py` and `.yml` -> `.py` symlinks
- Valid use cases must continue to work: direct `.json`/`.yaml` saves, and symlinks to valid `.json` files
- The existing prompt save/load round-trip tests and core prompt tests must still pass
- The modified file must pass `ruff check` and `mypy` type checking
