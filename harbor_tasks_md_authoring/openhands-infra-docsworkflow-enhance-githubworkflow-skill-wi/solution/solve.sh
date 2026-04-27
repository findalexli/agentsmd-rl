#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openhands-infra

# Idempotency guard
if grep -qF "description: This skill should be used when the user asks to \"create a PR\", \"add" ".claude/skills/github-workflow/SKILL.md" && grep -qF "--jq '[.[] | select(.user.login == \"codex[bot]\")] | .[-1] | {id: .id, submitted_" ".claude/skills/github-workflow/references/review-commands.md" && grep -qF "- **GitHub workflow**: Use `.claude/skills/github-workflow/` for PR creation, re" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/github-workflow/SKILL.md b/.claude/skills/github-workflow/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: github-workflow
-description: This skill should be used when the user asks to "create a PR", "address review comments", "resolve review threads", "retrigger Q review", "/q review", "respond to Amazon Q", "handle reviewer findings", "merge PR", "push changes", "check CI status", or mentions PR workflow, code review, or GitHub Actions checks.
+description: This skill should be used when the user asks to "create a PR", "address review comments", "resolve review threads", "retrigger Q review", "/q review", "respond to Amazon Q", "/codex review", "respond to Codex", "handle reviewer findings", "merge PR", "push changes", "check CI status", or mentions PR workflow, code review, reviewer bots, or GitHub Actions checks.
 ---
 
 # GitHub Development Workflow
@@ -9,16 +9,17 @@ This skill provides standardized guidance for the complete GitHub development wo
 
 ## Development Workflow Overview
 
-Follow this 7-step workflow for all feature development and bug fixes:
+Follow this 10-step workflow for all feature development and bug fixes:
 
 ```
 Step 1: CREATE BRANCH
   git checkout -b feat/<name> or fix/<name>
        ↓
 Step 2: IMPLEMENT CHANGES
   - Write code
-  - Update unit tests (npm run test)
-  - Update E2E test cases if needed
+  - Write new unit tests for new functionality
+  - Update existing tests if behavior changed
+  - Write/update E2E test cases if needed
        ↓
 Step 3: LOCAL VERIFICATION
   - npm run build
@@ -29,23 +30,83 @@ Step 4: COMMIT AND CREATE PR
   - git add && git commit -m "type(scope): description"
   - git push -u origin <branch-name>
   - Create PR via GitHub MCP or gh CLI
+  - Include checklist in PR description (see template below)
        ↓
 Step 5: WAIT FOR PR CHECKS
   - Monitor GitHub Actions checks
   - If FAIL → Return to Step 2
-  - If PASS → Proceed to Step 6
+  - If PASS → Update PR checklist, proceed to Step 6
        ↓
 Step 6: ADDRESS REVIEWER BOT FINDINGS
-  - Review Amazon Q Developer comments
+  - Review all bot comments (Amazon Q, Codex, etc.)
   - Fix issues or document design decisions
   - Reply DIRECTLY to each comment thread
   - RESOLVE each conversation
+  - Retrigger review: /q review, /codex review
        ↓
-Step 7: READY FOR MERGE
-  - All checks passed
-  - All comments addressed
+Step 7: ITERATE UNTIL NO FINDINGS
+  - Check for new bot findings
+  - If new findings → Return to Step 6
+  - If no findings → Update PR checklist, proceed to Step 8
+       ↓
+Step 8: DEPLOY TO STAGING
+  - Deploy changes to test/staging environment
+  - Verify deployment succeeds
+  - Update PR checklist
+       ↓
+Step 9: EXECUTE E2E TESTS
+  - Run full E2E test suite (see E2E_TEST_CASES.md)
+  - If FAIL → Return to Step 2
+    - Fix bugs or add missing test cases
+    - Push fixes and repeat from Step 5
+  - If PASS → Update PR checklist, proceed to Step 10
+       ↓
+Step 10: READY FOR MERGE (DO NOT MERGE)
+  - All CI checks passed
+  - All reviewer comments addressed
+  - Staging deployment verified
+  - E2E tests passed
+  - Update PR checklist to show all items complete
+  - STOP HERE: Report status to user
+  - User decides when to merge
+```
+
+## PR Description Template
+
+When creating a PR, include this checklist in the description. Update it as each step completes:
+
+```markdown
+## Test plan
+
+- [ ] Build passes (`npm run build`)
+- [ ] Unit tests pass (`npm run test`)
+- [ ] CI checks pass
+- [ ] Reviewer bot findings addressed (no new findings)
+- [ ] Deployed to staging
+- [ ] E2E tests pass
+
+## Checklist
+
+- [ ] New unit tests written for new functionality
+- [ ] E2E test cases updated if needed
+- [ ] Documentation updated if needed
 ```
 
+### Update PR Checklist Command
+
+After completing each step, update the PR description:
+
+```bash
+# Get current PR body
+gh pr view {pr_number} --json body --jq '.body' > /tmp/pr_body.md
+
+# Edit the checklist (mark items as [x])
+# Then update the PR
+gh pr edit {pr_number} --body "$(cat /tmp/pr_body.md)"
+```
+
+Or use the GitHub MCP tool to update the PR body directly.
+
 ## PR Check Monitoring
 
 ### Monitor CI Status
@@ -64,42 +125,58 @@ gh pr checks {pr_number}
 |-------|-------------|------------------|
 | CI / build-and-test | Build + unit tests | Fix code or update snapshots |
 | Security Scan | SAST, npm audit | Fix security issues |
-| Amazon Q Developer | Security review | Address findings or document decisions |
+| Amazon Q Developer | Security review | Address findings, retrigger with `/q review` |
+| Codex | AI code review | Address findings, retrigger with `/codex review` |
+| Other review bots | Various checks | Address findings, retrigger per bot docs |
+
+## Reviewer Bot Workflow
 
-## Amazon Q Developer Workflow
+Multiple review bots can provide automated code review findings on PRs:
 
-Amazon Q Developer provides automated security and code review findings on PRs.
+| Bot | Trigger Command | Bot Username |
+|-----|-----------------|--------------|
+| Amazon Q Developer | `/q review` | `amazon-q-developer[bot]` |
+| Codex | `/codex review` | `codex[bot]` |
+| Other bots | See bot documentation | Varies |
 
-### Handling Q Review Findings
+### Handling Bot Review Findings
 
 1. **Review all comments** - Read each finding carefully
 2. **Determine action**:
    - If valid issue → Fix the code and push
    - If false positive → Reply explaining the design decision
 3. **Reply to each thread** - Use direct reply, not general PR comment
 4. **Resolve each thread** - Mark conversation as resolved
-5. **Retrigger review** - Comment `/q review` to scan again
+5. **Retrigger review** - Comment with appropriate trigger (e.g., `/q review`, `/codex review`)
 
-### Retrigger Amazon Q Review
+### Retrigger Bot Reviews
 
 After addressing findings, trigger a new scan:
 
 ```bash
+# Amazon Q Developer
 gh pr comment {pr_number} --body "/q review"
+
+# Codex
+gh pr comment {pr_number} --body "/codex review"
 ```
 
 Wait 60-90 seconds for the review to complete, then check for new comments.
 
-### Iteration Loop
+### Iteration Loop (CRITICAL)
 
-Repeat until Q review finds no more issues:
+**Repeat until review bots find no more issues:**
 
 1. Address findings (fix code or explain design)
 2. Reply to each comment thread
 3. Resolve all threads
-4. Trigger `/q review`
-5. Check for new findings
-6. If new findings → repeat from step 1
+4. Trigger review command (`/q review`, `/codex review`, etc.)
+5. Wait 60-90 seconds
+6. Check for new findings
+7. **If new findings → repeat from step 1**
+8. **Only proceed to merge when no new positive findings appear**
+
+This loop is essential - review bots may find new issues in your fixes.
 
 ## Review Thread Management
 
@@ -201,6 +278,7 @@ The referenced file {filename} exists in the repository at {path}. This is a ref
 | Reply to comment | `gh api ... -X POST -F in_reply_to=<id>` |
 | Resolve thread | GraphQL `resolveReviewThread` mutation |
 | Trigger Q review | `gh pr comment {pr} --body "/q review"` |
+| Trigger Codex review | `gh pr comment {pr} --body "/codex review"` |
 | Check thread status | GraphQL query for `reviewThreads` |
 
 ## Additional Resources
diff --git a/.claude/skills/github-workflow/references/review-commands.md b/.claude/skills/github-workflow/references/review-commands.md
@@ -56,12 +56,23 @@ gh api repos/{owner}/{repo}/pulls/{pr}/reviews \
   --jq '[.[] | select(.user.login == "amazon-q-developer[bot]")] | .[-1] | {id: .id, submitted_at: .submitted_at}'
 ```
 
-### Trigger Amazon Q Review
+Get the most recent Codex review:
 
-Add a comment to trigger Amazon Q Developer to rescan:
+```bash
+gh api repos/{owner}/{repo}/pulls/{pr}/reviews \
+  --jq '[.[] | select(.user.login == "codex[bot]")] | .[-1] | {id: .id, submitted_at: .submitted_at}'
+```
+
+### Trigger Bot Reviews
+
+Add a comment to trigger bot rescans:
 
 ```bash
+# Amazon Q Developer
 gh pr comment {pr} --body "/q review"
+
+# Codex
+gh pr comment {pr} --body "/codex review"
 ```
 
 ### Monitor PR Checks
@@ -224,18 +235,29 @@ gh api repos/{owner}/{repo}/pulls/{pr}/comments \
 # Use the batch resolve script or loop above
 ```
 
-4. **Trigger new review**:
+4. **Trigger new review** (use appropriate bot command):
 ```bash
+# Amazon Q
 gh pr comment {pr} --body "/q review"
+
+# Codex
+gh pr comment {pr} --body "/codex review"
 ```
 
 5. **Wait and check for new comments**:
 ```bash
 sleep 90
+# Check Amazon Q
 gh api repos/{owner}/{repo}/pulls/{pr}/reviews \
   --jq '[.[] | select(.user.login == "amazon-q-developer[bot]")] | .[-1]'
+
+# Check Codex
+gh api repos/{owner}/{repo}/pulls/{pr}/reviews \
+  --jq '[.[] | select(.user.login == "codex[bot]")] | .[-1]'
 ```
 
+6. **Iterate until no new positive findings** - If new findings appear, repeat from step 1
+
 ### Check if All Threads Resolved
 
 ```bash
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,10 +1,25 @@
 # CLAUDE.md
 
+## Development Workflow (MANDATORY)
+
+**CRITICAL**: All feature development and bug fixes MUST strictly follow the `github-workflow` skill.
+
+Before ANY code changes involving functionality:
+1. **Invoke skill**: Use `/github-workflow` or load the skill
+2. **Follow the 10-step workflow** - NO shortcuts allowed
+3. **Do NOT merge** - Report status and wait for user decision
+
+The workflow includes:
+- Step 2: Write new unit tests + update E2E test cases
+- Steps 6-7: Address ALL reviewer bot findings (Q, Codex, etc.) and iterate until no new findings
+- Steps 8-9: Deploy to staging + run full E2E tests
+- Step 10: Report ready status (DO NOT MERGE)
+
 ## Quick Reference
 
 - **Branch naming**: `feat/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`
 - **Commit format**: `type(scope): description`
-- **GitHub workflow**: Use `.claude/skills/github-workflow/` for PR creation, review comments, Amazon Q
+- **GitHub workflow**: Use `.claude/skills/github-workflow/` for PR creation, review comments, reviewer bots
 
 ### Source Control Rules
 
PATCH

echo "Gold patch applied."
