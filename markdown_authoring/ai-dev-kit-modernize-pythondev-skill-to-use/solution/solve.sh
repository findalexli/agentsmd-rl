#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-dev-kit

# Idempotency guard
if grep -qF "6. **Environment**: Use `uv` exclusively for dependencies and execution, Ruff fo" ".claude/skills/python-dev/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/python-dev/SKILL.md b/.claude/skills/python-dev/SKILL.md
@@ -146,39 +146,62 @@ def test_calculate_total_negative_tax():
 ## Environment Management
 
 ### Dependency Management
-- **Use uv**: Dependency management via [uv](https://github.com/astral-sh/uv)
-- **Virtual environments**: Use virtual environments (`venv`) or `uv`
-- **Check existing venv**: Always check for existing `.venv` in current or parent directories before creating new one
-- **Activate before use**: Activate `.venv` before installing packages or executing scripts
-
-### Code Style
-- **Ruff**: Use Ruff for code style consistency and linting
+- **Use uv exclusively**: All packaging, environment, and script execution via [uv](https://github.com/astral-sh/uv)
+- **No pip/venv/conda**: Do not use `pip`, `python3 -m venv`, or `conda` — `uv` handles all of this
+- **pyproject.toml is the source of truth**: Define all dependencies in `pyproject.toml` (not `requirements.txt`)
 
 ### Environment Setup Example
 
 ```bash
-# Check for existing .venv
-if [ -d ".venv" ]; then
-    source .venv/bin/activate
-elif [ -d "../.venv" ]; then
-    source ../.venv/bin/activate
-else
-    # Create new venv or use uv
-    python3 -m venv .venv
-    source .venv/bin/activate
-fi
-
-# Install dependencies
-pip install -r requirements.txt
-
-# Or with uv
-uv pip install -r requirements.txt
+# Install dependencies from pyproject.toml
+uv sync
+
+# Install with optional dev dependencies
+uv sync --extra dev
+
+# Run a script (no activation needed)
+uv run python script.py
+
+# Run pytest
+uv run pytest
+
+# Add a new dependency
+uv add requests
+
+# Remove a dependency
+uv remove requests
+```
+
+### Running Python Code
+- Use `uv run` to execute scripts — no manual venv activation needed
+- Use `uv run <tool>` for dev tools (pytest, ruff, etc.)
+- Dependencies are defined in `pyproject.toml` (not requirements.txt)
+
+### Linting & Formatting (Ruff)
+- **Ruff**: Use Ruff for linting AND formatting (replaces flake8, black, isort)
+
+```bash
+# Lint code
+uv run ruff check .
+
+# Lint and auto-fix
+uv run ruff check --fix .
+
+# Format code
+uv run ruff format .
+
+# Check formatting without changes
+uv run ruff format --check .
+```
+
+### Type Checking (Pyright)
+
+```bash
+# Check types
+uv run pyright
 ```
 
-### Python Script Execution
-- Always activate virtual environment before running Python scripts
-- Use `python3` explicitly when not in venv
-- Check for `requirements.txt` or `pyproject.toml` for dependencies
+Note: Use `pyright` for type checking — do not use `mypy`.
 
 ## Best Practices Summary
 
@@ -187,5 +210,5 @@ uv pip install -r requirements.txt
 3. **Errors**: Specific exceptions, early validation, no bare except
 4. **Efficiency**: f-strings, comprehensions, context managers
 5. **Testing**: pytest only, TDD, tests in `./tests/`, all must pass
-6. **Environment**: uv or venv, check existing `.venv`, activate before use, Ruff for style
+6. **Environment**: Use `uv` exclusively for dependencies and execution, Ruff for linting/formatting, Pyright for type checking
 
PATCH

echo "Gold patch applied."
