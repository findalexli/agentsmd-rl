#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "uv run --only-group lint clint .                    # Run MLflow custom linter" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -88,14 +88,14 @@ yarn --cwd mlflow/server/js test
 
 ```bash
 # Python linting and formatting with Ruff
-uv run ruff check . --fix         # Lint with auto-fix
-uv run ruff format .              # Format code
+uv run --only-group lint ruff check . --fix         # Lint with auto-fix
+uv run --only-group lint ruff format .              # Format code
 
 # Custom MLflow linting with Clint
-uv run clint .                    # Run MLflow custom linter
+uv run --only-group lint clint .                    # Run MLflow custom linter
 
 # Check for MLflow spelling typos
-uv run bash dev/mlflow-typo.sh .
+uv run --only-group lint bash dev/mlflow-typo.sh .
 
 # JavaScript linting and formatting
 yarn --cwd mlflow/server/js lint
@@ -160,14 +160,14 @@ See `mlflow/server/js/` for frontend development.
 git commit -s -m "Your commit message"
 
 # Then check all files changed in your PR
-uv run pre-commit run --from-ref origin/master --to-ref HEAD
+uv run --only-group lint pre-commit run --from-ref origin/master --to-ref HEAD
 
 # Fix any issues and amend your commit if needed
 git add <fixed files>
 git commit --amend -s
 
 # Re-run pre-commit to verify fixes
-uv run pre-commit run --from-ref origin/master --to-ref HEAD
+uv run --only-group lint pre-commit run --from-ref origin/master --to-ref HEAD
 
 # Only push once all checks pass
 git push origin <your-branch>
@@ -217,23 +217,23 @@ gh run watch
 The repository uses pre-commit for code quality. Install hooks with:
 
 ```bash
-uv run pre-commit install --install-hooks
+uv run --only-group lint pre-commit install --install-hooks
 ```
 
 Run pre-commit manually:
 
 ```bash
 # Run on all files
-uv run pre-commit run --all-files
+uv run --only-group lint pre-commit run --all-files
 
 # Run on all files, skipping hooks that require external tools
-SKIP=taplo,typos,conftest uv run pre-commit run --all-files
+SKIP=taplo,typos,conftest uv run --only-group lint pre-commit run --all-files
 
 # Run on specific files
-uv run pre-commit run --files path/to/file.py
+uv run --only-group lint pre-commit run --files path/to/file.py
 
 # Run a specific hook
-uv run pre-commit run ruff --all-files
+uv run --only-group lint pre-commit run ruff --all-files
 ```
 
 This runs Ruff, typos checker, and other tools automatically before commits.
@@ -248,7 +248,7 @@ To install these tools:
 
 ```bash
 # Install all tools at once (recommended)
-uv run bin/install.py
+uv run --only-group lint bin/install.py
 ```
 
 This automatically downloads and installs the correct versions of all external tools to the `bin/` directory. The tools work on both Linux and ARM Macs.
PATCH

echo "Gold patch applied."
