#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uberon

# Idempotency guard
if grep -qF "- before committing, src/ontology/uberon-edit.obo should be reserialised via `ro" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -39,6 +39,7 @@ This includes instructions for editing the uberon ontology.
 - if you like you can edit multiple terms in one batch, e.g. `terms/my_batch.obo`
      - `obo-checkout.pl src/ontology/uberon-edit.obo terms/my_batch.obo`
 - checking in will update the edit file and remove the file from `terms/`
+- before committing, src/ontology/uberon-edit.obo should be reserialised via `robot convert -i  src/ontology/uberon-edit.obo -f obo -o src/ontology/uberon-edit.obo`
 - Commits are then made on src/ontology/uberon-edit.obo as appropriate
 - Note that `obo-checkin.pl` and `obo-checkout.pl` are in your PATH, no need to search for it
 - New terms must have:
PATCH

echo "Gold patch applied."
