#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'Sequential 4-phase workflow for GitHub issues' .github/agents/pr.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/README-AI.md b/.github/README-AI.md
index 4f6b1f21a8a7..c703358dfade 100644
--- a/.github/README-AI.md
+++ b/.github/README-AI.md
@@ -5,7 +5,7 @@ This folder contains instructions and configurations for AI coding assistants wo
 ## Available Agents
 
 ### PR Agent
-The PR agent is a unified 5-phase workflow for investigating issues and reviewing/working on PRs. It handles everything from context gathering through test verification, fix exploration, and creating PRs or review reports.
+The PR agent is a unified 4-phase workflow for investigating issues and reviewing/working on PRs. It handles everything from context gathering through test verification, fix exploration, and creating PRs or review reports.
 
 ### Sandbox Agent
 The sandbox agent is your general-purpose tool for working with the .NET MAUI Sandbox app. Use it for manual testing, PR validation, issue reproduction, and experimentation with MAUI features.
@@ -148,13 +148,12 @@ Automated testing specialist for the .NET MAUI test suite:
 
 ### PR Agent
 
-Unified 5-phase workflow for issue investigation and PR work:
+Unified 4-phase workflow for issue investigation and PR work:
 
 1. **Pre-Flight** - Context gathering from issues/PRs
-2. **Tests** - Create or verify reproduction tests exist
-3. **Gate** - Verify tests catch the issue (mandatory checkpoint)
-4. **Fix** - Explore fix alternatives using `try-fix` skill, compare approaches
-5. **Report** - Create PR or write review report
+2. **Gate** - Verify tests exist and catch the issue (mandatory checkpoint)
+3. **Fix** - Explore fix alternatives using `try-fix` skill, compare approaches
+4. **Report** - Create PR or write review report
 
 ### When Agents Pause
 
@@ -201,8 +200,8 @@ Agents work with **time budgets as estimates for planning**, not hard deadlines:
 ## File Structure
 
 ### Agent Definitions
-- **`agents/pr.md`** - PR workflow phases 1-3 (Pre-Flight, Tests, Gate)
-- **`agents/pr/post-gate.md`** - PR workflow phases 4-5 (Fix, Report)
+- **`agents/pr.md`** - PR workflow phases 1-2 (Pre-Flight, Gate)
+- **`agents/pr/post-gate.md`** - PR workflow phases 3-4 (Fix, Report)
 - **`agents/sandbox-agent.md`** - Sandbox agent for testing and experimentation
 - **`agents/write-tests-agent.md`** - Test writing agent (dispatches to skills like write-ui-tests)
 
@@ -210,8 +209,8 @@ Agents work with **time budgets as estimates for planning**, not hard deadlines:
 
 Agent files in the `.github/agents/` directory:
 
-- **`agents/pr.md`** - PR workflow phases 1-3 (Pre-Flight, Tests, Gate)
-- **`agents/pr/post-gate.md`** - PR workflow phases 4-5 (Fix, Report)
+- **`agents/pr.md`** - PR workflow phases 1-2 (Pre-Flight, Gate)
+- **`agents/pr/post-gate.md`** - PR workflow phases 3-4 (Fix, Report)
 - **`agents/sandbox-agent.md`** - Sandbox app testing and experimentation
 - **`agents/write-tests-agent.md`** - Test writing (invokes skills like write-ui-tests)
 
@@ -256,7 +255,7 @@ Reusable skills in `.github/skills/` that agents can invoke:
 ### Recent Improvements (January 2026)
 
 **PR Agent Consolidation:**
-1. **Unified PR Agent** - Replaced separate `issue-resolver` and `pr-reviewer` agents with single 5-phase `pr` agent
+1. **Unified PR Agent** - Replaced separate `issue-resolver` and `pr-reviewer` agents with single 4-phase `pr` agent
 2. **try-fix Skill** - New skill for exploring independent fix alternatives with empirical testing
 3. **Skills Integration** - Added `verify-tests-fail-without-fix` and `write-ui-tests` skills for reusable test workflows
 4. **Agent/Skills Guidelines** - New instruction files for authoring agents and skills
@@ -384,4 +383,4 @@ For issues or questions about the AI agent instructions:
 
 **Last Updated**: 2026-01-07
 
-**Note**: These instructions are actively being refined based on real-world usage. PR agent consolidation completed January 2026 (unified 5-phase workflow with try-fix skill). Feedback and improvements are welcome!
+**Note**: These instructions are actively being refined based on real-world usage. PR agent consolidation completed January 2026 (unified 4-phase workflow with try-fix skill). Feedback and improvements are welcome!
diff --git a/.github/agents/pr.md b/.github/agents/pr.md
index ecd6bc1d62e0..d5c55dbc80de 100644
--- a/.github/agents/pr.md
+++ b/.github/agents/pr.md
@@ -1,6 +1,6 @@
 ---
 name: pr
-description: Sequential 5-phase workflow for GitHub issues - Pre-Flight, Tests, Gate, Fix, Report. Phases MUST complete in order. State tracked in CustomAgentLogsTmp/PRState/
+description: Sequential 4-phase workflow for GitHub issues - Pre-Flight, Gate, Fix, Report. Phases MUST complete in order. State tracked in CustomAgentLogsTmp/PRState/
 ---
 
 # .NET MAUI Pull Request Agent
@@ -25,17 +25,17 @@ You are an end-to-end agent that takes a GitHub issue from investigation through
 
 ## Workflow Overview
 
-This file covers **Phases 1-3** (Pre-Flight → Tests → Gate).
+This file covers **Phases 1-2** (Pre-Flight → Gate).
 
-After Gate passes, read `.github/agents/pr/post-gate.md` for **Phases 4-5**.
+After Gate passes, read `.github/agents/pr/post-gate.md` for **Phases 3-4**.
 
 ```
 ┌─────────────────────────────────────────┐     ┌─────────────────────────────────────────────┐
 │  THIS FILE: pr.md                       │     │  pr/post-gate.md                            │
 │                                         │     │                                             │
-│  1. Pre-Flight  →  2. Tests  →  3. Gate │ ──► │  4. Fix  →  5. Report                       │
-│                          ⛔              │     │                                             │
-│                     MUST PASS            │     │  (Only read after Gate ✅ PASSED)           │
+│  1. Pre-Flight  →  2. Gate              │ ──► │  3. Fix  →  4. Report                       │
+│                       ⛔                 │     │                                             │
+│                  MUST PASS              │     │  (Only read after Gate ✅ PASSED)           │
 └─────────────────────────────────────────┘     └─────────────────────────────────────────────┘
 ```
 
@@ -57,7 +57,7 @@ After Gate passes, read `.github/agents/pr/post-gate.md` for **Phases 4-5**.
 - ❌ Never continue after environment blocker - STOP and ask user
 - ❌ Never mark phase ✅ with [PENDING] fields remaining
 
-Phase 4 uses a 5-model exploration workflow. See `post-gate.md` for detailed instructions after Gate passes.
+Phase 3 uses a 5-model exploration workflow. See `post-gate.md` for detailed instructions after Gate passes.
 
 ---
 
@@ -71,11 +71,11 @@ Phase 4 uses a 5-model exploration workflow. See `post-gate.md` for detailed ins
 
 | ❌ Do NOT | Why | When to do it |
 |-----------|-----|---------------|
-| Research git history | That's root cause analysis | Phase 4: 🔧 Fix |
-| Look at implementation code | That's understanding the bug | Phase 4: 🔧 Fix |
-| Design or implement fixes | That's solution design | Phase 4: 🔧 Fix |
-| Form opinions on correct approach | That's analysis | Phase 4: 🔧 Fix |
-| Run tests | That's verification | Phase 3: 🚦 Gate |
+| Research git history | That's root cause analysis | Phase 3: 🔧 Fix |
+| Look at implementation code | That's understanding the bug | Phase 3: 🔧 Fix |
+| Design or implement fixes | That's solution design | Phase 3: 🔧 Fix |
+| Form opinions on correct approach | That's analysis | Phase 3: 🔧 Fix |
+| Run tests | That's verification | Phase 2: 🚦 Gate |
 
 ### ✅ What TO Do in Pre-Flight
 
@@ -122,7 +122,6 @@ fi
 | Phase | Status |
 |-------|--------|
 | Pre-Flight | ▶️ IN PROGRESS |
-| 🧪 Tests | ⏳ PENDING |
 | 🚦 Gate | ⏳ PENDING |
 | 🔧 Fix | ⏳ PENDING |
 | 📋 Report | ⏳ PENDING |
@@ -174,21 +173,6 @@ fi
 
 </details>
 
-<details>
-<summary><strong>🧪 Tests</strong></summary>
-
-**Status**: ⏳ PENDING
-
-- [ ] PR includes UI tests
-- [ ] Tests reproduce the issue
-- [ ] Tests follow naming convention (`IssueXXXXX`)
-
-**Test Files:**
-- HostApp: [PENDING]
-- NUnit: [PENDING]
-
-</details>
-
 <details>
 <summary><strong>🚦 Gate - Test Verification</strong></summary>
 
@@ -209,7 +193,7 @@ fi
 |---|--------|----------|-------------|---------------|-------|
 | PR | PR #XXXXX | [PR's approach - from Pre-Flight] | ⏳ PENDING (Gate) | [files] | Original PR - validated by Gate |
 
-**Note:** try-fix candidates (1, 2, 3...) are added during Phase 4. PR's fix is reference only.
+**Note:** try-fix candidates (1, 2, 3...) are added during Phase 3. PR's fix is reference only.
 
 **Exhausted:** No
 **Selected Fix:** [PENDING]
@@ -218,7 +202,7 @@ fi
 
 ---
 
-**Next Step:** After Gate passes, read `.github/agents/pr/post-gate.md` and continue with phases 4-5.
+**Next Step:** After Gate passes, read `.github/agents/pr/post-gate.md` and continue with phases 3-4.
 ```
 
 This file:
@@ -226,7 +210,7 @@ This file:
 - Tracks progress if interrupted
 - Must exist before you start gathering context
 - **Always include when saving changes** (to `CustomAgentLogsTmp/PRState/`)
-- **Phases 4-5 sections are added AFTER Gate passes** (see `pr/post-gate.md`)
+- **Phases 3-4 sections are added AFTER Gate passes** (see `pr/post-gate.md`)
 
 **Then gather context and update the file as you go.**
 
@@ -330,7 +314,7 @@ The test result will be updated to `✅ PASS (Gate)` after Gate passes.
 1. Change Pre-Flight status from `▶️ IN PROGRESS` to `✅ COMPLETE`
 2. Fill in issue summary, platforms affected, regression info
 3. Add edge cases and any disagreements (if PR exists)
-4. Change 🧪 Tests status to `▶️ IN PROGRESS`
+4. Change 🚦 Gate status to `▶️ IN PROGRESS`
 
 **Before marking ✅ COMPLETE, verify state file contains:**
 - [ ] Issue summary filled (not [PENDING])
@@ -342,13 +326,15 @@ The test result will be updated to `✅ PASS (Gate)` after Gate passes.
 
 ---
 
-## 🧪 TESTS: Create/Verify Reproduction Tests (Phase 2)
+## 🚦 GATE: Verify Tests Catch the Issue (Phase 2)
 
-> **SCOPE**: Ensure tests exist that reproduce the issue. **Tests must be verified to FAIL before this phase is complete.**
+> **SCOPE**: Verify tests exist and correctly detect the fix (for PRs) or reproduce the bug (for issues).
+
+**⛔ This phase MUST pass before continuing. If it fails, stop and fix the tests.**
 
 **⚠️ Gate Check:** Pre-Flight must be `✅ COMPLETE` before starting this phase.
 
-### Step 1: Check if Tests Already Exist
+### Step 1: Check if Tests Exist
 
 **If PR exists:**
 ```bash
@@ -361,90 +347,27 @@ gh pr view XXXXX --json files --jq '.files[].path' | grep -E "TestCases\.(HostAp
 find src/Controls/tests -name "*XXXXX*" -type f 2>/dev/null
 ```
 
-**If tests exist** → Verify they follow conventions and reproduce the bug.
-
-**If NO tests exist** → Create them using the `write-ui-tests` skill.
-
-### Step 2: Create Tests (if needed)
-
-Invoke the `write-ui-tests` skill which will:
-1. Read `.github/instructions/uitests.instructions.md` for conventions
-2. Create HostApp page: `src/Controls/tests/TestCases.HostApp/Issues/IssueXXXXX.cs`
-3. Create NUnit test: `src/Controls/tests/TestCases.Shared.Tests/Tests/Issues/IssueXXXXX.cs`
-4. **Verify tests FAIL** (reproduce the bug) - iterating until they do
-
-### Step 3: Verify Tests Compile
-
-```bash
-dotnet build src/Controls/tests/TestCases.HostApp/Controls.TestCases.HostApp.csproj -c Debug -f net10.0-android --no-restore -v q
-dotnet build src/Controls/tests/TestCases.Shared.Tests/Controls.TestCases.Shared.Tests.csproj -c Debug --no-restore -v q
-```
-
-### Step 4: Verify Tests Reproduce the Bug (if not done by write-ui-tests skill)
-
-```bash
-pwsh .github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1 -Platform ios -TestFilter "IssueXXXXX"
-```
+**If tests exist** → Proceed to verification.
 
-The script auto-detects mode based on git diff. If only test files changed, it verifies tests FAIL.
+**If NO tests exist** → Let the user know that tests are missing. They can use the `write-tests-agent` to help create them.
 
-**Tests must FAIL.** If they pass, the test is wrong - fix it and rerun.
-
-### Complete 🧪 Tests
-
-**🚨 MANDATORY: Update state file**
-
-**Update state file**:
-1. Check off completed items in the checklist
-2. Fill in test file paths
-3. Note: "Tests verified to FAIL (bug reproduced)"
-4. Change 🧪 Tests status to `✅ COMPLETE`
-5. Change 🚦 Gate status to `▶️ IN PROGRESS`
-
-**Before marking ✅ COMPLETE, verify state file contains:**
-- [ ] Test file paths documented
-- [ ] "Tests verified to FAIL" note added
-- [ ] Test category identified
-- [ ] State file saved
-
----
-
-## 🚦 GATE: Verify Tests Catch the Issue (Phase 3)
-
-> **SCOPE**: Verify tests correctly detect the fix (for PRs) or confirm tests were verified (for issues).
-
-**⛔ This phase MUST pass before continuing. If it fails, stop and fix the tests.**
-
-**⚠️ Gate Check:** 🧪 Tests must be `✅ COMPLETE` before starting this phase.
-
-### Gate Depends on Starting Point
-
-**If starting from an Issue (no fix yet):**
-Tests were already verified to FAIL in Phase 2. Gate is a confirmation step:
-- Confirm tests were run and failed
-- Mark Gate as passed
-- Proceed to Phase 4 (Fix) to implement fix
-
-**If starting from a PR (fix exists):**
-Use full verification mode - tests should FAIL without fix, PASS with fix.
-
-### Platform Selection for Gate
+### Step 2: Select Platform
 
 **🚨 CRITICAL: Choose a platform that is BOTH affected by the bug AND available on the current host.**
 
-**Step 1: Identify affected platforms** from Pre-Flight:
+**Identify affected platforms** from Pre-Flight:
 - Check the "Platforms Affected" checkboxes in the state file
 - Check issue labels (e.g., `platform/iOS`, `platform/Android`)
 - Check which platform-specific files the PR modifies
 
-**Step 2: Match to available platforms on current host:**
+**Match to available platforms on current host:**
 
 | Host OS | Available Platforms |
 |---------|---------------------|
 | Windows | Android, Windows |
 | macOS | Android, iOS, MacCatalyst |
 
-**Step 3: Select the best match:**
+**Select the best match:**
 1. Pick a platform that IS affected by the bug
 2. That IS available on the current host
 3. Prefer the platform most directly impacted by the PR's code changes
@@ -457,6 +380,8 @@ Use full verification mode - tests should FAIL without fix, PASS with fix.
 
 **⚠️ Do NOT test on a platform that isn't affected by the bug** - the test will pass regardless of whether the fix works.
 
+### Step 3: Run Verification
+
 **🚨 MUST invoke as a task agent** to prevent command substitution:
 
 ```markdown
@@ -487,7 +412,7 @@ See `.github/skills/verify-tests-fail-without-fix/SKILL.md` for full skill docum
 
 ### If Tests Don't Behave as Expected
 
-**If tests PASS without fix** → Tests don't catch the bug. Go back to Phase 2, invoke `write-ui-tests` skill again to fix the tests.
+**If tests PASS without fix** → Tests don't catch the bug. Let the user know the tests need to be fixed. They can use the `write-tests-agent` for help.
 
 ### Complete 🚦 Gate
 
@@ -496,7 +421,7 @@ See `.github/skills/verify-tests-fail-without-fix/SKILL.md` for full skill docum
 **Update state file**:
 1. Fill in **Result**: `PASSED ✅`
 2. Change 🚦 Gate status to `✅ PASSED`
-3. Proceed to Phase 4
+3. Proceed to Phase 3
 
 **Before marking ✅ PASSED, verify state file contains:**
 - [ ] Result shows PASSED ✅ or FAILED ❌
@@ -508,7 +433,7 @@ See `.github/skills/verify-tests-fail-without-fix/SKILL.md` for full skill docum
 
 ## ⛔ STOP HERE
 
-**If Gate is `✅ PASSED`** → Read `.github/agents/pr/post-gate.md` to continue with phases 4-5.
+**If Gate is `✅ PASSED`** → Read `.github/agents/pr/post-gate.md` to continue with phases 3-4.
 
 **If Gate `❌ FAILED`** → Stop. Request changes from the PR author to fix the tests.
 
@@ -516,12 +441,12 @@ See `.github/skills/verify-tests-fail-without-fix/SKILL.md` for full skill docum
 
 ## Common Pre-Gate Mistakes
 
-- ❌ **Researching root cause during Pre-Flight** - Just document what the issue says, save analysis for Phase 4
+- ❌ **Researching root cause during Pre-Flight** - Just document what the issue says, save analysis for Phase 3
 - ❌ **Looking at implementation code during Pre-Flight** - Just gather issue/PR context
-- ❌ **Forming opinions on the fix during Pre-Flight** - That's Phase 4
-- ❌ **Running tests during Pre-Flight** - That's Phase 3
+- ❌ **Forming opinions on the fix during Pre-Flight** - That's Phase 3
+- ❌ **Running tests during Pre-Flight** - That's Phase 2 (Gate)
 - ❌ **Not creating state file first** - ALWAYS create state file before gathering context
-- ❌ **Skipping to Phase 4** - Gate MUST pass first
+- ❌ **Skipping to Phase 3** - Gate MUST pass first
 
 ## Common Gate Mistakes
 
diff --git a/.github/agents/pr/PLAN-TEMPLATE.md b/.github/agents/pr/PLAN-TEMPLATE.md
index a1d1e1912193..1ee1bbc54b65 100644
--- a/.github/agents/pr/PLAN-TEMPLATE.md
+++ b/.github/agents/pr/PLAN-TEMPLATE.md
@@ -1,10 +1,10 @@
 # PR Review Plan Template
 
-**Reusable checklist** for the 5-phase PR Agent workflow.
+**Reusable checklist** for the 4-phase PR Agent workflow.
 
 **Source documents:**
-- `.github/agents/pr.md` - Phases 1-3 (Pre-Flight, Tests, Gate)
-- `.github/agents/pr/post-gate.md` - Phases 4-5 (Fix, Report)
+- `.github/agents/pr.md` - Phases 1-2 (Pre-Flight, Gate)
+- `.github/agents/pr/post-gate.md` - Phases 3-4 (Fix, Report)
 - `.github/agents/pr/SHARED-RULES.md` - Critical rules (blockers, git, templates)
 
 ---
@@ -36,18 +36,10 @@ See `SHARED-RULES.md` for complete details. Key points:
 
 **Boundaries:** No code analysis, no fix opinions, no test running
 
-### Phase 2: Tests
-- [ ] Check if PR includes UI tests
-- [ ] Verify tests follow `IssueXXXXX` naming convention
-- [ ] If tests exist: Verify they compile
-- [ ] If tests missing: Invoke `write-ui-tests` skill
-- [ ] Document test files in state file
-- [ ] Update state file: Tests → ✅ COMPLETE
-- [ ] Save state file
-
-### Phase 3: Gate ⛔
+### Phase 2: Gate ⛔
 **🚨 Cannot continue if Gate fails**
 
+- [ ] Check if tests exist (if not, let the user know and suggest using `write-tests-agent`)
 - [ ] Select platform (must be affected AND available on host)
 - [ ] Invoke via **task agent** (NOT inline):
   ```
@@ -60,7 +52,7 @@ See `SHARED-RULES.md` for complete details. Key points:
 - [ ] Update state file: Gate → ✅ PASSED
 - [ ] Save state file
 
-### Phase 4: Fix 🔧
+### Phase 3: Fix 🔧
 *(Only if Gate ✅ PASSED)*
 
 **Round 1: Run try-fix with each model (SEQUENTIAL)**
@@ -86,12 +78,20 @@ See `SHARED-RULES.md` for complete details. Key points:
 - [ ] Update state file: Fix → ✅ COMPLETE
 - [ ] Save state file
 
-### Phase 5: Report 📋
-*(Only if Phases 1-4 complete)*
+### Phase 4: Report 📋
+*(Only if Phases 1-3 complete)*
 
 - [ ] Run `pr-finalize` skill
 - [ ] Generate review: root cause, candidates, recommendation
-- [ ] Post via `ai-summary-comment` skill
+- [ ] Post AI Summary comment (PR phases + try-fix):
+  ```bash
+  pwsh .github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1 -PRNumber XXXXX -SkipValidation
+  pwsh .github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1 -IssueNumber XXXXX
+  ```
+- [ ] Post PR Finalization comment (separate):
+  ```bash
+  pwsh .github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 -PRNumber XXXXX -SummaryFile CustomAgentLogsTmp/PRState/pr-XXXXX.md
+  ```
 - [ ] Update state file: Report → ✅ COMPLETE
 - [ ] Save final state file
 
@@ -102,7 +102,6 @@ See `SHARED-RULES.md` for complete details. Key points:
 | Phase | Key Action | Blocker Response |
 |-------|------------|------------------|
 | Pre-Flight | Create state file | N/A |
-| Tests | Verify/create tests | N/A |
 | Gate | Task agent → verify script | ⛔ STOP, report, ask |
 | Fix | Multi-model try-fix | ⛔ STOP, report, ask |
 | Report | Post via skill | ⛔ STOP, report, ask |
diff --git a/.github/agents/pr/post-gate.md b/.github/agents/pr/post-gate.md
index 8878f1b6928e..16c5fc8e3272 100644
--- a/.github/agents/pr/post-gate.md
+++ b/.github/agents/pr/post-gate.md
@@ -1,8 +1,8 @@
-# PR Agent: Post-Gate Phases (4-5)
+# PR Agent: Post-Gate Phases (3-4)
 
 **⚠️ PREREQUISITE: Only read this file after 🚦 Gate shows `✅ PASSED` in your state file.**
 
-If Gate is not passed, go back to `.github/agents/pr.md` and complete phases 1-3 first.
+If Gate is not passed, go back to `.github/agents/pr.md` and complete phases 1-2 first.
 
 ---
 
@@ -10,8 +10,8 @@ If Gate is not passed, go back to `.github/agents/pr.md` and complete phases 1-3
 
 | Phase | Name | What Happens |
 |-------|------|--------------|
-| 4 | **Fix** | Invoke `try-fix` skill repeatedly to explore independent alternatives, then compare with PR's fix |
-| 5 | **Report** | Deliver result (approve PR, request changes, or create new PR) |
+| 3 | **Fix** | Invoke `try-fix` skill repeatedly to explore independent alternatives, then compare with PR's fix |
+| 4 | **Report** | Deliver result (approve PR, request changes, or create new PR) |
 
 ---
 
@@ -26,7 +26,7 @@ If try-fix cannot run due to environment issues, **STOP and ask the user**. Do N
 
 ---
 
-## 🔧 FIX: Explore and Select Fix (Phase 4)
+## 🔧 FIX: Explore and Select Fix (Phase 3)
 
 > **SCOPE**: Explore independent fix alternatives using `try-fix` skill, compare with PR's fix, select the best approach.
 
@@ -193,11 +193,11 @@ Update the state file:
 
 ---
 
-## 📋 REPORT: Final Report (Phase 5)
+## 📋 REPORT: Final Report (Phase 4)
 
 > **SCOPE**: Deliver the final result - either a PR review or a new PR.
 
-**⚠️ Gate Check:** Verify ALL phases 1-4 are `✅ COMPLETE` or `✅ PASSED` before proceeding.
+**⚠️ Gate Check:** Verify ALL phases 1-3 are `✅ COMPLETE` or `✅ PASSED` before proceeding.
 
 ### Finalize Title and Description
 
@@ -290,7 +290,6 @@ Update all phase statuses to complete.
 - ❌ **Re-testing the PR's fix in try-fix** - Gate already validated it; try-fix tests YOUR ideas
 - ❌ **Skipping models in Round 1** - All 5 models must run try-fix before cross-pollination
 - ❌ **Running try-fix in parallel** - SEQUENTIAL ONLY - they modify same files and use same device
-- ❌ **Stopping before cross-pollination** - Must share results and check for new ideas
 - ❌ **Using explore/glob instead of invoking models** - Cross-pollination requires ACTUAL task agent invocations with each model, not code searches
 - ❌ **Assuming "comprehensive coverage" = exhausted** - Only exhausted when all 5 models explicitly say "NO NEW IDEAS"
 - ❌ **Not recording cross-pollination responses** - State file must have table showing each model's Round 2 response
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index d258c6022fd8..5c9f96eba10f 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -196,7 +196,7 @@ The repository includes specialized custom agents and reusable skills for specif
 
 ### Available Custom Agents
 
-1. **pr** - Sequential 5-phase workflow for reviewing and working on PRs
+1. **pr** - Sequential 4-phase workflow for reviewing and working on PRs
    - **Use when**: A PR already exists and needs review or work, OR an issue needs a fix
    - **Capabilities**: PR review, test verification, fix exploration, alternative comparison
    - **Trigger phrases**: "review PR #XXXXX", "work on PR #XXXXX", "fix issue #XXXXX", "continue PR #XXXXX"
diff --git a/.github/scripts/Review-PR.ps1 b/.github/scripts/Review-PR.ps1
index 1cdfc8c797c5..3df37e9216d2 100644
--- a/.github/scripts/Review-PR.ps1
+++ b/.github/scripts/Review-PR.ps1
@@ -3,13 +3,12 @@
     Runs a PR review using Copilot CLI and the PR Agent workflow.
 
 .DESCRIPTION
-    This script invokes Copilot CLI to perform a comprehensive 5-phase PR review:
+    This script invokes Copilot CLI to perform a comprehensive 4-phase PR review:
     
     Phase 1: Pre-Flight - Context gathering
-    Phase 2: Tests - Verify test existence
-    Phase 3: Gate - Verify tests catch the bug
-    Phase 4: Fix - Multi-model exploration of alternatives
-    Phase 5: Report - Final recommendation
+    Phase 2: Gate - Verify tests catch the bug
+    Phase 3: Fix - Multi-model exploration of alternatives
+    Phase 4: Report - Final recommendation
     
     The script:
     - Validates prerequisites (gh CLI, PR exists)
@@ -248,17 +247,17 @@ $platformInstruction
 - If you think you need to switch branches or push changes, you are WRONG - ask the user instead
 
 **Instructions:**
-1. Read the plan template at ``$planTemplatePath`` for the 5-phase workflow
-2. Read ``.github/agents/pr.md`` for Phases 1-3 instructions
+1. Read the plan template at ``$planTemplatePath`` for the 4-phase workflow
+2. Read ``.github/agents/pr.md`` for Phases 1-2 instructions
 3. Follow ALL critical rules, especially:
    - STOP on environment blockers and ask before continuing
    - Use task agent for Gate verification
-   - Run multi-model try-fix in Phase 4
+   - Run multi-model try-fix in Phase 3
 
 **Start with Phase 1: Pre-Flight**
 - Create state file: CustomAgentLogsTmp/PRState/pr-$PRNumber.md
 - Gather context from PR #$PRNumber
-- Proceed through all 5 phases
+- Proceed through all 4 phases
 
 Begin the review now.
 "@
diff --git a/.github/skills/ai-summary-comment/IMPROVEMENTS.md b/.github/skills/ai-summary-comment/IMPROVEMENTS.md
index 86094bdd752c..2de8dc008fe4 100644
--- a/.github/skills/ai-summary-comment/IMPROVEMENTS.md
+++ b/.github/skills/ai-summary-comment/IMPROVEMENTS.md
@@ -31,9 +31,8 @@ $preFlightContent = Get-SectionByPattern -Sections $allSections -Patterns @(
 
 **Example debug output:**
 ```
-[DEBUG] Found 7 section(s) in state file
+[DEBUG] Found 6 section(s) in state file
 [DEBUG] Section: '📋 Issue Summary' (803 chars)
-[DEBUG] Section: '🧪 Tests' (539 chars)
 [DEBUG] Section: '🚦 Gate - Test Verification' (488 chars)
 [DEBUG] Section: '🔧 Fix Candidates' (868 chars)
 [DEBUG] Section: '📋 Final Report' (2351 chars)
@@ -51,14 +50,14 @@ $preFlightContent = Get-SectionByPattern -Sections $allSections -Patterns @(
 ```powershell
 # Matches any of these (and more!):
 - "📋 Final Report" ✅
-- "📋 Phase 5: Final Report" ✅
+- "📋 Phase 4: Final Report" ✅
 - "📋 Report - Final Recommendation" ✅
 - Any title containing "📋" and "Report" ✅
 ```
 
 **Pattern examples:**
 - `'📋.*Issue Summary'` matches "📋 Issue Summary", "📋 Pre-Flight Issue Summary", etc.
-- `'🧪.*Tests'` matches "🧪 Tests", "🧪 Phase 2: Tests", etc.
+- `'🚦.*Gate'` matches "🚦 Gate", "🚦 Phase 2: Gate", etc.
 - `'📋.*Report'` matches any title with 📋 and Report in it
 
 ---
@@ -182,17 +181,11 @@ Any title matching `'📋.*Issue Summary'` or `'📋.*Pre-Flight'`:
 - ✅ "📋 Pre-Flight Analysis"
 - ✅ "📋 Context and Issue Summary"
 
-### Tests Phase
-Any title matching `'🧪.*Tests'`:
-- ✅ "🧪 Tests"
-- ✅ "🧪 Phase 2: Tests"
-- ✅ "🧪 Test Verification"
-
 ### Gate Phase
 Any title matching `'🚦.*Gate'`:
 - ✅ "🚦 Gate - Test Verification"
 - ✅ "🚦 Gate"
-- ✅ "🚦 Phase 3: Gate"
+- ✅ "🚦 Phase 2: Gate"
 
 ### Fix Phase
 Any title matching `'🔧.*Fix'`:
@@ -203,7 +196,7 @@ Any title matching `'🔧.*Fix'`:
 ### Report Phase
 Any title matching `'📋.*Report'` or `'Final Report'`:
 - ✅ "📋 Final Report"
-- ✅ "📋 Phase 5: Report"
+- ✅ "📋 Phase 4: Report"
 - ✅ "📋 Report - Final Recommendation"
 - ✅ "Final Report"
 
@@ -217,7 +210,7 @@ Any title matching `'📋.*Report'` or `'Final Report'`:
 
 **Old state files** with exact headers like:
 ```markdown
-<summary><strong>📋 Phase 5: Report — Final Recommendation</strong></summary>
+<summary><strong>📋 Phase 4: Report — Final Recommendation</strong></summary>
 ```
 
 **New state files** with simpler headers like:
@@ -325,7 +318,7 @@ $reportContent = Get-SectionByPattern -Sections $allSections -Patterns @(
 - Use `[regex]::Escape()` if you need literal special chars
 
 **Examples:**
-- `'🧪.*Tests'` - Title must contain both 🧪 and Tests
+- `'🚦.*Gate'` - Title must contain both 🚦 and Gate
 - `'^📋 Report'` - Title must START with "📋 Report"
 - `'Report$'` - Title must END with "Report"
 
@@ -334,7 +327,7 @@ $reportContent = Get-SectionByPattern -Sections $allSections -Patterns @(
 ## Testing
 
 Tested with:
-- ✅ PR #27340 (7 sections extracted successfully)
+- ✅ PR #27340 (6 sections extracted successfully)
 - ✅ Debug mode showing section discovery
 - ✅ Various header formats
 - ✅ Dry run mode
@@ -343,16 +336,14 @@ Tested with:
 
 **Debug output example:**
 ```
-[DEBUG] Found 7 section(s) in state file
+[DEBUG] Found 6 section(s) in state file
 [DEBUG] Section: '📋 Issue Summary' (803 chars)
 [DEBUG] Section: '📁 Files Changed' (0 chars)
 [DEBUG] Section: '💬 PR Discussion Summary' (0 chars)
-[DEBUG] Section: '🧪 Tests' (539 chars)
 [DEBUG] Section: '🚦 Gate - Test Verification' (488 chars)
 [DEBUG] Section: '🔧 Fix Candidates' (868 chars)
 [DEBUG] Section: '📋 Final Report' (2351 chars)
 [DEBUG] Matched '📋 Issue Summary' with pattern '📋.*Issue Summary'
-[DEBUG] Matched '🧪 Tests' with pattern '🧪.*Tests'
 [DEBUG] Matched '🚦 Gate - Test Verification' with pattern '🚦.*Gate'
 [DEBUG] Matched '🔧 Fix Candidates' with pattern '🔧.*Fix'
 [DEBUG] Matched '📋 Final Report' with pattern '📋.*Report'
@@ -451,7 +442,7 @@ Found 1 validation error(s):
 
 ---
 
-### 5. **Relaxed Phase 5 Validation**
+### 5. **Relaxed Phase 4 Validation**
 
 **Before:** Report phase required:
 - Exact "Final Recommendation" text
@@ -505,10 +496,6 @@ Any of these variations will be recognized:
 - `📋 Pre-Flight` ✅
 - `🔍 Pre-Flight` ✅
 
-**Tests:**
-- `🧪 Tests` ✅ (preferred)
-- `📋 Tests` ✅
-
 **Gate:**
 - `🚦 Gate - Test Verification` ✅ (preferred)
 - `🚦 Gate` ✅
@@ -521,9 +508,9 @@ Any of these variations will be recognized:
 
 **Report:**
 - `📋 Final Report` ✅
-- `📋 Phase 5: Final Report` ✅
+- `📋 Phase 4: Final Report` ✅
 - `📋 Report` ✅
-- `Phase 5: Report` ✅
+- `Phase 4: Report` ✅
 - `Final Report` ✅
 
 ---
@@ -533,7 +520,7 @@ Any of these variations will be recognized:
 **No changes needed!** The script is backward compatible. If you have existing state files with the old header format, they'll continue to work.
 
 If you want to use the new flexibility:
-- Just use simpler headers like `📋 Final Report` instead of `📋 Phase 5: Report — Final Recommendation`
+- Just use simpler headers like `📋 Final Report` instead of `📋 Phase 4: Report — Final Recommendation`
 - The script will find it either way
 
 ---
@@ -609,12 +596,12 @@ To support a new header variation, just add it to the array:
 
 ```powershell
 $reportContent = Extract-PhaseContent -StateContent $Content -PhaseTitles @(
-    "📋 Phase 5: Report — Final Recommendation",
-    "📋 Phase 5: Final Report",
-    "📋 Phase 5: Report",
+    "📋 Phase 4: Report — Final Recommendation",
+    "📋 Phase 4: Final Report",
+    "📋 Phase 4: Report",
     "📋 Final Report",
     "📋 Report",
-    "Phase 5: Report",
+    "Phase 4: Report",
     "Final Report",
     "Your New Pattern Here"  # <-- Add here
 ) -Debug:$debugMode
diff --git a/.github/skills/ai-summary-comment/NO-EXTERNAL-REFERENCES-RULE.md b/.github/skills/ai-summary-comment/NO-EXTERNAL-REFERENCES-RULE.md
index a4b8a4dd5c03..84545c9fa546 100644
--- a/.github/skills/ai-summary-comment/NO-EXTERNAL-REFERENCES-RULE.md
+++ b/.github/skills/ai-summary-comment/NO-EXTERNAL-REFERENCES-RULE.md
@@ -100,9 +100,9 @@ When running `pr-finalize` skill, you create TWO outputs:
    - Audience: PR authors, reviewers, community
    - **MUST be self-contained** - no external references
 
-### PR Agent Phase 5 (Report)
+### PR Agent Phase 4 (Report)
 
-When completing Phase 5:
+When completing Phase 4:
 - Include ALL pr-finalize findings inline
 - Show exact code blocks for NOTE block
 - Show exact before/after text for corrections
@@ -168,7 +168,7 @@ Add an **Implementation** subsection after "Description of Change":
 
 ## Checklist for Report Phase
 
-When completing Phase 5, verify:
+When completing Phase 4, verify:
 
 - [ ] All recommendations are inline (no file references)
 - [ ] Code blocks show exact text to add
diff --git a/.github/skills/ai-summary-comment/SKILL.md b/.github/skills/ai-summary-comment/SKILL.md
index 049918f02a17..9073d3bef37c 100644
--- a/.github/skills/ai-summary-comment/SKILL.md
+++ b/.github/skills/ai-summary-comment/SKILL.md
@@ -181,7 +181,7 @@ gh auth status  # Verify authentication before running
 ## Comment Format
 
 Comments are formatted with:
-- **Phase badge** (🔍 Pre-Flight, 🧪 Tests, 🚦 Gate, 🔧 Fix, 📋 Report)
+- **Phase badge** (🔍 Pre-Flight, 🚦 Gate, 🔧 Fix, 📋 Report)
 - **Status indicator** (✅ Completed, ⚠️ Issues Found)
 - **Expandable review sessions** (each session is a collapsible section)
 - **What's Next** (what phase happens next)
@@ -209,7 +209,7 @@ When the same PR is reviewed multiple times (e.g., after new commits), the scrip
 - Test coverage includes iOS device test
 
 ### Next Steps
-→ **Phase 2: Tests** - Analyzing test files and coverage
+→ **Phase 2: Gate** - Verifying tests catch the bug
 
 ---
 *Posted by PR Agent @ 2026-01-17 14:23:45 UTC*
diff --git a/.github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1 b/.github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1
index 82c8673c1b8e..46388f0a320f 100644
--- a/.github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1
+++ b/.github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1
@@ -13,7 +13,7 @@
     Format:
     ## 🤖 AI Summary — ✅ APPROVE
     <details><summary>📊 Expand Full Review</summary>
-      Status table + all 5 phases as nested details
+      Status table + all 4 phases as nested details
     </details>
 
 .PARAMETER PRNumber
@@ -192,11 +192,6 @@ function Test-PhaseContentComplete {
                 $validationWarnings += "Pre-Flight missing 'Platforms Affected' section (non-critical)"
             }
         }
-        "Tests" {
-            if ($PhaseContent -notmatch '(HostApp:|Test Files:)') {
-                $validationWarnings += "Tests phase missing test file paths (non-critical)"
-            }
-        }
         "Gate" {
             if ($PhaseContent -notmatch 'Result:') {
                 $validationWarnings += "Gate phase missing 'Result' field (non-critical)"
@@ -255,7 +250,6 @@ if ($Content -match '##\s+✅\s+Final Recommendation:\s+APPROVE') {
 # Extract phase statuses from state file
 $phaseStatuses = @{
     "Pre-Flight" = "⏳ PENDING"
-    "Tests" = "⏳ PENDING"
     "Gate" = "⏳ PENDING"
     "Fix" = "⏳ PENDING"
     "Report" = "⏳ PENDING"
@@ -351,11 +345,6 @@ $preFlightContent = Get-SectionByPattern -Sections $allSections -Patterns @(
     '🔍.*Pre-Flight'
 ) -Debug:$debugMode
 
-$testsContent = Get-SectionByPattern -Sections $allSections -Patterns @(
-    '🧪.*Tests',
-    '📋.*Tests'
-) -Debug:$debugMode
-
 $gateContent = Get-SectionByPattern -Sections $allSections -Patterns @(
     '🚦.*Gate',
     '📋.*Gate'
@@ -368,7 +357,7 @@ $fixContent = Get-SectionByPattern -Sections $allSections -Patterns @(
 
 $reportContent = Get-SectionByPattern -Sections $allSections -Patterns @(
     '📋.*Report',
-    'Phase 5.*Report',
+    'Phase 4.*Report',
     'Final Report'
 ) -Debug:$debugMode
 
@@ -584,9 +573,6 @@ if ($existingComment) {
     $preFlightMatch = Extract-PhaseFromComment -CommentBody $existingComment.body -Emoji "🔍" -PhaseName "Pre-Flight"
     if ($preFlightMatch) { $existingPreFlightSessions = Get-ExistingReviewSessions -PhaseContent $preFlightMatch }
     
-    $testsMatch = Extract-PhaseFromComment -CommentBody $existingComment.body -Emoji "🧪" -PhaseName "Tests"
-    if ($testsMatch) { $existingTestsSessions = Get-ExistingReviewSessions -PhaseContent $testsMatch }
-    
     $gateMatch = Extract-PhaseFromComment -CommentBody $existingComment.body -Emoji "🚦" -PhaseName "Gate"
     if ($gateMatch) { $existingGateSessions = Get-ExistingReviewSessions -PhaseContent $gateMatch }
     
@@ -601,14 +587,12 @@ if ($existingComment) {
 
 # Create NEW review sessions from current state file
 $newPreFlightSession = New-ReviewSession -PhaseContent $preFlightContent -CommitTitle $latestCommitTitle -CommitSha $latestCommitSha -CommitUrl $latestCommitUrl
-$newTestsSession = New-ReviewSession -PhaseContent $testsContent -CommitTitle $latestCommitTitle -CommitSha $latestCommitSha -CommitUrl $latestCommitUrl
 $newGateSession = New-ReviewSession -PhaseContent $gateContent -CommitTitle $latestCommitTitle -CommitSha $latestCommitSha -CommitUrl $latestCommitUrl
 $newFixSession = New-ReviewSession -PhaseContent $fixContent -CommitTitle $latestCommitTitle -CommitSha $latestCommitSha -CommitUrl $latestCommitUrl
 $newReportSession = New-ReviewSession -PhaseContent $reportContent -CommitTitle $latestCommitTitle -CommitSha $latestCommitSha -CommitUrl $latestCommitUrl
 
 # Merge existing sessions with new session (if new content exists)
 $allPreFlightSessions = if ($newPreFlightSession) { Merge-ReviewSessions -ExistingSessions $existingPreFlightSessions -NewSession $newPreFlightSession -NewCommitSha $latestCommitSha } else { $existingPreFlightSessions -join "`n`n---`n`n" }
-$allTestsSessions = if ($newTestsSession) { Merge-ReviewSessions -ExistingSessions $existingTestsSessions -NewSession $newTestsSession -NewCommitSha $latestCommitSha } else { $existingTestsSessions -join "`n`n---`n`n" }
 $allGateSessions = if ($newGateSession) { Merge-ReviewSessions -ExistingSessions $existingGateSessions -NewSession $newGateSession -NewCommitSha $latestCommitSha } else { $existingGateSessions -join "`n`n---`n`n" }
 $allFixSessions = if ($newFixSession) { Merge-ReviewSessions -ExistingSessions $existingFixSessions -NewSession $newFixSession -NewCommitSha $latestCommitSha } else { $existingFixSessions -join "`n`n---`n`n" }
 $allReportSessions = if ($newReportSession) { Merge-ReviewSessions -ExistingSessions $existingReportSessions -NewSession $newReportSession -NewCommitSha $latestCommitSha } else { $existingReportSessions -join "`n`n---`n`n" }
@@ -645,14 +629,12 @@ $Content
 
 # Build phase sections (only non-empty ones)
 $preFlightSection = New-PhaseSection -Icon "🔍" -PhaseName "Pre-Flight" -Subtitle "Context & Validation" -Content $allPreFlightSessions -Status $phaseStatuses['Pre-Flight']
-$testsSection = New-PhaseSection -Icon "🧪" -PhaseName "Tests" -Subtitle "Verification" -Content $allTestsSessions -Status $phaseStatuses['Tests']
 $gateSection = New-PhaseSection -Icon "🚦" -PhaseName "Gate" -Subtitle "Test Verification" -Content $allGateSessions -Status $phaseStatuses['Gate']
 $fixSection = New-PhaseSection -Icon "🔧" -PhaseName "Fix" -Subtitle "Analysis & Comparison" -Content $allFixSessions -Status $phaseStatuses['Fix']
 $reportSection = New-PhaseSection -Icon "📋" -PhaseName "Report" -Subtitle "Final Recommendation" -Content $allReportSessions -Status $phaseStatuses['Report']
 
 # Collect non-null sections
 if ($preFlightSection) { $phaseSections += $preFlightSection }
-if ($testsSection) { $phaseSections += $testsSection }
 if ($gateSection) { $phaseSections += $gateSection }
 if ($fixSection) { $phaseSections += $fixSection }
 if ($reportSection) { $phaseSections += $reportSection }
diff --git a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1 b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
index f3d889b51f69..2dd2919d2b16 100644
--- a/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
+++ b/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1
@@ -554,6 +554,8 @@ if ($CodeReviewStatus -ne "Skipped" -or -not [string]::IsNullOrWhiteSpace($CodeR
 
 <summary><b>Code Review: $codeReviewEmoji $codeReviewStatusDisplay</b></summary>
 
+<br>
+
 "@
 
     if (-not [string]::IsNullOrWhiteSpace($CodeReviewFindings)) {

PATCH

echo "Patch applied successfully."
