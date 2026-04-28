#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "Use the actual year the file was created \u2014 never a placeholder, never a year ran" ".opencode/skills/qtpass-fixing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-fixing/SKILL.md b/.opencode/skills/qtpass-fixing/SKILL.md
@@ -167,16 +167,19 @@ Use "cannot" instead of "can't" for formal consistency:
 // On Windows, we cannot safely backup
 ```
 
-### Copyright Year in Templates
+### Copyright Year in SPDX Headers
 
-Use `YYYY` as placeholder instead of current year:
+Use the actual year the file was created — never a placeholder, never a year range. Repository convention is a single literal year (the existing files are 2014/2015/2016/2018/2020/2026, all real years; PR #1162 review explicitly flagged `YYYY` placeholders).
 
 ```cpp
-// Bad
-// SPDX-FileCopyrightText: 2026 Your Name
-
-// Good
+// Bad — placeholder; reviewers will ask for a real year
 // SPDX-FileCopyrightText: YYYY Your Name
+
+// Bad — year range
+// SPDX-FileCopyrightText: 2014-2026 Your Name
+
+// Good — single real year
+// SPDX-FileCopyrightText: 2026 Your Name
 ```
 
 ### Return After Dialog Rejection
PATCH

echo "Gold patch applied."
