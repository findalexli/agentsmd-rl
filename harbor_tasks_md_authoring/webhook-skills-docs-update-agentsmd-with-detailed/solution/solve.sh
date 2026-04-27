#!/usr/bin/env bash
set -euo pipefail

cd /workspace/webhook-skills

# Idempotency guard
if grep -qF "This runs all example tests and uses Claude to review the skill against provider" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -739,14 +739,51 @@ echo "  {provider}-express   - {Provider} webhook handling in Express"
 
 When reviewing a provider skill (e.g. from a pull request or before merging):
 
-1. **Use the checklist** — In "Contributing a New Provider Skill" above, verify all items under Core Files, Examples (per framework), and **Integration**.
-2. **Integration requirements** — Confirm the skill is wired into:
-   - `README.md` — Provider Skills table
-   - `scripts/test-agent-scenario.sh` — at least one scenario (e.g. `{provider}-express`) in `usage()` and `get_scenario_config()`
-   - `.github/workflows/test-examples.yml` — provider in all three matrices (express, nextjs, fastapi)
-3. **Skill content** — Check SKILL.md has: frontmatter, "When to Use This Skill", "Resources" (or "Reference Materials"), "Related Skills" with **absolute GitHub URLs** (`https://github.com/hookdeck/webhook-skills/tree/main/skills/{skill-name}`), and for provider skills a "Recommended: webhook-handler-patterns" section linking to idempotency, error-handling, retry-logic.
-4. **Tests** — Run example tests: `./scripts/test-all-examples.sh` or per skill `cd skills/{provider}-webhooks/examples/express && npm test` (and nextjs, fastapi). Ensure test scripts exit (e.g. `"test": "vitest run"` not `"vitest"`).
-5. **More detail** — See [CONTRIBUTING.md](CONTRIBUTING.md) for the generator workflow, acceptance thresholds, and manual review steps.
+### Step 1: Run Automated Review (Primary)
+
+First, checkout the PR branch and run the automated review:
+
+```bash
+# Checkout the PR branch
+git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
+git checkout pr-<PR_NUMBER>
+
+# Run automated review (runs tests + AI review against provider docs)
+./scripts/generate-skills.sh review {provider} --no-worktree
+```
+
+This runs all example tests and uses Claude to review the skill against provider documentation for accuracy. See [CONTRIBUTING.md](CONTRIBUTING.md) for acceptance thresholds (0 critical, ≤1 major, ≤2 minor issues).
+
+### Step 2: Verify Integration (Not Covered by Automation)
+
+The automated review checks skill content and tests, but does **not** verify integration with repository infrastructure. Manually confirm:
+
+1. **README.md** — Provider added to Provider Skills table
+2. **scripts/test-agent-scenario.sh** — At least one scenario added (e.g. `{provider}-express`) in both `usage()` and `get_scenario_config()`
+3. **.github/workflows/test-examples.yml** — Provider added to all three test matrices (express, nextjs, fastapi)
+
+### Step 3: Spot-Check Skill Content
+
+Verify SKILL.md has required sections:
+- Frontmatter with name, description, license, metadata
+- "When to Use This Skill" section
+- "Resources" or "Reference Materials" section
+- "Related Skills" with **absolute GitHub URLs** (`https://github.com/hookdeck/webhook-skills/tree/main/skills/{skill-name}`)
+- For provider skills: "Recommended: webhook-handler-patterns" section
+
+### Quick Commands
+
+```bash
+# Run tests for a specific skill
+cd skills/{provider}-webhooks/examples/express && npm test
+cd skills/{provider}-webhooks/examples/nextjs && npm test
+cd skills/{provider}-webhooks/examples/fastapi && pytest test_webhook.py -v
+
+# Run all example tests
+./scripts/test-all-examples.sh
+```
+
+Ensure test scripts exit properly (e.g. `"test": "vitest run"` not `"vitest"`).
 
 ## Related Resources
 
PATCH

echo "Gold patch applied."
