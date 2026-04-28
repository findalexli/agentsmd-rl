#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-governance-toolkit

# Idempotency guard
if grep -qF "For major design changes, always ask the maintainer (@imran-siddique) before pro" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,5 +1,17 @@
 # Copilot Instructions for agent-governance-toolkit
 
+## Decision Escalation
+
+For major design changes, always ask the maintainer (@imran-siddique) before proceeding:
+- New packages or modules that change the repo structure
+- Cross-cutting changes spanning 3+ packages
+- Security model changes (identity, trust, policy engine)
+- Breaking API changes to public interfaces
+- New framework integrations or SDK additions
+- Changes to CI/CD pipeline architecture
+
+Do NOT auto-merge large feature PRs without maintainer review.
+
 ## PR Merge Workflow
 
 When merging PRs, follow this sequence for EACH PR (do not batch):
PATCH

echo "Gold patch applied."
