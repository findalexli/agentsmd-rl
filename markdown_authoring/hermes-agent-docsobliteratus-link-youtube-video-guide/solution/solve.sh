#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hermes-agent

# Idempotency guard
if grep -qF "https://www.youtube.com/watch?v=8fG9BrNTeHs (\"OBLITERATUS: An AI Agent Removed G" "skills/mlops/inference/obliteratus/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/mlops/inference/obliteratus/SKILL.md b/skills/mlops/inference/obliteratus/SKILL.md
@@ -17,6 +17,13 @@ Remove refusal behaviors (guardrails) from open-weight LLMs without retraining o
 
 **License warning:** OBLITERATUS is AGPL-3.0. NEVER import it as a Python library. Always invoke via CLI (`obliteratus` command) or subprocess. This keeps Hermes Agent's MIT license clean.
 
+## Video Guide
+
+Walkthrough of OBLITERATUS used by a Hermes agent to abliterate Gemma:
+https://www.youtube.com/watch?v=8fG9BrNTeHs ("OBLITERATUS: An AI Agent Removed Gemma 4's Safety Guardrails")
+
+Useful when the user wants a visual overview of the end-to-end workflow before running it themselves.
+
 ## When to Use This Skill
 
 Trigger when the user:
PATCH

echo "Gold patch applied."
