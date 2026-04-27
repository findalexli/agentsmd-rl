#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "uv run ruff format --check .   # Check formatting without making changes (same a" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -20,13 +20,22 @@ uv run dmypy run         # Type check Python code (uses mypy daemon)
 uv run pytest python/    # Run Python tests (use after both Rust and Python changes)
 ```
 
+### Code Formatting and Linting
+
+```bash
+uv run ruff format .           # Format Python code
+uv run ruff format --check .   # Check formatting without making changes (same as CI)
+uv run ruff check .            # Lint Python code
+```
+
 ### Workflow Summary
 
 | Change Type | Commands to Run |
 |-------------|-----------------|
 | Rust code only | `uv run maturin develop && cargo test` |
 | Python code only | `uv run dmypy run && uv run pytest python/` |
 | Both Rust and Python | Run all commands from both categories above |
+| Python formatting | `uv run ruff format .` |
 
 ## Code Structure
 
PATCH

echo "Gold patch applied."
