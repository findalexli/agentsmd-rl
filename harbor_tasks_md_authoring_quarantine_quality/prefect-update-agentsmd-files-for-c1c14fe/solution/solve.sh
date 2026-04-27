#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref" "docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -16,10 +16,11 @@ docs/
     how-to-guides/        # Practical guides organized by category
     advanced/             # Advanced topics
     examples/             # Auto-generated from examples/ Python files — do NOT edit directly
-    api-ref/              # Auto-generated API reference — do NOT edit directly
-      python/             # SDK reference
-      cli/                # CLI command reference
-      rest-api/           # REST API docs (server/ and cloud/)
+    api-ref/              # API reference — mix of auto-generated and hand-authored
+      python/             # SDK reference (auto-generated — do NOT edit directly)
+      cli/                # CLI command reference (auto-generated — do NOT edit directly)
+      rest-api/           # REST API docs (server/ and cloud/) (auto-generated — do NOT edit directly)
+      events/             # Events reference catalog — hand-authored, editable
     release-notes/        # Version release notes
     img/                  # Images organized by section
   integrations/           # Integration-specific docs (prefect-aws, prefect-gcp, etc.)
@@ -33,7 +34,8 @@ docs/
 ## Auto-generated content — do not edit
 
 - `v3/examples/` — generated from top-level `examples/` Python files by `generate_example_pages.py`
-- `v3/api-ref/` — generated API reference (Python SDK, CLI, REST API)
+- `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/` — generated API reference (Python SDK, CLI, REST API)
+- `v3/api-ref/events/` is **hand-authored** and should be edited directly when event schemas change
 - `integrations/<name>/api-ref/` — generated per-integration API reference via `mdxify` (e.g., `integrations/prefect-kubernetes/api-ref/`); regenerated on each integration release
 
 ## File format
@@ -95,7 +97,7 @@ just lint     # Run Vale linter
 
 ## Key rules
 
-1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref/`, and `integrations/<name>/api-ref/` are generated from source code.
+1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/`, and `integrations/<name>/api-ref/` are generated from source code. The exception is `v3/api-ref/events/`, which is hand-authored and should be edited when event schemas change.
 2. **Register new pages in `docs/docs.json`.** An unregistered page won't appear in navigation.
 3. **Use `.mdx` extension** for all new documentation files.
 4. **Use Mintlify components** (`<Note>`, `<Tabs>`, `<Steps>`, etc.) rather than Markdown-native admonition syntax.
PATCH

echo "Gold patch applied."
