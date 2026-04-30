#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nemoclaw

# Idempotency guard
if grep -qF "| `nemoclaw-maintainer-day` | Daytime loop: pick the highest-value version-targe" ".agents/skills/nemoclaw-skills-guide/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/nemoclaw-skills-guide/SKILL.md b/.agents/skills/nemoclaw-skills-guide/SKILL.md
@@ -21,10 +21,10 @@ The prefix in each skill name indicates who it is for.
 For end users operating a NemoClaw sandbox.
 Covers installation, inference configuration, network policy management, monitoring, remote deployment, security configuration, workspace management, and reference material.
 
-### `nemoclaw-maintainer-*` (3 skills)
+### `nemoclaw-maintainer-*` (6 skills)
 
 For project maintainers.
-Covers cutting releases, finding PRs to review, and performing security code reviews.
+Covers the daily maintainer cadence (morning standup, daytime loop, evening handoff), cutting releases, finding PRs to review, and performing security code reviews.
 
 ### `nemoclaw-contributor-*` (1 skill)
 
@@ -51,6 +51,9 @@ Covers drafting documentation updates from recent commits.
 
 | Skill | Summary |
 |-------|---------|
+| `nemoclaw-maintainer-morning` | Morning standup: triage the backlog, determine the day's target version, label selected items, surface stragglers, and output the daily plan. |
+| `nemoclaw-maintainer-day` | Daytime loop: pick the highest-value version-targeted item and execute the right workflow (merge gate, salvage, security sweep, test gaps, hotspot cooling, or sequencing). Designed for `/loop`. |
+| `nemoclaw-maintainer-evening` | End-of-day handoff: check version progress, bump stragglers to the next patch, generate a QA handoff summary, and cut the release tag. |
 | `nemoclaw-maintainer-cut-release-tag` | Cut an annotated semver tag on main, move the `latest` floating tag, and push both to origin. |
 | `nemoclaw-maintainer-find-review-pr` | Find open PRs labeled security + priority-high, link each to its issue, detect duplicates, and present a review summary. |
 | `nemoclaw-maintainer-security-code-review` | Perform a 9-category security review of a PR or issue, producing per-category PASS/WARNING/FAIL verdicts. |
@@ -61,25 +64,20 @@ Covers drafting documentation updates from recent commits.
 |-------|---------|
 | `nemoclaw-contributor-update-docs` | Scan recent git commits for user-facing changes and draft or update the corresponding documentation pages. |
 
-## Quick Decision Guide
-
-Use this table to jump directly to the right skill.
-
-| I want to... | Load this skill |
-|---------------|-----------------|
-| Install NemoClaw or onboard for the first time | `nemoclaw-user-get-started` |
-| Understand what NemoClaw is or how it fits together | `nemoclaw-user-overview` |
-| Switch my inference provider or model | `nemoclaw-user-configure-inference` |
-| Set up a local model server (Ollama, vLLM, NIM) | `nemoclaw-user-configure-inference` |
-| Approve or deny a blocked network request | `nemoclaw-user-manage-policy` |
-| Add or remove endpoints from the network policy | `nemoclaw-user-manage-policy` |
-| Check sandbox logs, status, or health | `nemoclaw-user-monitor-sandbox` |
-| Deploy to a remote GPU or cloud instance | `nemoclaw-user-deploy-remote` |
-| Set up Telegram or a chat bridge | `nemoclaw-user-deploy-remote` |
-| Review security controls or credential storage | `nemoclaw-user-configure-security` |
-| Back up or restore workspace files | `nemoclaw-user-workspace` |
-| Look up a CLI command or troubleshoot an error | `nemoclaw-user-reference` |
-| Cut a new release tag | `nemoclaw-maintainer-cut-release-tag` |
-| Find the next PR to review | `nemoclaw-maintainer-find-review-pr` |
-| Security review a pull request | `nemoclaw-maintainer-security-code-review` |
-| Update docs after landing code changes | `nemoclaw-contributor-update-docs` |
+## Getting Started
+
+Ask the user which role best describes them:
+
+- **User** — operating a NemoClaw sandbox (running, configuring, monitoring).
+- **Contributor** — contributing code or docs to the NemoClaw project.
+- **Maintainer** — triaging, reviewing, releasing, and managing the project day-to-day.
+
+Skills are cumulative. Each role includes the skills from the roles above it:
+
+| Role | Skills included | Count | Start with |
+|------|----------------|-------|------------|
+| User | `nemoclaw-user-*` | 9 | `nemoclaw-user-get-started` |
+| Contributor | `nemoclaw-user-*` + `nemoclaw-contributor-*` | 10 | `nemoclaw-user-overview` |
+| Maintainer | All skills | 16 | `nemoclaw-maintainer-morning` |
+
+After identifying the role, present the applicable skills from the Skill Catalog above and recommend the starting skill.
PATCH

echo "Gold patch applied."
