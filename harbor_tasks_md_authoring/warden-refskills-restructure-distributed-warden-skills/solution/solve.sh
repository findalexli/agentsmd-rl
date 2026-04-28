#!/usr/bin/env bash
set -euo pipefail

cd /workspace/warden

# Idempotency guard
if grep -qF "description: Full-repository code sweep. Scans every file with Warden, verifies " "skills/warden-sweep/SKILL.md" && grep -qF "| Known issues/workarounds | partial | Resume, partial scans, skipped findings, " "skills/warden-sweep/SOURCES.md" && grep -qF "It exists for batch remediation work where a normal targeted Warden run is too n" "skills/warden-sweep/SPEC.md" && grep -qF "3. If the script fails, show the error and continue to the patch phase. PRs can " "skills/warden-sweep/references/issue-phase.md" && grep -qF "Finalize sweep artifacts, security views, PR links, and the summary report." "skills/warden-sweep/references/organize-phase.md" && grep -qF "Run patch work using the host agent's task/delegation mechanism when available. " "skills/warden-sweep/references/patch-phase.md" && grep -qF "Continue from the first incomplete phase. Do not start a new sweep unless the us" "skills/warden-sweep/references/resume-and-artifacts.md" && grep -qF "4. Treat exit code `2` as partial: report timed-out and errored files separately" "skills/warden-sweep/references/scan-phase.md" && grep -qF "Runs setup and scan in one call: generates a run ID, creates the sweep directory" "skills/warden-sweep/references/script-interfaces.md" && grep -qF "2. Launch verification work using the host agent's task/delegation mechanism whe" "skills/warden-sweep/references/verify-phase.md" && grep -qF "| `<skill-root>/references/configuration.md` | Editing warden.toml, triggers, pa" "skills/warden/SKILL.md" && grep -qF "| Config/runtime options | covered | `references/configuration.md` and `referenc" "skills/warden/SOURCES.md" && grep -qF "It exists as the lightweight runtime companion to the Warden CLI. The skill shou" "skills/warden/SPEC.md" && grep -qF "- Per-Command Options" "skills/warden/references/cli-reference.md" && grep -qF "- Built-in Skip Patterns" "skills/warden/references/config-schema.md" && grep -qF "- Environment Variables" "skills/warden/references/configuration.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/warden-sweep/SKILL.md b/skills/warden-sweep/SKILL.md
@@ -1,350 +1,70 @@
 ---
 name: warden-sweep
-description: Full-repository code sweep. Scans every file with warden, verifies findings via deep tracing, creates draft PRs for validated issues. Use when asked to "sweep the repo", "scan everything", "find all bugs", "full codebase review", "batch code analysis", or run warden across the entire repository.
+description: Full-repository code sweep. Scans every file with Warden, verifies findings through deep tracing, creates draft PRs for validated issues. Use when asked to "sweep the repo", "scan everything", "find all bugs", "full codebase review", "batch code analysis", or run Warden across the entire repository.
 disable-model-invocation: true
 ---
 
 # Warden Sweep
 
-Full-repository code sweep: scan every file, verify findings with deep tracing, create draft PRs for validated issues.
+Run a full-repository Warden sweep: scan files, verify findings, create a tracking issue, open draft PRs for validated issues, and organize the final report.
 
-**Requires**: `warden`, `gh`, `git`, `jq`, `uv`
+**Requires**: `warden`, `gh`, `git`, `jq`, `uv`.
 
-**Important**: Run all scripts from the repository root using `${CLAUDE_SKILL_ROOT}`. Output goes to `.warden/sweeps/<run-id>/`.
+Run commands from the repository root. Use the host's skill-root path for bundled scripts and references.
 
-## Bundled Scripts
+Output goes to `.warden/sweeps/<run-id>/`.
 
-### `scripts/scan.py`
+## References
 
-Runs setup and scan in one call: generates run ID, creates sweep dir, checks deps, creates `warden` label, enumerates files, runs warden per file, extracts findings.
+Load only the reference for the current phase:
 
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/scan.py [file ...]
-  --sweep-dir DIR     # Resume into existing sweep dir
-```
-
-### `scripts/index_prs.py`
-
-Fetches open warden-labeled PRs, builds file-to-PR dedup index, caches diffs for overlapping PRs.
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/index_prs.py <sweep-dir>
-```
-
-### `scripts/create_issue.py`
-
-Creates a GitHub tracking issue summarizing sweep results. Run after verification, before patching.
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/create_issue.py <sweep-dir>
-```
-
-### `scripts/organize.py`
-
-Tags security findings, labels security PRs, updates finding reports with PR links, posts final results to tracking issue, generates summary report, finalizes manifest.
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/organize.py <sweep-dir>
-```
-
-### `scripts/extract_findings.py`
-
-Parses warden JSONL log files and extracts normalized findings. Called automatically by `scan.py`.
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/extract_findings.py <log-path-or-directory> -o <output.jsonl>
-```
-
-### `scripts/generate_report.py`
-
-Builds `summary.md` and `report.json` from sweep data. Called automatically by `organize.py`.
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/generate_report.py <sweep-dir>
-```
-
-### `scripts/find_reviewers.py`
-
-Finds top 2 git contributors for a file (last 12 months).
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/find_reviewers.py <file-path>
-```
-
-Returns JSON: `{"reviewers": ["user1", "user2"]}`
-
----
-
-## Phase 1: Scan
-
-**Run** (1 tool call):
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/scan.py
-```
-
-To resume a partial scan:
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/scan.py --sweep-dir .warden/sweeps/<run-id>
-```
-
-Parse the JSON stdout. Save `runId` and `sweepDir` for subsequent phases.
-
-**Report** to user:
-
-```
-## Scan Complete
-
-Scanned **{filesScanned}** files, **{filesTimedOut}** timed out, **{filesErrored}** errors.
-
-### Findings ({totalFindings} total)
-
-| # | Severity | Skill | File | Title |
-|---|----------|-------|------|-------|
-| 1 | **HIGH** | security-review | `src/db/query.ts:42` | SQL injection in query builder |
-...
-```
+| Need | Read |
+|------|------|
+| Script arguments, outputs, and side effects | `references/script-interfaces.md` |
+| Phase 1 scan workflow | `references/scan-phase.md` |
+| Phase 2 verification workflow | `references/verify-phase.md` |
+| Phase 3 tracking issue workflow | `references/issue-phase.md` |
+| Phase 4 patch and draft PR workflow | `references/patch-phase.md` |
+| Phase 5 organize and final report workflow | `references/organize-phase.md` |
+| Resume behavior and artifact layout | `references/resume-and-artifacts.md` |
+| Verification task prompt template | `references/verify-prompt.md` |
+| Patch task prompt template | `references/patch-prompt.md` |
 
-Render every finding from the `findings` array. Bold severity for high and above.
+## Workflow
 
-**On failure**: If exit code 1, show the error JSON and stop. If exit code 2, show the partial results. List timed-out files separately from errored files so users know which can be retried.
+Track progress across phases:
 
----
-
-## Phase 2: Verify
-
-Deep-trace each finding using Task subagents to qualify or disqualify.
+- [ ] Phase 1: Scan repository files with Warden.
+- [ ] Phase 2: Verify findings before patching.
+- [ ] Phase 3: Create a tracking issue.
+- [ ] Phase 4: Patch verified findings and open draft PRs.
+- [ ] Phase 5: Organize results and produce the final report.
 
-**For each finding in `data/all-findings.jsonl`:**
+## Phase Order
 
-Check if `data/verify/<finding-id>.json` already exists (incrementality). If it does, skip.
+1. Read `references/script-interfaces.md` once before running scripts.
+2. Run Phase 1 from `references/scan-phase.md`. Save `runId` and `sweepDir`.
+3. Run Phase 2 from `references/verify-phase.md`. Verify every finding before patching.
+4. Run Phase 3 from `references/issue-phase.md`. Continue if issue creation fails.
+5. Run Phase 4 from `references/patch-phase.md`. Patch sequentially, one finding at a time.
+6. Run Phase 5 from `references/organize-phase.md`.
+7. For interrupted or partial runs, read `references/resume-and-artifacts.md` and continue from the first incomplete phase.
 
-Launch a Task subagent (`subagent_type: "general-purpose"`) for each finding. Process findings in parallel batches of up to 8 to improve throughput.
+## Non-Negotiable Rules
 
-**Task prompt for each finding:**
+- Verify findings before creating fixes.
+- Use draft PRs for generated patches.
+- Branch every patch from the repository default branch.
+- Patch findings sequentially; do not run patch workers in parallel.
+- Skip existing entries in sweep artifacts instead of duplicating work.
+- Record failures in sweep data and continue to the next finding when possible.
+- Clean up each worktree after patch success or failure.
 
-Read `${CLAUDE_SKILL_ROOT}/references/verify-prompt.md` for the prompt template. Substitute the finding's values into the `${...}` placeholders.
+## Final Response
 
-**Process results:**
-
-Parse the JSON from the subagent response and:
-- Write result to `data/verify/<finding-id>.json`
-- Append to `data/verified.jsonl` or `data/rejected.jsonl`
-- For verified findings, generate `findings/<finding-id>.md`:
+After organizing, report:
 
 ```markdown
-# ${TITLE}
-
-**ID**: ${FINDING_ID} | **Severity**: ${SEVERITY} | **Confidence**: ${CONFIDENCE}
-**Skill**: ${SKILL} | **File**: ${FILE_PATH}:${START_LINE}
-
-## Description
-${DESCRIPTION}
-
-## Verification
-**Verdict**: Verified (${VERIFICATION_CONFIDENCE})
-**Reasoning**: ${REASONING}
-**Code trace**: ${TRACE_NOTES}
-
-## Suggested Fix
-${FIX_DESCRIPTION}
-```diff
-${FIX_DIFF}
-```
-```
-
-Update manifest: set `phases.verify` to `"complete"`.
-
-**Report** to user after all verifications:
-
-```
-## Verification Complete
-
-**{verified}** verified, **{rejected}** rejected.
-
-### Verified Findings
-
-| # | Severity | Confidence | File | Title | Reasoning |
-|---|----------|------------|------|-------|-----------|
-| 1 | **HIGH** | high | `src/db/query.ts:42` | SQL injection in query builder | User input flows directly into... |
-...
-
-### Rejected ({rejected_count})
-
-- `{findingId}` {file}: {reasoning}
-...
-```
-
----
-
-## Phase 3: Issue
-
-Create a tracking issue that ties all PRs together and gives reviewers a single overview.
-
-**Run** (1 tool call):
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/create_issue.py ${SWEEP_DIR}
-```
-
-Parse the JSON stdout. Save `issueUrl` and `issueNumber` for Phase 4.
-
-**Report** to user:
-
-```
-## Tracking Issue Created
-
-{issueUrl}
-```
-
-**On failure**: Show the error. Continue to Phase 4 (PRs can still be created without a tracking issue).
-
----
-
-## Phase 4: Patch
-
-For each verified finding, create a worktree, fix the code, and open a draft PR. Process findings **sequentially** (one at a time) since parallel subagents cross-contaminate worktrees.
-
-**Severity triage**: Patch HIGH and above. For MEDIUM, only patch findings from bug-detection skills (e.g., `code-review`, `security-review`). Skip LOW and INFO findings.
-
-**Step 0: Setup** (run once before the loop):
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/index_prs.py ${SWEEP_DIR}
-```
-
-Parse the JSON stdout. Use `fileIndex` for dedup checks.
-
-Determine the default branch and fetch latest so worktrees branch from current upstream:
-
-```bash
-DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
-git fetch origin "${DEFAULT_BRANCH}"
-```
-
-**For each finding in `data/verified.jsonl`:**
-
-Check if finding ID already exists in `data/patches.jsonl` (incrementality). If it does, skip.
-
-**Dedup check**: Use the file index from `index_prs.py` output to determine if an existing open PR already addresses the same issue.
-
-1. **File match**: Look up the finding's file path in the `fileIndex`. If no PR touches that file, no conflict; proceed to Step 1.
-2. **Chunk overlap**: If a PR does touch the same file, read its cached diff from `data/pr-diffs/<number>.diff` and check whether the PR's changed hunks overlap with the finding's line range (startLine-endLine). Overlapping or adjacent hunks (within ~10 lines) indicate the same code region.
-3. **Same concern**: If the hunks overlap, compare the PR title and the finding title/description. Are they fixing the same kind of defect? A PR fixing an off-by-one error and a finding about a null check in the same function are different issues; both should proceed.
-
-Skip the finding only when there is both chunk overlap AND the PR addresses the same concern. Record it in `data/patches.jsonl` with `"status": "existing"` and `"prUrl"` pointing to the matching PR, then continue to the next finding.
-
-**Step 1: Create worktree**
-
-```bash
-BRANCH="warden-sweep/${RUN_ID}/${FINDING_ID}"
-WORKTREE="${SWEEP_DIR}/worktrees/${FINDING_ID}"
-git worktree add "${WORKTREE}" -b "${BRANCH}" "origin/${DEFAULT_BRANCH}"
-```
-
-Each finding branches from the repo's default branch so PRs contain only the fix commit.
-
-**Step 2: Generate fix**
-
-Launch a Task subagent (`subagent_type: "general-purpose"`) to apply the fix in the worktree. Read `${CLAUDE_SKILL_ROOT}/references/patch-prompt.md` for the prompt template. Substitute the finding's values and worktree path into the `${...}` placeholders.
-
-**Step 2b: Handle skipped findings**
-
-If the subagent returned `"status": "skipped"` (not `"applied"`), do NOT proceed to Steps 3-4. Instead:
-1. Record the finding in `data/patches.jsonl` with `"status": "error"` and `"error": "Subagent skipped: ${skipReason}"`
-2. Clean up the worktree
-3. Continue to the next finding
-
-**Step 3: Find reviewers**
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/find_reviewers.py "${FILE_PATH}"
-```
-
-**Step 4: Create draft PR**
-
-```bash
-cd "${WORKTREE}" && git push -u origin HEAD:"${BRANCH}"
-```
-
-Create the PR with a 1-2 sentence "What" summary based on the finding and fix, followed by the finding description and verification reasoning:
-
-```bash
-REVIEWERS=""
-# If find_reviewers.py returned reviewers, build the flags
-# e.g., REVIEWERS="--reviewer user1 --reviewer user2"
-
-gh pr create --draft \
-  --label "warden" \
-  --title "fix: ${TITLE}" \
-  --body "$(cat <<'EOF'
-${FIX_WHAT_DESCRIPTION}
-
-${DESCRIPTION}
-
-${REASONING}
-
-Automated fix for Warden finding ${FINDING_ID} (${SEVERITY}, detected by ${SKILL}).
-
-<!-- Only include the next line if Phase 3 succeeded and ISSUE_NUMBER is available -->
-Ref #${ISSUE_NUMBER}
-
-> This PR was auto-generated by a Warden Sweep (run ${RUN_ID}).
-> The finding has been validated through automated deep tracing,
-> but human confirmation is requested as this is batch work.
-EOF
-)" ${REVIEWERS}
-```
-
-Save the PR URL.
-
-**Step 5: Record and cleanup**
-
-Append to `data/patches.jsonl` (use `"created"` as status for successful PRs, not the subagent's `"applied"`):
-```json
-{"findingId": "...", "prUrl": "https://...", "branch": "...", "reviewers": ["user1", "user2"], "filesChanged": ["..."], "status": "created|existing|error"}
-```
-
-Remove the worktree:
-```bash
-cd "$(git rev-parse --show-toplevel)"
-git worktree remove "${WORKTREE}" --force
-```
-
-**Error handling**: On failure at any step, write to `data/patches.jsonl` with `"status": "error"` and `"error": "..."`, clean up the worktree, and continue to the next finding.
-
-Update manifest: set `phases.patch` to `"complete"`.
-
-**Report** to user after all patches:
-
-```
-## PRs Created
-
-**{created}** created, **{skipped}** skipped (existing), **{failed}** failed.
-
-| # | Finding | PR | Status |
-|---|---------|-----|--------|
-| 1 | `security-review-a1b2c3d4` SQL injection in query builder | #142 | created |
-| 2 | `code-review-e5f6g7h8` Null pointer in handler | - | existing (#138) |
-...
-```
-
----
-
-## Phase 5: Organize
-
-**Run** (1 tool call):
-
-```bash
-uv run ${CLAUDE_SKILL_ROOT}/scripts/organize.py ${SWEEP_DIR}
-```
-
-Parse the JSON stdout.
-
-**Report** to user:
-
-```
 ## Sweep Complete
 
 | Metric | Count |
@@ -356,45 +76,3 @@ Parse the JSON stdout.
 
 Full report: `{summaryPath}`
 ```
-
-**On failure**: Show the error and note which steps completed.
-
----
-
-## Resuming a Sweep
-
-Each phase is incremental. To resume from where you left off:
-
-1. Check `data/manifest.json` to see which phases are complete
-2. For scan: pass `--sweep-dir` to `scan.py`
-3. For verify: existing `data/verify/<id>.json` files are skipped
-4. For issue: `create_issue.py` is idempotent (skips if `issueUrl` in manifest)
-5. For patch: existing entries in `data/patches.jsonl` are skipped
-6. For organize: safe to re-run (idempotent)
-
-## Output Directory Structure
-
-```
-.warden/sweeps/<run-id>/
-  summary.md                        # Stats, key findings, PR links
-  findings/                         # One markdown per verified finding
-    <finding-id>.md
-  security/                         # Security-specific view
-    index.jsonl                     # Security findings index
-    <finding-id>.md                 # Copies of security findings
-  data/                             # Structured data for tooling
-    manifest.json                   # Run metadata, phase state
-    scan-index.jsonl                # Per-file scan tracking
-    all-findings.jsonl              # Every finding from scan
-    verified.jsonl                  # Findings that passed verification
-    rejected.jsonl                  # Findings that failed verification
-    patches.jsonl                   # Finding -> PR URL -> reviewers
-    existing-prs.json               # Cached open warden PRs
-    report.json                     # Machine-readable summary
-    verify/                         # Individual verification results
-      <finding-id>.json
-    logs/                           # Warden JSONL logs per file
-      <hash>.jsonl
-    pr-diffs/                       # Cached PR diffs for dedup
-      <number>.diff
-```
diff --git a/skills/warden-sweep/SOURCES.md b/skills/warden-sweep/SOURCES.md
@@ -0,0 +1,43 @@
+# Warden Sweep Sources
+
+## Source Inventory
+
+| Source | Trust tier | Confidence | Usage constraints |
+|--------|------------|------------|-------------------|
+| `skills/warden-sweep/SKILL.md` | canonical runtime | high | Keep as router and phase overview. |
+| `skills/warden-sweep/references/*.md` | bundled runtime references | high | Keep focused by phase or lookup need. |
+| `skills/warden-sweep/scripts/*.py` | executable workflow | high | Script interfaces in references must match these files. |
+| `src/cli/output/jsonl.ts` | Warden output contract | high | Verify JSONL parsing assumptions when Warden output changes. |
+| `src/output/renderer.ts` and `src/types/` | finding/report semantics | high | Verify severity, confidence, and finding fields here. |
+| GitHub CLI commands used by scripts | external tool contract | medium | Confirm command flags when GitHub CLI behavior changes. |
+
+## Coverage Matrix
+
+| Dimension | Coverage status | Evidence |
+|-----------|-----------------|----------|
+| Workflow phases | covered | `SKILL.md` routes scan, verify, issue, patch, organize, and resume behavior to focused references. |
+| Script interfaces | covered | `references/script-interfaces.md` lists scripts, arguments, outputs, and side effects. |
+| Artifact schema | covered | `references/resume-and-artifacts.md` documents directories and key JSONL/JSON files. |
+| Verification behavior | covered | `references/verify-phase.md` and `references/verify-prompt.md` define qualification and rejection behavior. |
+| Patch behavior | covered | `references/patch-phase.md` and `references/patch-prompt.md` define triage, worktree isolation, draft PR creation, and cleanup. |
+| Known issues/workarounds | partial | Resume, partial scans, skipped findings, and existing PR dedup are covered; CI follow-up and rate-limit recovery are not. |
+| Version/migration variance | partial | Current artifact names and script interfaces are documented; no formal migration path exists for old sweep directories. |
+
+## Decisions
+
+- Split phase detail out of `SKILL.md` so agents load only the current phase instructions.
+- Keep script interface documentation separate from phase runbooks because scripts are reused across phases and by resume workflows.
+- Describe verification and patch work in host-neutral terms while allowing parallel agent tasks when the host supports them.
+- Keep prompt templates as separate references because they are substituted into delegated verification and patch work.
+- Keep generated sweep artifacts under `.warden/sweeps/<run-id>/` so runs are resumable and isolated from normal source files.
+
+## Open Gaps
+
+- Add a redacted fixture sweep to validate the full workflow without touching real GitHub repositories.
+- Document rate-limit and permission failure recovery if these become common in real sweeps.
+- Add migration notes if artifact schemas change after users have existing sweep directories.
+- Consider adding a script-level dry-run mode for issue and PR creation.
+
+## Changelog
+
+- 2026-04-27: Reverse-engineered maintenance spec and split the distributed `warden-sweep` workflow into phase references.
diff --git a/skills/warden-sweep/SPEC.md b/skills/warden-sweep/SPEC.md
@@ -0,0 +1,126 @@
+# Warden Sweep Skill Specification
+
+## Intent
+
+The `warden-sweep` skill runs a full-repository Warden scan, verifies findings through deeper code tracing, and creates draft PRs for validated issues.
+
+It exists for batch remediation work where a normal targeted Warden run is too narrow. The workflow is intentionally conservative: scan broadly, verify before patching, deduplicate against existing PRs, and record every decision in sweep artifacts.
+
+## Scope
+
+In scope:
+
+- Scanning a repository file-by-file with Warden.
+- Extracting and normalizing Warden findings.
+- Verifying findings before any code changes are attempted.
+- Creating a tracking issue for the sweep.
+- Creating one draft PR per validated issue that passes patch triage.
+- Organizing reports, security findings, PR links, and resumable sweep state.
+
+Out of scope:
+
+- Replacing human review of generated PRs.
+- Applying fixes directly to the user's current branch.
+- Patching low-confidence or unverified findings.
+- Running generic codebase review without Warden scan artifacts.
+- Managing CI iteration after PR creation.
+
+## Users And Trigger Context
+
+- Primary users: maintainers asking an agent to perform broad Warden-backed repository cleanup.
+- Common user requests: "sweep the repo", "scan everything", "find all bugs", "full codebase review", "batch code analysis", "run Warden across the whole repository".
+- Should not trigger for: normal pre-commit Warden runs, single-file checks, generic code review, or PR feedback iteration.
+
+## Runtime Contract
+
+- Required first actions:
+  - Confirm the repository has the required tools: `warden`, `gh`, `git`, `jq`, and `uv`.
+  - Run `scripts/scan.py` from the repository root using the host skill-root path.
+  - Preserve the returned `runId` and `sweepDir`.
+  - Resume existing sweep artifacts instead of duplicating work when a sweep directory is provided.
+- Required outputs:
+  - Phase summaries after scan, verification, issue creation, patching, and organization.
+  - Final pointer to the generated summary report.
+  - Explicit counts for scanned files, timeouts/errors, verified/rejected findings, created/existing/failed PRs, and security findings.
+- Non-negotiable constraints:
+  - Verify findings before patching.
+  - Patch findings sequentially to avoid worktree and branch cross-contamination.
+  - Create draft PRs, not direct commits to the default branch.
+  - Record errors in sweep data and continue to the next finding when possible.
+  - Clean up worktrees after patch attempts.
+- Expected bundled files loaded at runtime:
+  - `references/script-interfaces.md`
+  - `references/scan-phase.md`
+  - `references/verify-phase.md`
+  - `references/issue-phase.md`
+  - `references/patch-phase.md`
+  - `references/organize-phase.md`
+  - `references/resume-and-artifacts.md`
+  - `references/verify-prompt.md`
+  - `references/patch-prompt.md`
+  - `scripts/*.py`
+
+## Source And Evidence Model
+
+Authoritative sources:
+
+- `skills/warden-sweep/SKILL.md` and bundled references.
+- `skills/warden-sweep/scripts/*.py`.
+- Warden JSONL output schema and renderer code in `src/cli/output/`.
+- GitHub CLI behavior for PRs, issues, labels, and repo metadata.
+
+Useful improvement sources:
+
+- positive examples: completed sweeps with verified findings, clean draft PRs, and accurate final reports
+- negative examples: duplicate PRs, false positive patches, failed worktree cleanup, incorrect artifact state, or patch contamination across findings
+- commit logs/changelogs: changes to Warden output, script behavior, or sweep artifact schema
+- issue or PR feedback: reviewer complaints about generated PR quality, false positives, or sweep noise
+- eval results: dry-run prompts for scan resume, verification, patch triage, and final organization
+
+Data that must not be stored:
+
+- secrets, credentials, or tokens
+- private customer data
+- raw issue/PR content unrelated to the sweep finding
+- unredacted sensitive code excerpts beyond what is needed in local sweep artifacts
+
+## Reference Architecture
+
+- `SKILL.md` contains the phase overview, routing table, universal constraints, and completion contract.
+- `SOURCES.md` contains source inventory, coverage, decisions, gaps, and changelog.
+- `references/` contains focused phase runbooks, prompt templates, script interfaces, and artifact layout.
+- `references/evidence/` is unused until durable examples are needed.
+- `scripts/` contains repeatable automation for scan, extraction, issue creation, PR indexing, reviewer selection, report generation, and organization.
+- `assets/` is unused.
+
+## Evaluation
+
+- Lightweight validation:
+  - Run the skill validator against `skills/warden-sweep`.
+  - Confirm every script mentioned in `SKILL.md` and references exists.
+  - Confirm every phase reference has one clear lookup purpose.
+- Deeper evaluation:
+  - Run a dry sweep in a small fixture repository when script or artifact behavior changes.
+  - Exercise resume paths for scan, verify, issue, patch, and organize phases.
+- Holdout examples:
+  - Store redacted false positive and duplicate-PR examples in `references/evidence/` if these failures recur.
+- Acceptance gates:
+  - Findings are verified before patching.
+  - Patch phase creates isolated branches and draft PRs.
+  - Existing overlapping PRs are detected before creating new PRs.
+  - Final artifacts are resumable and summarize errors separately from successful work.
+
+## Known Limitations
+
+- The workflow depends on external CLIs and repository permissions.
+- Verification and patching quality depends on the host agent's ability to inspect code deeply.
+- The skill uses host-agent delegation when available; hosts without parallel delegation can run the same verification steps serially.
+- Broad scans can be expensive and noisy if repository Warden configuration is too broad.
+
+## Maintenance Notes
+
+- Update `SKILL.md` when phase order, universal constraints, or routing changes.
+- Update `SOURCES.md` when source inventory, decisions, coverage, or known gaps change.
+- Update phase references when script arguments, output shapes, artifact schema, or error handling changes.
+- Update prompt templates when verification or patch quality failures recur.
+- Update `references/evidence/` when preserving redacted examples will improve future iterations.
diff --git a/skills/warden-sweep/references/issue-phase.md b/skills/warden-sweep/references/issue-phase.md
@@ -0,0 +1,24 @@
+# Issue Phase
+
+Create a tracking issue that ties all generated PRs together and gives reviewers one overview.
+
+## Run
+
+```bash
+uv run <skill-root>/scripts/create_issue.py ${SWEEP_DIR}
+```
+
+## Process
+
+1. Parse the JSON stdout.
+2. Save `issueUrl` and `issueNumber`.
+3. If the script fails, show the error and continue to the patch phase. PRs can still be created without a tracking issue.
+4. Update the checklist: Phase 3 complete.
+
+## Report Template
+
+```markdown
+## Tracking Issue Created
+
+{issueUrl}
+```
diff --git a/skills/warden-sweep/references/organize-phase.md b/skills/warden-sweep/references/organize-phase.md
@@ -0,0 +1,31 @@
+# Organize Phase
+
+Finalize sweep artifacts, security views, PR links, and the summary report.
+
+## Run
+
+```bash
+uv run <skill-root>/scripts/organize.py ${SWEEP_DIR}
+```
+
+## Process
+
+1. Parse the JSON stdout.
+2. Confirm `summary.md` and `data/report.json` were produced.
+3. If the script fails, show the error and note which phases completed.
+4. Update the checklist: Phase 5 complete.
+
+## Report Template
+
+```markdown
+## Sweep Complete
+
+| Metric | Count |
+|--------|-------|
+| Files scanned | {filesScanned} |
+| Findings verified | {verified} |
+| PRs created | {prsCreated} |
+| Security findings | {securityFindings} |
+
+Full report: `{summaryPath}`
+```
diff --git a/skills/warden-sweep/references/patch-phase.md b/skills/warden-sweep/references/patch-phase.md
@@ -0,0 +1,142 @@
+# Patch Phase
+
+Create isolated fixes for verified findings and open draft PRs.
+
+## Contents
+
+- Rules
+- Setup
+- Per-Finding Process
+- Dedup Check
+- Worktree, Fix, Reviewers, And PR
+- Report Template
+
+## Rules
+
+- Patch high-severity and above.
+- Patch medium findings only when they come from bug-detection skills such as `code-review` or `security-review`.
+- Skip low and info findings.
+- Process findings sequentially.
+- Create one worktree and one branch per finding.
+- Clean up worktrees after success or failure.
+
+## Setup
+
+Index existing PRs before patching:
+
+```bash
+uv run <skill-root>/scripts/index_prs.py ${SWEEP_DIR}
+```
+
+Parse the JSON stdout and use `fileIndex` for dedup checks.
+
+Determine the default branch and fetch latest:
+
+```bash
+DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
+git fetch origin "${DEFAULT_BRANCH}"
+```
+
+## Per-Finding Process
+
+For each finding in `data/verified.jsonl`:
+
+1. If the finding ID already exists in `data/patches.jsonl`, skip it.
+2. Run the dedup check.
+3. Create a worktree.
+4. Apply the fix using `references/patch-prompt.md`.
+5. If the patch task returns `"status": "skipped"`, record an error, clean up the worktree, and continue.
+6. Find reviewers.
+7. Push the branch.
+8. Create a draft PR.
+9. Record the result in `data/patches.jsonl`.
+10. Clean up the worktree.
+
+## Dedup Check
+
+Use the file index from `index_prs.py`:
+
+1. File match: if no open Warden PR touches the finding file, proceed.
+2. Chunk overlap: if a PR touches the same file, read `data/pr-diffs/<number>.diff` and check whether changed hunks overlap or sit within roughly 10 lines of the finding range.
+3. Same concern: compare PR title and finding title/description.
+
+Skip the finding only when there is both chunk overlap and the PR addresses the same concern. Record it with `"status": "existing"` and the matching `prUrl`.
+
+## Worktree, Fix, Reviewers, And PR
+
+```bash
+BRANCH="warden-sweep/${RUN_ID}/${FINDING_ID}"
+WORKTREE="${SWEEP_DIR}/worktrees/${FINDING_ID}"
+git worktree add "${WORKTREE}" -b "${BRANCH}" "origin/${DEFAULT_BRANCH}"
+```
+
+Each finding branches from the default branch so PRs contain only the fix commit.
+
+Run patch work using the host agent's task/delegation mechanism when available. Read `references/patch-prompt.md` and substitute the finding values and worktree path into the `${...}` placeholders.
+
+If delegated tasks are not available, apply the prompt instructions yourself in the worktree.
+
+```bash
+uv run <skill-root>/scripts/find_reviewers.py "${FILE_PATH}"
+```
+
+```bash
+cd "${WORKTREE}" && git push -u origin HEAD:"${BRANCH}"
+```
+
+Create the PR with a short "what" summary followed by the finding description and verification reasoning:
+
+```bash
+gh pr create --draft \
+  --label "warden" \
+  --title "fix: ${TITLE}" \
+  --body "$(cat <<'EOF'
+${FIX_WHAT_DESCRIPTION}
+
+${DESCRIPTION}
+
+${REASONING}
+
+Automated fix for Warden finding ${FINDING_ID} (${SEVERITY}, detected by ${SKILL}).
+
+<!-- Only include the next line if Phase 3 succeeded and ISSUE_NUMBER is available -->
+Ref #${ISSUE_NUMBER}
+
+> This PR was auto-generated by a Warden Sweep (run ${RUN_ID}).
+> The finding has been validated through automated deep tracing,
+> but human confirmation is requested as this is batch work.
+EOF
+)" ${REVIEWERS}
+```
+
+## Record Result
+
+Append to `data/patches.jsonl`. Use `"created"` for successful PRs, not the patch task's `"applied"` status.
+
+```json
+{"findingId": "...", "prUrl": "https://...", "branch": "...", "reviewers": ["user1", "user2"], "filesChanged": ["..."], "status": "created|existing|error"}
+```
+
+Clean up:
+
+```bash
+cd "$(git rev-parse --show-toplevel)"
+git worktree remove "${WORKTREE}" --force
+```
+
+On failure at any step, write `"status": "error"` with an `"error"` message, clean up the worktree, and continue.
+
+Update the manifest: set `phases.patch` to `"complete"`.
+
+## Report Template
+
+```markdown
+## PRs Created
+
+**{created}** created, **{skipped}** skipped (existing), **{failed}** failed.
+
+| # | Finding | PR | Status |
+|---|---------|----|--------|
+| 1 | `security-review-a1b2c3d4` SQL injection in query builder | #142 | created |
+| 2 | `code-review-e5f6g7h8` Null pointer in handler | - | existing (#138) |
+```
diff --git a/skills/warden-sweep/references/resume-and-artifacts.md b/skills/warden-sweep/references/resume-and-artifacts.md
@@ -0,0 +1,51 @@
+# Resume And Artifacts
+
+Use this reference when resuming a partial sweep or inspecting generated files.
+
+## Resume Rules
+
+Each phase is incremental:
+
+1. Check `data/manifest.json` for phase state.
+2. For scan, pass `--sweep-dir` to `scan.py`.
+3. For verify, skip existing `data/verify/<id>.json` files.
+4. For issue, `create_issue.py` skips if `issueUrl` exists in the manifest.
+5. For patch, skip existing entries in `data/patches.jsonl`.
+6. For organize, rerun safely.
+
+Continue from the first incomplete phase. Do not start a new sweep unless the user asks for a clean run.
+
+## Output Directory Structure
+
+```text
+.warden/sweeps/<run-id>/
+  summary.md                        # Stats, key findings, PR links
+  findings/                         # One markdown per verified finding
+    <finding-id>.md
+  security/                         # Security-specific view
+    index.jsonl                     # Security findings index
+    <finding-id>.md                 # Copies of security findings
+  data/                             # Structured data for tooling
+    manifest.json                   # Run metadata, phase state
+    scan-index.jsonl                # Per-file scan tracking
+    all-findings.jsonl              # Every finding from scan
+    verified.jsonl                  # Findings that passed verification
+    rejected.jsonl                  # Findings that failed verification
+    patches.jsonl                   # Finding -> PR URL -> reviewers
+    existing-prs.json               # Cached open Warden PRs
+    report.json                     # Machine-readable summary
+    verify/                         # Individual verification results
+      <finding-id>.json
+    logs/                           # Warden JSONL logs per file
+      <hash>.jsonl
+    pr-diffs/                       # Cached PR diffs for dedup
+      <number>.diff
+```
+
+## Failure Handling
+
+- Preserve partial artifacts.
+- Record per-finding errors in the relevant JSONL file.
+- Distinguish timed-out files from errored files.
+- Clean up worktrees before retrying patch work.
+- Re-run organize after manual recovery to refresh reports.
diff --git a/skills/warden-sweep/references/scan-phase.md b/skills/warden-sweep/references/scan-phase.md
@@ -0,0 +1,46 @@
+# Scan Phase
+
+Run Warden across repository files and collect normalized findings.
+
+## Run
+
+```bash
+uv run <skill-root>/scripts/scan.py
+```
+
+To scan only specific files:
+
+```bash
+uv run <skill-root>/scripts/scan.py src/foo.ts src/bar.ts
+```
+
+To resume a partial scan:
+
+```bash
+uv run <skill-root>/scripts/scan.py --sweep-dir .warden/sweeps/<run-id>
+```
+
+## Process
+
+1. Parse the JSON stdout.
+2. Save `runId` and `sweepDir`.
+3. Treat exit code `1` as fatal and stop.
+4. Treat exit code `2` as partial: report timed-out and errored files separately, then continue only if the user accepts the partial results.
+5. Render every finding from the `findings` array.
+6. Update the checklist: Phase 1 complete.
+
+## Report Template
+
+```markdown
+## Scan Complete
+
+Scanned **{filesScanned}** files, **{filesTimedOut}** timed out, **{filesErrored}** errors.
+
+### Findings ({totalFindings} total)
+
+| # | Severity | Skill | File | Title |
+|---|----------|-------|------|-------|
+| 1 | **HIGH** | security-review | `src/db/query.ts:42` | SQL injection in query builder |
+```
+
+Bold severity for high and above.
diff --git a/skills/warden-sweep/references/script-interfaces.md b/skills/warden-sweep/references/script-interfaces.md
@@ -0,0 +1,127 @@
+# Script Interfaces
+
+Use this reference before running Warden Sweep scripts. Run scripts from the repository root and pass the host skill-root path.
+
+## Contents
+
+- `scan.py`
+- `index_prs.py`
+- `create_issue.py`
+- `organize.py`
+- `extract_findings.py`
+- `generate_report.py`
+- `find_reviewers.py`
+
+## `scripts/scan.py`
+
+Runs setup and scan in one call: generates a run ID, creates the sweep directory, checks dependencies, creates the `warden` label, enumerates files, runs Warden per file, writes `scan-index.jsonl`, and extracts findings.
+
+```bash
+uv run <skill-root>/scripts/scan.py [file ...]
+uv run <skill-root>/scripts/scan.py --sweep-dir .warden/sweeps/<run-id>
+```
+
+Stdout JSON:
+
+```json
+{
+  "runId": "abc123",
+  "sweepDir": ".warden/sweeps/abc123",
+  "filesScanned": 10,
+  "filesTimedOut": 0,
+  "filesErrored": 0,
+  "totalFindings": 3,
+  "findings": []
+}
+```
+
+Exit codes: `0` success, `1` fatal error, `2` partial scan.
+
+## `scripts/index_prs.py`
+
+Fetches open Warden-labeled PRs, builds a file-to-PR dedup index, and caches diffs for overlapping PRs.
+
+```bash
+uv run <skill-root>/scripts/index_prs.py <sweep-dir>
+```
+
+Stdout JSON includes `fileIndex`. Side effects:
+
+- writes `data/existing-prs.json`
+- writes `data/pr-diffs/<number>.diff` for overlapping PRs
+
+## `scripts/create_issue.py`
+
+Creates a GitHub tracking issue summarizing verified sweep results.
+
+```bash
+uv run <skill-root>/scripts/create_issue.py <sweep-dir>
+```
+
+Stdout JSON:
+
+```json
+{
+  "issueUrl": "https://github.com/owner/repo/issues/123",
+  "issueNumber": 123
+}
+```
+
+Idempotent: skips creation when `issueUrl` already exists in the manifest.
+
+## `scripts/organize.py`
+
+Tags security findings, labels security PRs, updates finding reports with PR links, posts final results to the tracking issue, generates the summary report, and finalizes the manifest.
+
+```bash
+uv run <skill-root>/scripts/organize.py <sweep-dir>
+```
+
+Stdout JSON includes final sweep counts and report paths. Side effects:
+
+- creates `security/index.jsonl`
+- copies security finding reports to `security/`
+- creates or reuses the `security` GitHub label
+- labels security PRs
+- appends PR links to `findings/*.md`
+- writes `summary.md` and `data/report.json`
+- updates `phases.organize` in `data/manifest.json`
+
+## `scripts/extract_findings.py`
+
+Parses Warden JSONL log files and extracts normalized findings. Usually called by `scan.py`.
+
+```bash
+uv run <skill-root>/scripts/extract_findings.py <log-path-or-directory> -o <output.jsonl>
+```
+
+Writes one normalized finding per line to `<output.jsonl>`.
+
+## `scripts/generate_report.py`
+
+Builds `summary.md` and `report.json` from sweep data. Usually called by `organize.py`.
+
+```bash
+uv run <skill-root>/scripts/generate_report.py <sweep-dir>
+```
+
+Side effects:
+
+- writes `<sweep-dir>/summary.md`
+- writes `<sweep-dir>/data/report.json`
+
+## `scripts/find_reviewers.py`
+
+Finds the top two git contributors for a file from the last 12 months.
+
+```bash
+uv run <skill-root>/scripts/find_reviewers.py <file-path>
+```
+
+Stdout JSON:
+
+```json
+{
+  "reviewers": ["user1", "user2"]
+}
+```
diff --git a/skills/warden-sweep/references/verify-phase.md b/skills/warden-sweep/references/verify-phase.md
@@ -0,0 +1,69 @@
+# Verify Phase
+
+Deep-trace every finding before patching. This phase qualifies true issues and rejects false positives.
+
+## Input
+
+Read findings from:
+
+```text
+<sweep-dir>/data/all-findings.jsonl
+```
+
+## Process
+
+For each finding:
+
+1. If `data/verify/<finding-id>.json` exists, skip it.
+2. Launch verification work using the host agent's task/delegation mechanism when available. Process findings in parallel batches up to 8 if the host supports parallel work.
+3. Read `references/verify-prompt.md` and substitute the finding values into the `${...}` placeholders.
+4. Parse the returned JSON.
+5. Write the raw result to `data/verify/<finding-id>.json`.
+6. Append verified findings to `data/verified.jsonl`.
+7. Append rejected findings to `data/rejected.jsonl`.
+8. For verified findings, generate `findings/<finding-id>.md`.
+
+If the host does not support delegated tasks, run the same verification prompt serially.
+
+## Verified Finding Report
+
+````markdown
+# ${TITLE}
+
+**ID**: ${FINDING_ID} | **Severity**: ${SEVERITY} | **Confidence**: ${CONFIDENCE}
+**Skill**: ${SKILL} | **File**: ${FILE_PATH}:${START_LINE}
+
+## Description
+${DESCRIPTION}
+
+## Verification
+**Verdict**: Verified (${VERIFICATION_CONFIDENCE})
+**Reasoning**: ${REASONING}
+**Code trace**: ${TRACE_NOTES}
+
+## Suggested Fix
+${FIX_DESCRIPTION}
+```diff
+${FIX_DIFF}
+```
+````
+
+Update the manifest: set `phases.verify` to `"complete"`.
+
+## Report Template
+
+```markdown
+## Verification Complete
+
+**{verified}** verified, **{rejected}** rejected.
+
+### Verified Findings
+
+| # | Severity | Confidence | File | Title | Reasoning |
+|---|----------|------------|------|-------|-----------|
+| 1 | **HIGH** | high | `src/db/query.ts:42` | SQL injection in query builder | User input flows directly into... |
+
+### Rejected ({rejected_count})
+
+- `{findingId}` {file}: {reasoning}
+```
diff --git a/skills/warden/SKILL.md b/skills/warden/SKILL.md
@@ -11,10 +11,10 @@ Read the relevant reference when the task requires deeper detail:
 
 | Document | Read When |
 |----------|-----------|
-| `${CLAUDE_SKILL_ROOT}/references/cli-reference.md` | Full option details, per-command flags, examples |
-| `${CLAUDE_SKILL_ROOT}/references/configuration.md` | Editing warden.toml, triggers, patterns, troubleshooting |
-| `${CLAUDE_SKILL_ROOT}/references/config-schema.md` | Exact field names, types, and defaults |
-| `${CLAUDE_SKILL_ROOT}/references/creating-skills.md` | Writing custom skills, remote skills, skill discovery |
+| `<skill-root>/references/cli-reference.md` | Full option details, per-command flags, examples |
+| `<skill-root>/references/configuration.md` | Editing warden.toml, triggers, patterns, troubleshooting |
+| `<skill-root>/references/config-schema.md` | Exact field names, types, and defaults |
+| `<skill-root>/references/creating-skills.md` | Writing custom skills, remote skills, skill discovery |
 
 ## Running Warden
 
@@ -73,4 +73,4 @@ Run Warden once to validate work. Do not loop re-running Warden on the same chan
 | `warden sync [remote]` | Update cached remote skills |
 | `warden setup-app` | Create GitHub App via manifest flow |
 
-For full options and flags, read `${CLAUDE_SKILL_ROOT}/references/cli-reference.md`.
+For full options and flags, read `<skill-root>/references/cli-reference.md`.
diff --git a/skills/warden/SOURCES.md b/skills/warden/SOURCES.md
@@ -0,0 +1,39 @@
+# Warden Skill Sources
+
+## Source Inventory
+
+| Source | Trust tier | Confidence | Usage constraints |
+|--------|------------|------------|-------------------|
+| `skills/warden/SKILL.md` | canonical runtime | high | Keep concise; runtime instructions only. |
+| `skills/warden/references/*.md` | bundled runtime references | high | Keep focused by lookup need. |
+| `src/cli/` | implementation | high | Verify CLI flags and behavior here before changing examples. |
+| `src/config/` and `src/types/` | implementation | high | Verify config field names, defaults, and validation rules here. |
+| `packages/docs/src/pages/cli.astro` | generated/user docs source | medium | Useful for CLI descriptions, but implementation wins on conflicts. |
+| `packages/docs/src/pages/config.astro` | generated/user docs source | medium | Useful for config examples, but implementation wins on conflicts. |
+| `packages/docs/src/pages/skill.astro` | generated/user docs source | medium | Useful for install and skill-discovery language. |
+
+## Coverage Matrix
+
+| Dimension | Coverage status | Evidence |
+|-----------|-----------------|----------|
+| CLI surface | covered | `references/cli-reference.md` lists commands, targets, flags, exit codes, and examples. |
+| Config/runtime options | covered | `references/configuration.md` and `references/config-schema.md` cover `warden.toml` structure, fields, defaults, triggers, and environment variables. |
+| Common use cases | covered | `SKILL.md` covers run-before-commit, explicit skill runs, file targets, git refs, fix mode, and config edits. |
+| Known issues/workarounds | partial | `references/configuration.md` has troubleshooting; CLI auth and install failures could use more detail. |
+| Version/migration variance | partial | Remote skill pinning and cache behavior are documented; package-version migration notes are not maintained here. |
+
+## Decisions
+
+- Keep `SKILL.md` as a quick router because agents often need only a command, not the full CLI documentation.
+- Keep CLI, config, schema, and skill creation in separate references so agents can load only the relevant detail.
+- Keep Warden-specific skill creation guidance in this skill even though generic skill authoring belongs elsewhere, because Warden has its own discovery, config, and remote-skill behavior.
+
+## Open Gaps
+
+- Add or verify an auth/setup troubleshooting reference if repeated agent runs fail before Warden can execute.
+- Confirm CLI examples after each release that changes flags, output modes, or init/add/sync behavior.
+- Add migration notes if Warden introduces breaking config changes beyond `version = 1`.
+
+## Changelog
+
+- 2026-04-27: Reverse-engineered maintenance spec and source inventory from the distributed `warden` skill.
diff --git a/skills/warden/SPEC.md b/skills/warden/SPEC.md
@@ -0,0 +1,112 @@
+# Warden Skill Specification
+
+## Intent
+
+The `warden` skill teaches coding agents how to run Warden during local development, interpret its output, and update Warden configuration or skill definitions when asked.
+
+It exists as the lightweight runtime companion to the Warden CLI. The skill should get agents to the right command or reference quickly without duplicating the full product documentation.
+
+## Scope
+
+In scope:
+
+- Running Warden against uncommitted changes, explicit files, or git refs.
+- Reading and editing `warden.toml`.
+- Explaining Warden CLI flags, exit codes, severity thresholds, and output modes.
+- Creating or wiring local Warden analysis skills.
+- Directing agents to focused bundled references for detailed CLI, config, and skill-authoring behavior.
+
+Out of scope:
+
+- Replacing Warden product documentation.
+- Running full-repository batch sweeps; use `warden-sweep` for that workflow.
+- Defining project-specific review policy.
+- Teaching generic agent skill authoring beyond Warden-specific discovery and config.
+
+## Users And Trigger Context
+
+- Primary users: coding agents working in repositories that use Warden.
+- Common user requests: "run warden", "check my changes", "review before commit", "update warden.toml", "add a Warden trigger", "create a Warden skill".
+- Should not trigger for: ordinary code review requests with no Warden context, generic testing, PR writing, or full-repository sweep requests.
+
+## Runtime Contract
+
+- Required first actions:
+  - Identify whether the user wants to run Warden, edit config, inspect output, or create/update a Warden skill.
+  - Load only the reference needed for that task.
+  - Prefer local repository configuration over generic examples.
+- Required outputs:
+  - For runs: summarize command used, findings count, failure threshold, and next action.
+  - For config edits: state the changed trigger or setting and how to validate it.
+  - For skill creation: state where the skill was created and how it is referenced.
+- Non-negotiable constraints:
+  - Do not loop Warden repeatedly on unchanged work.
+  - Do not invent config fields; check `references/config-schema.md` for exact names.
+  - Do not treat Warden findings as advisory text to suppress; fix the code or explicitly explain why a finding is not actionable.
+- Expected bundled files loaded at runtime:
+  - `references/cli-reference.md`
+  - `references/configuration.md`
+  - `references/config-schema.md`
+  - `references/creating-skills.md`
+
+## Source And Evidence Model
+
+Authoritative sources:
+
+- Warden CLI behavior in `src/cli/`.
+- Warden config loading and schemas in `src/config/` and `src/types/`.
+- Documentation pages in `packages/docs/src/pages/`.
+- Existing runtime references in `skills/warden/references/`.
+
+Useful improvement sources:
+
+- positive examples: agent sessions where Warden was run once, findings were fixed, and config edits used valid schema fields
+- negative examples: repeated Warden reruns with no changes, invented config fields, stale CLI flags, or generic skill instructions that do not match Warden discovery
+- commit logs/changelogs: CLI flag changes, config schema changes, and skill discovery changes
+- issue or PR feedback: reports of confusing Warden setup, missing command coverage, or stale agent skill docs
+- eval results: local prompts covering run, config, output interpretation, and skill creation paths
+
+Data that must not be stored:
+
+- secrets, tokens, or API keys
+- customer data
+- private repository URLs or identifiers not needed for reproduction
+- raw Warden logs containing sensitive code or findings
+
+## Reference Architecture
+
+- `SKILL.md` contains task routing, quick commands, core constraints, and the reference map.
+- `SOURCES.md` contains source inventory, coverage, gaps, and changelog.
+- `references/` contains focused CLI, config, schema, and Warden skill creation guides.
+- `references/evidence/` is unused until repeated examples need durable storage.
+- `scripts/` is unused; this skill delegates execution to the installed `warden` CLI.
+- `assets/` is unused.
+
+## Evaluation
+
+- Lightweight validation:
+  - Run the skill validator against `skills/warden`.
+  - Check that every referenced bundled file exists.
+  - Spot-check CLI flags and config fields against source or generated docs.
+- Deeper evaluation:
+  - Exercise prompts for running Warden, adding a trigger, explaining output, and creating a skill.
+- Holdout examples:
+  - Preserve only redacted examples if recurring failures appear.
+- Acceptance gates:
+  - `SKILL.md` stays concise and routes to focused references.
+  - Long references include navigation.
+  - Config examples use valid field names.
+  - Trigger description catches Warden-specific local development tasks without matching generic code review.
+
+## Known Limitations
+
+- The skill assumes the `warden` CLI is installed and authenticated where required.
+- CLI and config details can drift when source changes without updating the bundled references.
+- Some host agents expose different skill-root variables; references are written as bundled file paths, while examples may need host-specific substitution.
+
+## Maintenance Notes
+
+- Update `SKILL.md` when task routing, trigger language, or universal run constraints change.
+- Update `SOURCES.md` when source inventory, decisions, coverage, or gaps change.
+- Update references when CLI flags, config fields, remote skill behavior, or examples change.
+- Update `references/evidence/` only for durable positive or negative examples that should guide future iterations.
diff --git a/skills/warden/references/cli-reference.md b/skills/warden/references/cli-reference.md
@@ -1,13 +1,22 @@
 # CLI Reference
 
+## Contents
+
+- Usage
+- Commands
+- Targets
+- Options
+- Per-Command Options
+- Severity Levels
+- Exit Codes
+- Examples
+
 ## Usage
 
 ```
 warden [command] [targets...] [options]
 ```
 
-Analyze code for security issues and code quality.
-
 ## Commands
 
 | Command | Description |
@@ -83,8 +92,6 @@ Ambiguous targets (no path separator, no extension) are resolved by checking if
 
 ## Severity Levels
 
-Used in `--fail-on` and `--report-on`:
-
 | Level | Meaning |
 |-------|---------|
 | `high` | Must fix before merge |
diff --git a/skills/warden/references/config-schema.md b/skills/warden/references/config-schema.md
@@ -1,5 +1,14 @@
 # warden.toml Configuration Schema
 
+## Contents
+
+- Top-Level Structure
+- Defaults Section
+- Skills Section
+- Severity Values
+- Built-in Skip Patterns
+- Environment Variables
+
 ## Top-Level Structure
 
 ```toml
diff --git a/skills/warden/references/configuration.md b/skills/warden/references/configuration.md
@@ -1,5 +1,14 @@
 # Configuration (warden.toml)
 
+## Contents
+
+- Minimal Example
+- Skill Configuration
+- Common Patterns
+- Model Precedence
+- Environment Variables
+- Troubleshooting
+
 See [config-schema.md](config-schema.md) for the complete schema reference.
 
 ## Minimal Example
PATCH

echo "Gold patch applied."
