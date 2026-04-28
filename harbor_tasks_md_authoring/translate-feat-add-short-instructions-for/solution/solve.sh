#!/usr/bin/env bash
set -euo pipefail

cd /workspace/translate

# Idempotency guard
if grep -qF "- Use dependency groups for different environments (dev, test, docs, etc.)" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,28 @@
+# Copilot Instructions for translate-toolkit
+
+# Existing documentation
+
+Follow existing contributor documentation in `docs/developers/`.
+
+## Code Style and Standards
+
+- Follow PEP 8 standards
+- Use type annotations
+
+### Linting and Formatting
+
+- Pre-commit hooks are configured (`.pre-commit-config.yaml`)
+- Use pylint for Python code quality
+- Follow existing code formatting patterns
+- Run `pre-commit run --all-files` before committing
+- Type check new code with `mypy`
+
+## Documentation
+
+- Document new feature in `docs/`
+
+### Dependencies
+
+- Manage dependencies in `pyproject.toml`
+- Use dependency groups for different environments (dev, test, docs, etc.)
+- Keep dependencies up to date with security considerations
PATCH

echo "Gold patch applied."
