# Fix the syntax error in the example repo

The repository at `/workspace/example-repo` contains a Python module `src/utils.py` with two functions — `helper_function` and `process_data` — but the file has a **syntax error** that prevents it from compiling or being imported.

## Symptom

Running either of these commands from `/workspace/example-repo` fails:

```bash
python -m py_compile src/utils.py
python -c "from src import utils; print('OK')"
```

The module cannot be compiled or imported due to the syntax error in `src/utils.py`.

## Task

Fix the syntax error so that the file is valid Python. After the fix, all of the following CI checks must pass (run from `/workspace/example-repo`):

1. **Compilation**: `python -m py_compile src/utils.py` exits with code 0.
2. **Import**: `python -c "from src import utils; print('OK')"` succeeds and prints `OK`.
3. **Lint**: `ruff check src/ tests/` exits with code 0.
4. **Type check**: `mypy src/ --ignore-missing-imports` exits with code 0.
5. **Unit tests (module)**: `python -m pytest tests/test_utils.py -v` — all tests pass.
6. **Full test suite**: `python -m pytest tests/ -v` — all tests pass.
