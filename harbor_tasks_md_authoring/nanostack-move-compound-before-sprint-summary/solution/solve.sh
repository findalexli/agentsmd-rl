#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "**3. What could come next.** Suggest 2-3 concrete extensions as `/feature` comma" "ship/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -274,30 +274,31 @@ These were discovered from shipping real PRs:
 
 ## Next Step
 
-After shipping, close with two things: what was built and what could come next.
+After shipping, two things happen in order:
+
+**First: capture learnings.** Run compound immediately:
+
+```
+Use Skill tool: skill="compound"
+```
+
+Do not ask. Do not skip. Compound reads the sprint artifacts and saves solutions for future sprints.
+
+**Then: close the sprint.** This is the last thing the user sees. Make it count.
 
 **1. What was built.** Summarize what the user now has in plain language. Not phase names or artifact counts. What does the thing DO, where is it, and how to use it.
 
-**2. What could come next.** Suggest 2-3 concrete extensions based on what was built. These should be things the user can say right now to start a new sprint. Frame them as natural next steps, not feature requests.
+**2. How to use it.** Show the exact command or URL to try it right now.
+
+**3. What could come next.** Suggest 2-3 concrete extensions as `/feature` commands the user can run immediately.
 
 Example:
 
-> Sprint complete. You have a habit tracker with a GitHub-style contribution graph.
+> Sprint complete. You have a JSON validator CLI.
 >
-> How do you want to see it?
-> 1. Local — I'll start the server and show you how to open it
-> 2. Production — I'll guide you through deploying to the internet
-> 3. I'm done — just the commit
+> Try it: `node src/index.js test.json`
 >
 > Ideas for the next feature:
-> - `/feature Add JSON and CSV export for habit data backup`
-> - `/feature Add weekly and monthly streak counters`
-> - `/feature Add categories to organize habits by area`
->
-After presenting the summary and next steps, automatically run compound to capture learnings:
-
-```
-Use Skill tool: skill="compound"
-```
-
-Do not ask. Do not skip. Compound reads the sprint artifacts and saves solutions for future sprints.
+> - `/feature Add --format flag to pretty-print valid JSON`
+> - `/feature Add directory mode: jsonlint schemas/*.json`
+> - `/feature Add --fix mode that auto-corrects trailing commas`
PATCH

echo "Gold patch applied."
