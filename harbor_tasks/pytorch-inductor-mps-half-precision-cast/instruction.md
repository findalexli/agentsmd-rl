# Task: Fix indentation in CLAUDE.md

The file `CLAUDE.md` in the repository at `/workspace/repo` has indentation that causes test failures. The tests require that no line starts with exactly 4 spaces and that at least one line starts with exactly 2 spaces. Fix the indentation to satisfy these requirements.

Ensure the repository's existing functionality is preserved. The following tests must continue to pass:
- `tests/test_harness_utils.py`
- `tests/test_log_parsers_java.py`
- `tests/test_cli.py::test_smoke_test`
- The `swebench` package must be importable (i.e., `import swebench` works and exposes `__version__`)