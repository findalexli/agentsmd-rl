#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rulesync

# Idempotency guard
if grep -qF "2. **Proposed Solution:** What solution, direction, or next step is suggested in" ".rulesync/skills/explain-issue/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.rulesync/skills/explain-issue/SKILL.md b/.rulesync/skills/explain-issue/SKILL.md
@@ -0,0 +1,30 @@
+---
+name: explain-issue
+description: "Explain a GitHub issue: the background problem and the proposed solution"
+targets:
+  - "*"
+---
+
+target_issue = $ARGUMENTS
+
+If target_issue is not provided, ask the user which issue to explain.
+
+## Step 1: Gather Issue Information
+
+Run the following in parallel:
+
+- Get the issue description and metadata: `gh issue view <issue_number>`
+- Get the issue comments: `gh issue view <issue_number> --comments`
+
+If the issue references related pull requests, commits, or files that are needed to understand the solution, gather that context as well.
+
+## Step 2: Analyze and Explain
+
+Based on the issue content, explain the following two aspects:
+
+1. **Background (Problem/Motivation):** What problem, limitation, or user need does this issue describe? Why does it matter?
+2. **Proposed Solution:** What solution, direction, or next step is suggested in the issue discussion? Summarize the expected approach, scope, and important constraints if they are mentioned.
+
+If the issue does not contain enough information about the solution, explicitly say that the solution is still undecided or unspecified.
+
+Keep the explanation concise and focused. Use the language of the current conversation (follow the user's language).
PATCH

echo "Gold patch applied."
