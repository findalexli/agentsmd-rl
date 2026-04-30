#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "- Do not copy or forward personal excerpts outside the current workspace/session" "prompts/munger-observer/SKILL.md" && grep -qF "- In DMs/private channels, require explicit user confirmation before broad histo" "skills/context-recovery/SKILL.md" && grep -qF "- Any mutating action (pause/enable/edit bids/budgets) requires explicit confirm" "skills/google-ads/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/prompts/munger-observer/SKILL.md b/prompts/munger-observer/SKILL.md
@@ -77,3 +77,10 @@ Automated daily review applying Charlie Munger's mental models to surface blind
 Set up a cron job for daily automated review:
 - Recommended time: End of workday (e.g., 5pm local)
 - Trigger message: `MUNGER_OBSERVER_RUN`
+
+## Privacy Addendum
+
+- Analyze only the minimum required memory/session span for the requested review.
+- Exclude credentials, financial account numbers, health data, and private identifiers from outputs.
+- Do not copy or forward personal excerpts outside the current workspace/session without explicit user instruction.
+
diff --git a/skills/context-recovery/SKILL.md b/skills/context-recovery/SKILL.md
@@ -268,3 +268,12 @@ User message: "did this happen?"
 > - Nexus sessions: `~/.clawdbot-duke-leto/archive/nexus-sessions/` (96 files)
 >
 > Shall I proceed with the extraction?"
+
+## Privacy Guardrails (Required)
+
+- Default to minimum retrieval scope:
+  - last 24h or last 50 messages (whichever is smaller), unless user asks for more.
+- In DMs/private channels, require explicit user confirmation before broad history scans.
+- Do not persist recovered summaries to memory files without explicit approval.
+- Never include secrets/tokens in recovered summaries; replace with `[REDACTED]`.
+
diff --git a/skills/google-ads/SKILL.md b/skills/google-ads/SKILL.md
@@ -199,3 +199,11 @@ When reporting findings, use tables:
 - **Authentication failed**: Refresh OAuth token, check `google-ads.yaml`
 - **Developer token rejected**: Ensure token is approved (not test mode)
 - **Customer ID error**: Use 10-digit ID without dashes
+
+## Security & Change-Control Addendum
+
+- Default mode is read-only audit/reporting.
+- Any mutating action (pause/enable/edit bids/budgets) requires explicit confirmation listing impacted entities first.
+- Browser mode must be user-attended for account-affecting actions.
+- Protect `~/.google-ads.yaml` permissions and never echo tokens/secrets in terminal output.
+
PATCH

echo "Gold patch applied."
