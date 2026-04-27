#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-plugins

# Idempotency guard
if grep -qF "description: \"Deploy applications to AWS. Triggers on: deploy to AWS, host on AW" "plugins/deploy-on-aws/skills/deploy/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/deploy-on-aws/skills/deploy/SKILL.md b/plugins/deploy-on-aws/skills/deploy/SKILL.md
@@ -1,9 +1,6 @@
 ---
 name: deploy
-description: >
-  Deploy applications to AWS. Triggers on: "deploy to AWS", "host on AWS",
-  "run this on AWS", "AWS architecture", "estimate AWS cost", "generate
-  infrastructure". Analyzes any codebase and deploys to optimal AWS services.
+description: "Deploy applications to AWS. Triggers on: deploy to AWS, host on AWS, run this on AWS, AWS architecture, estimate AWS cost, generate infrastructure. Analyzes any codebase and deploys to optimal AWS services."
 ---
 
 # Deploy on AWS
PATCH

echo "Gold patch applied."
