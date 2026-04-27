#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "# BAD \u2014 three scans, three answers (3\u00d7 the cost for the same information)" "exploring-codebases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/exploring-codebases/SKILL.md b/exploring-codebases/SKILL.md
@@ -9,7 +9,7 @@ description: >-
   the divergent "what's here?" skill — for targeted "where is X?" queries,
   use searching-codebases instead.
 metadata:
-  version: 2.2.0
+  version: 2.2.1
 ---
 
 # Exploring Codebases
@@ -71,12 +71,20 @@ repo" exploration, skip drilling and go to step 3 — featuring surfaces
 the interesting paths for you. Drill when a user asked about a specific
 subsystem, or when step 3's output raises a question that needs source.
 
-When you do drill, BATCH queries in one call — each extra query adds
-~0ms, separate invocations re-scan from scratch:
+**When you do drill, batch queries in one invocation.** Every treesit
+call pays the full scan cost. Multiple queries added to the same command
+share that scan and each additional query adds ~0ms. If you're about to
+make a second treesit call on the same path, fold it into the first.
 
 ```bash
+# GOOD — one scan, three answers
 $PYTHON $TREESIT /tmp/$REPO --path=SUBDIR --detail=full \
   'find:*Handler*:function' 'source:main' 'refs:Config'
+
+# BAD — three scans, three answers (3× the cost for the same information)
+$PYTHON $TREESIT /tmp/$REPO --path=SUBDIR --detail=full
+$PYTHON $TREESIT /tmp/$REPO 'find:*Handler*:function'
+$PYTHON $TREESIT /tmp/$REPO 'refs:Config'
 ```
 
 ### 3. Feature synthesis
PATCH

echo "Gold patch applied."
