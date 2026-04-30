#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "If you are operating inside the canonical `neomjs/neo` repository as a core swar" ".agent/skills/pull-request/references/pull-request-workflow.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/pull-request/references/pull-request-workflow.md b/.agent/skills/pull-request/references/pull-request-workflow.md
@@ -145,6 +145,12 @@ You MUST follow this exact handoff protocol:
 - **7-day-open fallback**: The PR itself has been OPEN for >= 7 days AND no cross-family reviewer has engaged on the thread. Any cross-family thread engagement (review, comment, or status) resets the 7-day-open clock; only an `Approved` status satisfies the mandate. Deterministically verifiable via `get_conversation(pr_number)`: (a) `now - createdAt >= 7 days`, (b) `comments.nodes` contains no entry whose `author.login` resolves to the cross-family pattern. Fallback invocation MUST include the PR's `createdAt` timestamp + explicit confirmation that no cross-family engagement has occurred, embedded in the self-review comment.
 - **Emergency hotfix escalator**: `priority: P0` label OR an explicit Tobi-override comment on the PR; post-merge cross-family retrospective review REQUIRED within 7 days.
 
+### 6.2 The Core Swarm A2A Notification Mandate
+
+If you are operating inside the canonical `neomjs/neo` repository as a core swarm member (e.g., `@neo-opus-4-7`, `@neo-gemini-3-1-pro`), immediately after successfully opening a PR, you MUST send an A2A notification message via the `add_message` tool to your peer(s) informing them that the PR has been created. 
+
+This strict feedback loop prevents duplicated work and confusion over ticket ownership when multiple agents are running concurrently. This rule strictly applies only to the `neomjs/neo` repo for the core team; it does NOT affect external contributors, forks, or users of `npx neo-app` workspaces.
+
 ## 7. Review Response Protocol
 
 Once a reviewer posts `Status: Request Changes` (per the `pr-review` skill) or `Status: Comment` with actionable Required Actions, the author MUST respond via a structured comment on the PR thread. This closes the review-negotiation loop in a way both downstream human re-reviewers and automated consumers (Retrospective daemon, graph ingestion) can parse unambiguously.
PATCH

echo "Gold patch applied."
