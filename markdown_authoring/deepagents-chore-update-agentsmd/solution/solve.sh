#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deepagents

# Idempotency guard
if grep -qF "Prefer inline `# noqa: RULE` over `[tool.ruff.lint.per-file-ignores]` for indivi" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -15,6 +15,9 @@ deepagents/
 │   ├── cli/         # CLI tool
 │   ├── acp/         # Agent Context Protocol support
 │   └── harbor/      # Evaluation/benchmark framework
+│   └── partners/    # Integration packages
+│       └── daytona/
+│       └── ...
 ├── .github/         # CI/CD workflows and templates
 └── README.md        # Information about Deep Agents
 ```
@@ -25,6 +28,27 @@ deepagents/
 - `make` – Task runner for common development commands. Feel free to look at the `Makefile` for available commands and usage patterns.
 - `ruff` – Fast Python linter and formatter
 - `ty` – Static type checking
+
+#### Suppressing ruff lint rules
+
+Prefer inline `# noqa: RULE` over `[tool.ruff.lint.per-file-ignores]` for individual exceptions. `per-file-ignores` silences a rule for the *entire* file — If you add it for one violation, all future violations of that rule in the same file are silently ignored. Inline `# noqa` is precise to the line, self-documenting, and keeps the safety net intact for the rest of the file.
+
+Reserve `per-file-ignores` for **categorical policy** that applies to a whole class of files (e.g., `"tests/**" = ["D1", "S101"]` — tests don't need docstrings, `assert` is expected). These are not exceptions; they are different rules for a different context.
+
+```toml
+# GOOD – categorical policy in pyproject.toml
+[tool.ruff.lint.per-file-ignores]
+"tests/**" = ["D1", "S101"]
+
+# BAD – single-line exception buried in pyproject.toml
+"deepagents_cli/agent.py" = ["PLR2004"]
+```
+
+```python
+# GOOD – precise, self-documenting inline suppression
+timeout = 30  # noqa: PLR2004  # default HTTP timeout, not arbitrary
+```
+
 - `pytest` – Testing framework
 
 This monorepo uses `uv` for dependency management. Local development uses editable installs: `[tool.uv.sources]`
@@ -122,14 +146,11 @@ Every new feature or bugfix MUST be covered by unit tests.
 - Avoid mocks as much as possible
 - Test actual implementation, do not duplicate logic into tests
 
-**Checklist:**
+Ensure the following:
 
-- [ ] Tests fail when your new logic is broken
-- [ ] Happy path is covered
-- [ ] Edge cases and error conditions are tested
-- [ ] Use fixtures/mocks for external dependencies
-- [ ] Tests are deterministic (no flaky tests)
-- [ ] Does the test suite fail if your new logic is broken?
+- Does the test suite fail if your new logic is broken?
+- Edge cases and error conditions are tested
+- Tests are deterministic (no flaky tests)
 
 ### Security and risk assessment
 
PATCH

echo "Gold patch applied."
