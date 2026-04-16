Fix the Python environment so the `requests` library can be imported and used.

The repository at `/workspace/requests` contains the source code for the `requests` library. Currently, attempting to `import requests` in Python fails. The fix should make the following work:

1. Python can `import requests` and the library version starts with "2." (as reported by `requests.__version__`)
2. An HTTP GET request to `https://httpbin.org/get` succeeds with status code 200

The repository structure must remain intact with these key files present:
- Source files: `src/requests/__init__.py`, `src/requests/api.py`, `src/requests/sessions.py`, `src/requests/models.py`
- Test files: `tests/test_utils.py`, `tests/test_structures.py`, `tests/test_requests.py`, `tests/conftest.py`
- Makefile with a `ci:` target

Additionally, these quality checks must pass:
- `ruff check src/requests tests/` exits successfully
- `ruff format --check src/` exits successfully
- `pyproject.toml` is valid TOML
