#!/usr/bin/env bash
set -euo pipefail

cd /workspace/causalpy

# Idempotency guard
if grep -qF "- **Before committing**: Always run `pre-commit run --all-files` to ensure all c" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -41,6 +41,15 @@
 - **Custom exceptions**: Use project-specific exceptions from `causalpy.custom_exceptions`: `FormulaException`, `DataException`, `BadIndexException`
 - **File organization**: Experiments in `causalpy/experiments/`, PyMC models in `causalpy/pymc_models.py`, scikit-learn models in `causalpy/skl_models.py`
 
+## Code quality checks
+
+- **Before committing**: Always run `pre-commit run --all-files` to ensure all checks pass (linting, formatting, type checking)
+- **Quick check**: Run `ruff check causalpy/` for fast linting feedback during development
+- **Auto-fix**: Run `ruff check --fix causalpy/` to automatically fix many linting issues
+- **Format**: Run `ruff format causalpy/` to format code according to project standards
+- **Linting rules**: Project uses strict linting (F, B, UP, C4, SIM, I) to catch bugs and enforce modern Python patterns
+- **Note**: Documentation notebooks in `docs/` are excluded from strict linting rules
+
 ## Type Checking
 
 - **Tool**: MyPy
PATCH

echo "Gold patch applied."
