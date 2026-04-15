# Task: Fix indentation in CLAUDE.md

The file `CLAUDE.md` in the repository at `/workspace/repo` uses 4-space indentation throughout. Convert the entire file to use 2-space indentation instead. The conversion must apply to every indented line in the file.

After the change, the following must hold:
- No line in the file should start with exactly 4 spaces of indentation (i.e., no line whose leading whitespace is exactly 4 spaces)
- The file must contain at least one line that uses 2-space indentation (i.e., starts with exactly 2 spaces)

Ensure the repository's existing functionality is preserved. The following tests must continue to pass:
- `tests/test_harness_utils.py`
- `tests/test_log_parsers_java.py`
- `tests/test_cli.py::test_smoke_test`
- The `swebench` package must be importable (i.e., `import swebench` works and exposes `__version__`)
