# ERA001 false positive on `ty: ignore` comments

## Bug

The `eradicate` rule ERA001 ("Found commented-out code") incorrectly flags `# ty: ignore` comments as commented-out code. These are type-checker suppression comments used by `ty` (Ruff's type checker) and should be treated the same way as `# type: ignore`, `# mypy:`, and `# pyright:` comments, which are already allowlisted.

## Reproduction

Create a Python file with a `# ty: ignore` comment:

```python
import foo  # ty: ignore[unresolved-import]

# ty: ignore
x: int = "hello"  # ty: ignore[invalid-assignment]
```

Run `ruff check --select ERA001` on it. The `# ty: ignore` lines are incorrectly reported as ERA001 violations.

## Expected behavior

`# ty: ignore` comments (with or without error codes in brackets) should be allowlisted in the eradicate detection logic, just like `# type: ignore`, `# mypy:`, and `# pyright:` comments already are.

## Relevant files

- `crates/ruff_linter/src/rules/eradicate/detection.rs` — contains the `ALLOWLIST_REGEX` and `comment_contains_code` function
- `crates/ruff_linter/resources/test/fixtures/eradicate/ERA001.py` — test fixtures for the rule
