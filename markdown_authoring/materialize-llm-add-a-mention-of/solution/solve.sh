#!/usr/bin/env bash
set -euo pipefail

cd /workspace/materialize

# Idempotency guard
if grep -qF "Some compositions (e.g. platform-checks, upgrade, pg-cdc multi-version) run the" ".agents/skills/mz-test/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/mz-test/SKILL.md b/.agents/skills/mz-test/SKILL.md
@@ -56,6 +56,33 @@ bin/mzcompose --find testdrive run default -- FILENAME.td
 
 `FILENAME.td` is a file in `test/testdrive/`, relative to that directory (not the repo root).
 
+Some compositions (e.g. platform-checks, upgrade, pg-cdc multi-version) run the
+same `.td` file against multiple Materialize versions. When a change alters
+version-sensitive output (e.g. the result of a `SHOW`, a system-catalog query,
+or the exact text of an error message), gate the affected lines with version
+guards so each version asserts on the output it actually produces:
+
+```
+>[version<2602300] SHOW some_setting
+old_default
+
+>[version>=2602300] SHOW some_setting
+new_default
+
+![version<2602300] SELECT * FROM t1_update;
+contains:Invalid data in source, saw retractions
+
+![version>=2602300] SELECT * FROM t1_update;
+contains:negative record multiplicity
+```
+
+The `[version...]` guard goes immediately after the directive sigil (`>` for a
+query expecting success, `!` for one expecting an error, etc.) and before the
+SQL. The version is encoded as `MMmmmpp` (e.g. `26.23.0` → `2602300`); see
+`src/build-info/src/lib.rs::version_num`. Existing examples:
+`test/pg-cdc-old-syntax/privileges.td`,
+`test/pg-cdc/publication-with-publish-option.td`.
+
 ## pgtest
 
 Run pgtest files with:
PATCH

echo "Gold patch applied."
