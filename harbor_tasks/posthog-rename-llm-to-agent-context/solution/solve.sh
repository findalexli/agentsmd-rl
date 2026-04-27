#!/usr/bin/env bash
set -euo pipefail

# Apply the gold rename: "LLM context" → "🤖 Agent context" across the
# PR template, AGENTS.md and AI_POLICY.md.
#
# We write the three files in their final (gold) state directly. This is a
# faithful reproduction of the upstream merge commit
# (74a5d94a49ec956a7b310945f24d6c1e83727908) for the three touched files.

cd /workspace/posthog

# Idempotency guard — bail if the rename already landed.
if grep -qxF '## 🤖 Agent context' .github/pull_request_template.md 2>/dev/null; then
    echo "solve.sh: gold already applied — skipping"
    exit 0
fi

cat > .github/pull_request_template.md <<'PR_TEMPLATE_EOF'
## Problem

<!-- Who are we building for, what are their needs, why is this important? -->

<!-- Does this fix an issue? Uncomment the line below with the issue ID to automatically close it when merged -->
<!-- Closes #ISSUE_ID -->

## Changes

<!-- If there are frontend changes, please include screenshots. -->
<!-- If a reference design was involved, include a link to the relevant Figma frame! -->

## How did you test this code?

<!-- Describe steps to reproduce and verify the changes, and what the expected behavior is. -->
<!-- Include automated tests if possible, otherwise describe the manual testing routine. -->
<!-- Agents: do NOT claim manual testing you haven't done. State that you're an agent and list only the automated tests you actually ran. -->

👉 _Stay up-to-date with [PostHog coding conventions](https://posthog.com/docs/contribute/coding-conventions) for a smoother review._

## Publish to changelog?

<!-- For features only -->

<!-- If publishing, you must provide changelog details in the #changelog Slack channel. You will receive a follow-up PR comment or notification. -->

<!-- If not, write "no" or "do not publish to changelog" to explicitly opt-out of posting to #changelog. Removing this entire section will not prevent posting. -->

## Docs update

<!-- Add the `skip-inkeep-docs` label if this PR should not trigger an automatic docs update from the Inkeep agent. -->

## 🤖 Agent context

<!-- Fill this section if an agent co-authored or authored this PR. Remove it for fully human-authored PRs. -->
<!-- Include: tools/agent used, link to session, key decisions made, and anything that helps reviewers. -->
<!-- Rules for agent-authored PRs:
     - All PRs must be attributable to a human author, even if agent-assisted.
     - Do not add a human Co-authored-by just for the sake of attribution — if no human was involved in the changes, own it as agent-authored.
     - Agent-authored PRs always require human review — do not self-merge or auto-approve.
     - Do NOT claim manual testing you haven't done.
-->
PR_TEMPLATE_EOF

# AGENTS.md: only one line changes, the rest of this 200-line file is preserved.
python3 - <<'PY'
from pathlib import Path
p = Path("AGENTS.md")
src = p.read_text()
old = "Always uncomment and fill the `## LLM context` section for agent-authored PRs.\n"
new = "Always fill the `## 🤖 Agent context` section when creating PRs.\n"
if old not in src:
    raise SystemExit(f"AGENTS.md: expected line not found: {old!r}")
p.write_text(src.replace(old, new, 1))
PY

# AI_POLICY.md: two adjacent disclosure lines change; rest preserved.
python3 - <<'PY'
from pathlib import Path
p = Path("AI_POLICY.md")
src = p.read_text()
old = (
    "Our [PR template](.github/pull_request_template.md) includes an LLM context section — please use it (most agents will pick it up automatically).\n"
    "If an LLM co-authored or authored your PR, say so and leave context about the tools and session.\n"
)
new = (
    "Our [PR template](.github/pull_request_template.md) includes an Agent context section — please use it (most agents will pick it up automatically).\n"
    "If an agent co-authored or authored your PR, say so and leave context about the tools and session.\n"
)
if old not in src:
    raise SystemExit("AI_POLICY.md: expected disclosure block not found")
p.write_text(src.replace(old, new, 1))
PY

echo "solve.sh: gold rename applied"
