#!/usr/bin/env bash
set -euo pipefail

cd /workspace/go-ontology

# Idempotency guard
if grep -qF "Preserve ALL existing term_tracker_items. Preserve existing comments and append " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -115,6 +115,8 @@ Note the pattern for names and definitions.
 No relationship should point to an obsolete term - when you obsolete a term, you may need to also rewire
 terms to "skip" the obsoleted term.
 
+Preserve ALL existing term_tracker_items. Preserve existing comments and append obsoletion reason.
+
 ## Other metadata
 
 - Link back to the issue you are dealing with using the `term_tracker_item`
PATCH

echo "Gold patch applied."
