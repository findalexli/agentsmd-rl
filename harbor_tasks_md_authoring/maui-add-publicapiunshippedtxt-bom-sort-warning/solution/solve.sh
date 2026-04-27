#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotency guard
if grep -qF "Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-p" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -138,6 +138,26 @@ When working with public API changes:
 - **Use `dotnet format analyzers`** if having trouble
 - **If files are incorrect**: Revert all changes, then add only the necessary new API entries
 
+**🚨 CRITICAL: `#nullable enable` must be line 1**
+
+Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-prefixed: `﻿#nullable enable`) on the **first line**. If this line is moved or removed, the analyzer treats it as a declared API symbol and emits **RS0017** errors.
+
+**Never sort these files with plain `sort`** — the BOM bytes (`0xEF 0xBB 0xBF`) sort after ASCII characters under `LC_ALL=C`, pushing `#nullable enable` to the bottom of the file.
+
+When resolving merge conflicts or adding entries, use this safe pattern that preserves line 1:
+```bash
+for f in $(git diff --name-only --diff-filter=U | grep "PublicAPI.Unshipped.txt"); do
+  # Extract and preserve the #nullable enable line (with or without BOM)
+  HEADER=$(head -1 "$f" | grep -o '.*#nullable enable' || echo '#nullable enable')
+  # Strip conflict markers, remove all #nullable lines, sort+dedup the API entries
+  grep -v '^<<<<<<\|^======\|^>>>>>>\|#nullable enable' "$f" | LC_ALL=C sort -u | sed '/^$/d' > /tmp/api_fix.txt
+  # Reassemble: header first, then sorted entries
+  printf '%s\n' "$HEADER" > "$f"
+  cat /tmp/api_fix.txt >> "$f"
+  git add "$f"
+done
+```
+
 ### Branching
 - `main` - For bug fixes without API changes
 - `net10.0` - For new features and API changes
PATCH

echo "Gold patch applied."
