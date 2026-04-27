#!/bin/bash
# Gold solution for apache/superset#38742.
# Adds STAR_EXCEPT = "EXCLUDE" to the Firebolt SQLGlot Generator so that
# `SELECT * EXCLUDE (col)` round-trips through the Firebolt dialect with
# EXCLUDE preserved instead of being rewritten to EXCEPT.
set -euo pipefail

cd /workspace/superset

TARGET="superset/sql/dialects/firebolt.py"

# Idempotency: bail out if the fix is already applied.
if grep -q 'STAR_EXCEPT = "EXCLUDE"' "${TARGET}"; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/sql/dialects/firebolt.py b/superset/sql/dialects/firebolt.py
index d0a562dfa5e1..f930da0e2d1d 100644
--- a/superset/sql/dialects/firebolt.py
+++ b/superset/sql/dialects/firebolt.py
@@ -58,6 +58,8 @@ class Generator(generator.Generator):
         Custom generator for Firebolt.
         """

+        STAR_EXCEPT = "EXCLUDE"
+
         TYPE_MAPPING = {
             **generator.Generator.TYPE_MAPPING,
             exp.DataType.Type.VARBINARY: "BYTEA",
PATCH

echo "Patch applied successfully."
grep -n 'STAR_EXCEPT' "${TARGET}" || true
