#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "Automated workflow to resolve all issues surfaced in a pr-review report \u2014 parse " ".claude/skills/pr-fix/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-fix/SKILL.md b/.claude/skills/pr-fix/SKILL.md
@@ -8,7 +8,7 @@ description: |
 
 # PR Review Fix Skill
 
-Automated workflow to resolve all issues surfaced in a pr-review report — parse summary → detect PR status → create fix branch or checkout original branch → fix by priority → quality gate → commit → publish → verify.
+Automated workflow to resolve all issues surfaced in a pr-review report — parse summary → detect PR status → create fix branch or checkout original branch → **triage & validate** → fix by priority → quality gate → commit → publish → verify.
 
 **Announce at start:** "I'm using pr-fix skill to fix all review issues."
 
@@ -118,7 +118,7 @@ If state is `MERGED`: abort with:
 
 If `IS_FORK=true` AND `CAN_MODIFY=false`: set `FORK_FALLBACK=true` and continue.
 In this path (Step 3 onwards), fixes are applied on a new branch in the main repo instead of the fork.
-Save `FIX_BRANCH=bot/fix-pr-<PR_NUMBER>` for use in Step 3 and Step 7.
+Save `FIX_BRANCH=bot/fix-pr-<PR_NUMBER>` for use in Step 3 and Step 8.
 
 ---
 
@@ -179,15 +179,101 @@ Save `REPO_ROOT` and `WORKTREE_DIR` for later steps. All file reads, edits, lint
 
 ---
 
-### Step 4 — Fix Issues by Priority
+### Step 4 — Triage & Validate
+
+Before fixing anything, independently verify each issue from the review report. This prevents blind application of potentially incorrect or suboptimal fixes.
+
+All file operations in this step use worktree paths (`$WORKTREE_DIR/<relative_path>`).
+
+**For each CRITICAL / HIGH / MEDIUM issue (skip LOW), perform three-layer triage:**
+
+#### Layer 1 — Is the issue real?
+
+Read the target file and the surrounding context. Independently assess whether the reported problem actually exists:
+
+- Does the problematic code pattern still exist at the reported location? (Review may be based on an older version)
+- Is the reported behavior actually a bug, or is it intentional design? (Check PR description, related files, project conventions)
+- Does the reviewer's reasoning hold up given the full context?
+
+If the issue is **not real** → mark as `DISMISSED` with a clear reason.
+
+#### Layer 2 — Is the suggested fix reasonable?
+
+If the issue is real, evaluate the review report's "修复建议":
+
+- Does the suggested fix actually resolve the problem?
+- Does it introduce side effects (type errors, behavioral changes, broken imports)?
+- Is it consistent with the project's patterns and conventions?
+
+If the suggestion is **reasonable** → mark as `FIX` (adopt the original suggestion).
+
+#### Layer 3 — Is there a better fix?
+
+If the suggestion is flawed or suboptimal, consider an alternative:
+
+- The alternative must target the **same file(s) and same code area** — do not expand scope
+- The alternative must solve the **same problem**, just with a different approach
+- The alternative's diff should not be significantly larger than the original suggestion — if it is, the change likely exceeds fix scope and should be a separate PR
+
+If a better fix exists → mark as `FIX_ALT` with the alternative plan.
+If no better fix exists → fall back to `FIX` (adopt the original suggestion despite its flaws, as long as it doesn't make things worse).
+
+#### Triage output
+
+Build an enhanced issue list. Each issue now has:
+
+| Field      | Values                          | Description                                                                  |
+| ---------- | ------------------------------- | ---------------------------------------------------------------------------- |
+| `verdict`  | `FIX` / `FIX_ALT` / `DISMISSED` | Triage decision                                                              |
+| `reason`   | free text                       | Why this verdict was chosen                                                  |
+| `fix_plan` | code/description                | The actual fix to apply (`FIX`: original suggestion; `FIX_ALT`: alternative) |
+
+#### CRITICAL issue constraints
+
+**Automation mode (`--automation`):** CRITICAL issues **cannot** be dismissed. If triage concludes a CRITICAL issue is a false positive, the fixer must escalate — abort the fix workflow and transfer to human review:
+
+```bash
+gh pr edit <PR_NUMBER> --remove-label "bot:fixing" --add-label "bot:needs-human-review"
+gh pr comment <PR_NUMBER> --body "<!-- pr-automation-bot -->
+⚠️ Triage 阶段发现 CRITICAL 问题 #<issue_number> 可能为误报，但自动化流程无法自行驳回 CRITICAL 级别问题，已转交人工确认。
+
+**问题：** <issue description>
+**驳回理由：** <reason>"
+```
+
+Then **EXIT**.
+
+**Interactive mode (no `--automation`):** Present the dismissal reasoning to the user and ask for confirmation:
+
+> Triage 认为 CRITICAL 问题 #N 可能是误报：<reason>
+> 是否同意驳回此问题？(yes/no)
+
+- User says **yes** → mark as `DISMISSED`
+- User says **no** → mark as `FIX` (apply original suggestion)
+
+#### Post-triage check
+
+After triage, if all non-LOW issues are `DISMISSED`, abort with:
+
+> All issues were dismissed during triage — nothing to fix.
+
+In automation mode, also transfer to human review (since at least one issue was CRITICAL/HIGH/MEDIUM but all were dismissed, a human should confirm):
+
+```bash
+gh pr edit <PR_NUMBER> --remove-label "bot:fixing" --add-label "bot:needs-human-review"
+```
+
+---
+
+### Step 5 — Fix Issues by Priority
 
 All file operations in this step use worktree paths. The Read tool should target `$WORKTREE_DIR/<relative_path>`, and the Edit tool should modify files at the same worktree paths.
 
-Process issues CRITICAL → HIGH → MEDIUM only. Skip LOW. For each issue:
+Process only issues with verdict `FIX` or `FIX_ALT` from the triage output, in order CRITICAL → HIGH → MEDIUM. For each issue:
 
 1. Read the target file (use Read tool at the file path from the summary table)
 2. Locate the exact problem — match the review report's quoted code and line number
-3. Apply the fix described in the review report's "修复建议" section
+3. Apply the `fix_plan` from triage (original suggestion for `FIX`, alternative for `FIX_ALT`)
 4. After fixing each file batch, run a quick type check:
 
 ```bash
@@ -200,7 +286,7 @@ Resolve any type errors before moving to the next issue.
 
 ---
 
-### Step 5 — Full Quality Gate
+### Step 6 — Full Quality Gate
 
 All commands run inside the worktree (`$WORKTREE_DIR`):
 
@@ -215,7 +301,7 @@ bun run test
 
 ---
 
-### Step 6 — Commit
+### Step 7 — Commit
 
 Follow the [commit skill](../commit/SKILL.md) workflow. Commit message **must** reference the original PR:
 
@@ -231,7 +317,7 @@ Review follow-up for #<PR_NUMBER>
 
 ---
 
-### Step 7 — Publish
+### Step 8 — Publish
 
 **Same-repo PR (`IS_FORK=false`):**
 
@@ -297,15 +383,15 @@ Output to user:
 
 ---
 
-### Step 8 — Verification Report
+### Step 9 — Verification Report
 
 For each issue in the original summary table, verify the fix exists in actual code:
 
 1. Read the relevant file (Read tool)
 2. Grep for the original problematic pattern to confirm it is gone
 3. Confirm the corrected code is in place
 
-Post the verification report as a PR comment AND output it in the conversation:
+Post the verification report as a PR comment AND output it in the conversation. The report now includes a **Triage 决策** section before the fix table:
 
 ```bash
 gh pr comment <PR_NUMBER> --body "$(cat <<'EOF'
@@ -315,12 +401,25 @@ gh pr comment <PR_NUMBER> --body "$(cat <<'EOF'
 **原始 PR:** #<PR_NUMBER>
 **修复方式:** 直接推送到 `<head_branch>`
 
+### Triage 决策
+
+| # | 严重级别 | 原始问题 | 判定 | 理由 |
+|---|---------|---------|------|------|
+| 2 | 🟠 HIGH | <问题描述> | ⏭️ 驳回 | <驳回理由，引用具体代码或项目约定> |
+| 3 | 🟡 MEDIUM | <问题描述> | 🔄 替代方案 | <为什么原建议不适用，替代方案是什么> |
+
+> 仅列出被驳回（DISMISSED）或使用替代方案（FIX_ALT）的问题。采纳原建议（FIX）的问题不在此表中。
+> 若所有问题均采纳原建议，省略此区块。
+
+### 修复结果
+
 | # | 严重级别 | 文件 | 问题 | 修复方式 | 状态 |
 |---|---------|------|------|---------|------|
 | 1 | 🔴 CRITICAL | `file.ts:N` | <原始问题> | <修复措施> | ✅ 已修复 |
-| 2 | 🟠 HIGH     | `file.ts:N` | <原始问题> | <修复措施> | ✅ 已修复 |
+| 2 | 🟠 HIGH     | `file.ts:N` | <原始问题> | <修复措施> | ✅ 已修复（替代方案） |
+| 3 | 🟡 MEDIUM   | `file.ts:N` | <原始问题> | — | ⏭️ 驳回 |
 
-**总结：** ✅ 已修复 N 个 | ❌ 未能修复 N 个
+**总结：** ✅ 已修复 N 个 | 🔄 替代方案 N 个 | ⏭️ 驳回 N 个 | ❌ 未能修复 N 个
 
 > 🔵 LOW 级别问题已跳过（不阻塞合并，修复优先级低）。
 EOF
@@ -331,7 +430,7 @@ After posting, output the same verification table in the conversation for immedi
 
 ---
 
-### Step 9 — Cleanup
+### Step 10 — Cleanup
 
 Remove the worktree. All paths use `--detach` so no local branches were created.
 
@@ -348,24 +447,32 @@ git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
 - **Always reference original PR** — every commit and PR body must include `Review follow-up for #<PR_NUMBER>`
 - **No issue creation** — this skill skips the issue-association step in pr skill
 - **Fix, don't workaround** — no `// @ts-ignore`, no lint suppression; address the root cause
+- **Triage before fix** — never blindly apply review suggestions; independently verify each issue and evaluate the proposed fix
+- **Fix scope = review scope** — alternative fixes must target the same files and same problem; do not expand scope or refactor beyond what the issue requires
+- **CRITICAL cannot be auto-dismissed** — in automation mode, dismissing a CRITICAL issue requires human escalation
 
 ---
 
 ## Quick Reference
 
 ```
-0. Require pr-review report in current session — abort if not found
-1. Parse summary table → ordered issue list
-2. Pre-flight: fetch PR info (state, isCrossRepository, maintainerCanModify, forkOwner)
-   → ABORT: state=MERGED
-3. Create worktree at /tmp/aionui-pr-<PR_NUMBER> (all paths use --detach):
-   → same-repo:        git fetch + git worktree add --detach
-   → fork+canModify:   git worktree add --detach + gh pr checkout <PR_NUMBER>
-   → fork+fallback:    git worktree add --detach + merge fork head
-4. Fix issues CRITICAL→HIGH→MEDIUM only (skip LOW); bunx tsc --noEmit after each file batch
-5. bun run lint:fix && bun run format && bunx tsc --noEmit && bun run test (in worktree)
-6. Commit: fix(<scope>): address review issues from PR #N
-7. Push from worktree (same-repo / fork+canModify / fork+fallback)
-8. Verify → post as gh pr comment PR_NUMBER + output in conversation
-9. Cleanup: git worktree remove + git branch -D (worktree and local branches)
+ 0. Require pr-review report in current session — abort if not found
+ 1. Parse summary table → ordered issue list
+ 2. Pre-flight: fetch PR info (state, isCrossRepository, maintainerCanModify, forkOwner)
+    → ABORT: state=MERGED
+ 3. Create worktree at /tmp/aionui-pr-<PR_NUMBER> (all paths use --detach):
+    → same-repo:        git fetch + git worktree add --detach
+    → fork+canModify:   git worktree add --detach + gh pr checkout <PR_NUMBER>
+    → fork+fallback:    git worktree add --detach + merge fork head
+ 4. Triage & Validate: verify each issue independently (3-layer check)
+    → Layer 1: is issue real? → DISMISSED if false positive
+    → Layer 2: is suggested fix reasonable? → FIX if yes
+    → Layer 3: is there a better fix? → FIX_ALT if yes
+    → CRITICAL cannot be auto-dismissed in automation mode (escalate to human)
+ 5. Fix issues with verdict FIX/FIX_ALT, CRITICAL→HIGH→MEDIUM; tsc after each batch
+ 6. bun run lint:fix && bun run format && bunx tsc --noEmit && bun run test (in worktree)
+ 7. Commit: fix(<scope>): address review issues from PR #N
+ 8. Push from worktree (same-repo / fork+canModify / fork+fallback)
+ 9. Verify → post Triage 决策 + 修复结果 as gh pr comment + output in conversation
+10. Cleanup: git worktree remove + git branch -D (worktree and local branches)
 ```
PATCH

echo "Gold patch applied."
