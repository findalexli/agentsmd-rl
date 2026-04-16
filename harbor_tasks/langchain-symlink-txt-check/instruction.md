# Fix Symlink Vulnerability in Template Loading

## Context

The langchain repository at `/workspace/langchain` has a security vulnerability in its template loading code. The function `_load_template`, importable from `langchain_core.prompts.loading`, does not properly guard against symlink-based attacks when loading template files.

## Function Signature and Return Value

`_load_template` is called as:

```python
_load_template("template", {"template_path": some_path}, allow_dangerous_paths=True)
```

It returns a `dict` with the key `"template"` containing the file contents as a string. The returned dict must NOT contain the key `"template_path"`.

## Vulnerability Description

When `allow_dangerous_paths=True`, the function accepts a file path via the `template_path` config key and is supposed to validate that only safe file types are loaded. However, an attacker can create a symbolic link (symlink) with an innocent `.txt` extension that actually points to a dangerous file type:

- A symlink named `exploit_link.txt` pointing to `secret.py` will cause Python source code to be loaded as template content
- A symlink named `rce_bypass.txt` pointing to `payload.j2` will cause a jinja2 template to be loaded, enabling remote code execution

The extension check only looks at the symlink's own name, not what the symlink ultimately targets.

## Expected Behavior After Fix

When `allow_dangerous_paths=True`:

1. Loading a real (non-symlink) `.txt` file should succeed and return `{"template": "<file contents>"}`
2. Loading a `.txt` symlink that points to a real `.txt` file should succeed and return `{"template": "<file contents>"}`
3. Loading a `.txt` symlink that points to a `.py` file must raise `ValueError`
4. Loading a `.txt` symlink that points to a `.j2` file must raise `ValueError`

## Validation

After your fix, the existing repository unit tests must still pass. Run these test commands to verify:

- From repo root: `python -m pytest libs/core/tests/unit_tests/prompts/test_loading.py -v`
- From `libs/core`: `python -m pytest tests/unit_tests/prompts/test_imports.py -v`
- From `libs/core`: `python -m pytest tests/unit_tests/prompts/test_prompt.py -v`
