#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tracee

# Idempotency guard
if grep -qF "# BAD: No == in [ ] for max portability" ".cursor/rules/shell-style-guide.mdc" && grep -qF "- arrows to `->` or the equivalent word (e.g., \"returns\", \"maps to\") depending o" ".cursor/rules/text-ascii-safety.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/shell-style-guide.mdc b/.cursor/rules/shell-style-guide.mdc
@@ -1428,7 +1428,7 @@ var+="suffix"                  # Bash only (use var="${var}suffix" in sh)
 # BAD: No {n..m} brace expansion
 for i in {1..10}; do           # Bash only (use while loop in sh)
 
-# BAD: No ==  in [ ] for max portability
+# BAD: No == in [ ] for max portability
 [ "${a}" == "${b}" ]           # Use = instead for POSIX
 
 # BAD: No [[ ]] regex matching
diff --git a/.cursor/rules/text-ascii-safety.mdc b/.cursor/rules/text-ascii-safety.mdc
@@ -24,7 +24,11 @@ markdown, comments, and generated text. There are no doc-only exceptions.
   - any other non-printing Unicode control chars (except newline/tab where valid)
 
 - If a forbidden char is found, replace it with ASCII:
-  - dashes to `-`, curly single quotes to `'`, curly double quotes to `"`, and bullets/arrows to `-` or words.
+  - dashes to `-`
+  - curly single quotes to `'`
+  - curly double quotes to `"`
+  - bullets to `-`
+  - arrows to `->` or the equivalent word (e.g., "returns", "maps to") depending on context
 
 ## Mandatory Review Check
 
PATCH

echo "Gold patch applied."
