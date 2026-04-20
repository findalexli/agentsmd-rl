# Fix filter_files to include parent directories for .prefectignore negation patterns

## Problem Description

When a `.prefectignore` file contains negation patterns that re-include files inside otherwise-ignored directories, the current implementation returns the re-included files but does NOT include their parent directories in the result set.

This causes problems for `shutil.copytree`, which uses an `ignore_func` that skips directories that are not in the included set. Since parent directories are not in the result, `copytree` never traverses into them, and the re-included files are never copied.

## Expected Behavior

When the filter_files function is called with `include_dirs=True` (the default) and negation patterns re-include files, the function must:

1. Include all re-included files in the result (current behavior)
2. **Also include all parent directories of those files** (missing behavior)

For example, given this directory structure:
```
tmp/
├── workflows/
│   └── flow.py
└── other.txt
```

And these ignore patterns: `["*", "!workflows/", "!workflows/*"]`

The result should contain BOTH:
- `"workflows"` (the parent directory)
- `"workflows/flow.py"` (the file itself)

## Test Requirements

Your fix must satisfy these test assertions:

**Test 1: Basic negation with parent directory**
- Create a temp directory with: `workflows/flow.py` and `other.txt`
- Create a `.prefectignore` file (empty content)
- Call `filter_files(root=str(tmp_path), ignore_patterns=["*", "!.prefectignore", "!workflows/", "!workflows/*"])`
- Assert that `"workflows"` is in the result
- Assert that `"workflows/flow.py"` (or similar path) is in the result

**Test 2: Nested directories**
- Create: `a/b/c/file.py` with nested parent directories
- Call `filter_files(root=str(tmp_path), ignore_patterns=["*", "!a/b/c/file.py"])`
- Assert that `"a"`, `"a/b"`, `"a/b/c"`, and `"a/b/c/file.py"` are ALL in the result

**Test 3: include_dirs=False behavior unchanged**
- When `include_dirs=False` is passed, the fix should NOT add parent directories
- The behavior for `include_dirs=False` must remain exactly as before

**Test 4: Existing functionality preserved**
- Basic filtering without negation patterns must still work correctly
- The repo's existing tests in `tests/utilities/test_filesystem.py` must pass
- The code must pass ruff linting and have valid AST

## Agent Configuration References

- `src/prefect/utilities/AGENTS.md`: Utilities must not import from server modules (they are used client-side)
- Root `AGENTS.md`: Use modern Python typing (`list[int]`, `T | None`), run `uv run pytest` for tests
