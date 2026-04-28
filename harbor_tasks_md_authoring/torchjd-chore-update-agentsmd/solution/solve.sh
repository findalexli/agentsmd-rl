#!/usr/bin/env bash
set -euo pipefail

cd /workspace/torchjd

# Idempotency guard
if grep -qF "- When you create or modify a code example in a public docstring, always update " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,6 +6,9 @@
 - We use uv for everything (e.g. we do `uv run python ...` to run some python code, and
   `uv run pytest tests/unit` to run unit tests). Please prefer `uv run python -c ...` over
   `python3 -c ...`
+- When you create or modify a code example in a public docstring, always update the corresponding
+  doc test in the appropriate file of `tests/doc`. This also applies to any change in an example of
+  a `.rst` file, that must be updated in the corresponding test in `tests/doc/test_rst.py`.
 - After generating code, please run `uv run ty check`, `uv run ruff check` and `uv run ruff format`.
   Fix any error.
 - After changing anything in `src` or in `tests/unit` or `tests/doc`, please identify the affected
PATCH

echo "Gold patch applied."
