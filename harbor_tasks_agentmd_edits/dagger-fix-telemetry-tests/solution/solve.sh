#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dagger

# Idempotent: skip if already applied
if grep -q 'e.Original.Error()' dagql/idtui/exit.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/dagql/idtui/exit.go b/dagql/idtui/exit.go
index bf592685bdf..8f59557415f 100644
--- a/dagql/idtui/exit.go
+++ b/dagql/idtui/exit.go
@@ -20,7 +20,13 @@ var Fail = ExitError{Code: 1}

 func (e ExitError) Error() string {
 	// Not actually printed anywhere.
-	return fmt.Sprintf("exit code %d", e.Code)
+	msg := fmt.Sprintf("exit code %d", e.Code)
+	if e.Original != nil {
+		// Be sure to include the original error in the message so that we can still
+		// parse out error origins.
+		msg += "\n\n" + e.Original.Error()
+	}
+	return msg
 }

 func (e ExitError) Unwrap() error {
diff --git a/skills/dagger-chores/SKILL.md b/skills/dagger-chores/SKILL.md
index 5eefa4c364f..7760cdd83c4 100644
--- a/skills/dagger-chores/SKILL.md
+++ b/skills/dagger-chores/SKILL.md
@@ -37,3 +37,9 @@ Use this checklist when asked to regenerate generated files.
 3. Search the temp file as needed instead of printing full output.

 4. Delete the temp file when done.
+
+## Regenerate Golden Tests
+
+Use this checklist when asked to regenerate telemetry golden tests.
+
+1. From the Dagger repo root, run `dagger -c 'engine-dev | test-telemetry --update | export .'`
\ No newline at end of file

PATCH

echo "Patch applied successfully."
