"""Behavioral checks for pdpipe-chore-add-cursorrules-files-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pdpipe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/always.mdc')
    assert 'You are a both **Python expert** and a **Data Science expert**, with deep knowledge of modern Python practices, machine learning tools and practices. Prioritize clean, maintainable code that follows P' in text, "expected to find: " + 'You are a both **Python expert** and a **Data Science expert**, with deep knowledge of modern Python practices, machine learning tools and practices. Prioritize clean, maintainable code that follows P'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/always.mdc')
    assert '- pdpipe is a Python package for building serializable, chainable, and verbose data processing pipelines for pandas DataFrames, with a focus on data science and machine learning workflows.' in text, "expected to find: " + '- pdpipe is a Python package for building serializable, chainable, and verbose data processing pipelines for pandas DataFrames, with a focus on data science and machine learning workflows.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/always.mdc')
    assert '- Tests must be added for all new code. Place tests in the appropriate module subdirectory under tests/, and use one test function per use case. Aim to maintain 100% test coverage.' in text, "expected to find: " + '- Tests must be added for all new code. Place tests in the appropriate module subdirectory under tests/, and use one test function per use case. Aim to maintain 100% test coverage.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dev_test_and_build.mdc')
    assert "- In this machine, uv is installed on pyenv's Python 3.12.10, and pyenv is not initialized on every terminal session *on purpose*, so you'll have to run `pyenv init - bash`, then `pyenv shell 3.12.10`" in text, "expected to find: " + "- In this machine, uv is installed on pyenv's Python 3.12.10, and pyenv is not initialized on every terminal session *on purpose*, so you'll have to run `pyenv init - bash`, then `pyenv shell 3.12.10`"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dev_test_and_build.mdc')
    assert 'description: When asked to build virtualenvs, run commands in them, run tests, setup or build the package, handle dependencies, integrate tools into the package or the CI, and anytime handling pyproje' in text, "expected to find: " + 'description: When asked to build virtualenvs, run commands in them, run tests, setup or build the package, handle dependencies, integrate tools into the package or the CI, and anytime handling pyproje'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dev_test_and_build.mdc')
    assert "- Before every commit, run the pre-commit hooks defined by pre-commit-config.yaml by running `uv run pre-commit run --all-files` in the project's root, and fix every raised error." in text, "expected to find: " + "- Before every commit, run the pre-commit hooks defined by pre-commit-config.yaml by running `uv run pre-commit run --all-files` in the project's root, and fix every raised error."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python.mdc')
    assert '*   **src layout:** Consider using a `src` directory to separate application code from project-level files (setup.py, requirements.txt, etc.). This helps avoid import conflicts and clarifies the proje' in text, "expected to find: " + '*   **src layout:** Consider using a `src` directory to separate application code from project-level files (setup.py, requirements.txt, etc.). This helps avoid import conflicts and clarifies the proje'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python.mdc')
    assert 'description: Comprehensive guidelines for Python development, covering code organization, performance, security, testing, and more.  These rules promote maintainable, efficient, and secure Python code' in text, "expected to find: " + 'description: Comprehensive guidelines for Python development, covering code organization, performance, security, testing, and more.  These rules promote maintainable, efficient, and secure Python code'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python.mdc')
    assert '*   **Dunder names:** `__all__`, `__version__`, etc. should be after the module docstring but before any imports (except `from __future__`).  Use `__all__` to explicitly define the public API.' in text, "expected to find: " + '*   **Dunder names:** `__all__`, `__version__`, etc. should be after the module docstring but before any imports (except `from __future__`).  Use `__all__` to explicitly define the public API.'[:80]

