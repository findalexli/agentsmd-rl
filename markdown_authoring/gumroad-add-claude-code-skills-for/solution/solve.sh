#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gumroad

# Idempotency guard
if grep -qF "2. Run `git diff` and `git diff --cached` to understand staged and unstaged chan" ".claude/skills/commit/SKILL.md" && grep -qF "The root cause. Explain the technical reason the problem exists \u2014 not just sympt" ".claude/skills/create-issue/SKILL.md" && grep -qF "Generate a concise, high-quality PR description from the current branch and its " ".claude/skills/pr-description/SKILL.md" && grep -qF "Inertia.js caches the entire `page.props` object in browser history state. When " ".claude/skills/pr-description/references/example.md" && grep -qF "Check the diff against every applicable rule in CONTRIBUTING.md (code standards," ".claude/skills/review-pr/SKILL.md" && grep -qF "Supplementary review guidance beyond what CONTRIBUTING.md already covers. Read C" ".claude/skills/review-pr/references/review-guidance.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/commit/SKILL.md b/.claude/skills/commit/SKILL.md
@@ -0,0 +1,38 @@
+---
+name: commit
+description: Stage and commit changes with a clear, concise commit message.
+argument-hint: [optional message hint]
+allowed-tools: Bash(git *)
+---
+
+# Commit
+
+Create a commit for the current changes.
+
+## Steps
+
+1. Run `git status` (without `-uall`) to see untracked and modified files.
+2. Run `git diff` and `git diff --cached` to understand staged and unstaged changes.
+3. Run `git log --oneline -5` to see recent commit style.
+4. Stage the relevant files by name — avoid `git add -A` or `git add .`.
+5. Write a commit message and commit.
+
+If `$ARGUMENTS` is provided, use it as a hint for the message.
+
+## Commit message rules
+
+- Use the imperative mood ("Add", "Fix", "Remove", not "Added", "Fixes", "Removed").
+- Be concise: one short sentence, ideally under 50 characters.
+- Do NOT use conventional commit prefixes (no `feat:`, `fix:`, `chore:`, etc.).
+- Do NOT add any `Co-Authored-By` or similar trailers.
+- Focus on **what** changed and **why**, not how.
+- If a second line is needed for context, keep it brief.
+
+## Examples of good messages
+
+- `Prevent discount code from being cleared on edit`
+- `Add integration test for offer code persistence`
+- `Remove unused legacy export helper`
+- `Fix thumbnail missing in upsell insert`
+
+$ARGUMENTS
diff --git a/.claude/skills/create-issue/SKILL.md b/.claude/skills/create-issue/SKILL.md
@@ -0,0 +1,100 @@
+---
+name: create-issue
+description: >
+  Draft GitHub issues for the Gumroad codebase. Outputs to an unstaged markdown file in the repo
+  root. Never creates issues on GitHub. Triggers on: "create issue", "write issue", "draft issue",
+  "write a bug report", "file an issue", "create a ticket", or when the user describes a problem
+  or feature they want to turn into a GitHub issue.
+---
+
+# Issue Drafting
+
+Draft well-structured GitHub issues. Output to an unstaged `.md` file — never post to GitHub.
+
+## Workflow
+
+### 1. Understand the Problem
+
+Gather context from the user. Ask clarifying questions if needed:
+
+- What's happening vs what should happen?
+- Who's affected and how often?
+- Any workarounds in use?
+- Is there data that quantifies the impact?
+
+If the user points to code, trace the relevant paths to understand the root cause. Include aggregated, anonymized data that quantifies the impact when available (e.g., "99 purchases across 82 sellers are in this state"). Never include PII — no emails, names, IDs, or payment details.
+
+### 2. Decide: Single Issue or Parent + Sub-issues
+
+Before writing, assess the scope:
+
+**Single issue** when:
+
+- One clear problem with one solution path
+- The fix would be one PR (~100 LOC per CONTRIBUTING.md)
+- No independent workstreams
+
+**Parent + sub-issues** when:
+
+- The solution has multiple independently shippable parts
+- Different parts could be worked on in parallel or by different people
+- The total scope would exceed one reasonably-sized PR
+- There's a logical sequence (e.g., API integration → webhook fix → backfill)
+
+If suggesting sub-issues, number the solution parts clearly and note which can be done independently vs which depend on each other. Write the parent issue as the full document, then note where to split.
+
+### 3. Write the Issue
+
+Structure:
+
+**## What**
+The problem, concretely. Include:
+
+- What's happening and what the impact is
+- Who's affected (users, sellers, internal team)
+- Quantify with data when possible (error rates, support ticket counts)
+- Link to related issues, Slack threads, or prior attempts
+- Mention workarounds people are using and why they're insufficient
+
+**## Why**
+The root cause. Explain the technical reason the problem exists — not just symptoms. Reference code areas and behaviors (e.g., "the PayPal webhook handler" or "the dispute resolution flow"), not specific file paths or line numbers — those change. This is what makes the issue actionable rather than just a complaint.
+
+**## Proposed solution**
+High-level direction that's technically sound but not overly prescriptive. Give enough guidance that someone can start working without a long investigation phase, while leaving room for implementation decisions:
+
+- Name the approach and why it's the right one
+- If there are API constraints or non-obvious technical details, explain them (link to external docs when relevant)
+- Number the parts if the solution has multiple steps
+- Note alternatives considered and why they were rejected, if relevant
+- Don't dictate implementation details like exact method signatures or class names — describe what needs to happen, not exactly how to code it
+
+**## Acceptance criteria**
+Checkboxes. Each one should be independently testable. Cover:
+
+- The happy path
+- Key edge cases
+- Things that should NOT change (e.g., "Stripe behavior is unchanged")
+
+**## Edge cases** (when applicable)
+Call out non-obvious scenarios: race conditions, ordering issues, backward compatibility, migration concerns.
+
+### 4. Output
+
+Write to `gh-issue-draft.md` in the repo root. Do NOT stage or commit.
+
+If the issue should be split into sub-issues, write the parent issue first, then add a `## Sub-issues` section at the end listing each sub-issue with a one-line summary. The user can split them manually.
+
+## Style
+
+- Concise and direct. No jargon, no filler.
+- Ground claims in data or code references — don't just say "this is a problem," show it.
+- Use `product` not `link`, `buyer`/`seller` not `customer`/`creator` per CONTRIBUTING.md.
+- Link to external docs (API references, etc.) where they add clarity.
+- Reference code by area or concept ("the dispute webhook handler"), not by file:line — those change.
+- The issue is public (open source). It must be **self-contained**: an OSS contributor who has no access to prod, Slack, or internal tools should have everything they need to implement it without asking follow-up questions.
+- Include aggregated data when it quantifies the problem. **Never include PII** — no emails, user IDs, names, or payment details.
+
+## Important
+
+- Use `gh` read-only only. Never create issues via CLI.
+- The user reviews and posts manually — just write the best possible draft.
diff --git a/.claude/skills/pr-description/SKILL.md b/.claude/skills/pr-description/SKILL.md
@@ -0,0 +1,123 @@
+---
+name: pr-description
+description: >
+  Generate a PR description for the current branch and its linked GitHub issue.
+  Outputs to an unstaged markdown file in the repo root. Never creates or updates PRs.
+  Triggers on: "generate PR description", "write PR description", "PR description",
+  "describe this PR", "draft PR", or after completing implementation work when the user
+  wants to prepare a PR. Also use when the user says "pr", "pull request description",
+  or asks to summarize their branch changes for review.
+---
+
+# PR Description Generator
+
+Generate a concise, high-quality PR description from the current branch and its linked GitHub issue. Output to an unstaged `.md` file — never publish or update a PR.
+
+## Workflow
+
+### 1. Gather Context
+
+Run these in parallel:
+
+```bash
+# Current branch name
+git branch --show-current
+
+# Commits on this branch vs main
+git log main..HEAD --oneline
+
+# Full diff against main
+git diff main...HEAD
+
+# Check for linked issue number in branch name or commits
+# Branch names often follow: username/issue-description or fix/NNNN-description
+```
+
+If the branch name or commits reference an issue number, fetch it:
+
+```bash
+gh issue view <number> --repo antiwork/gumroad --comments
+```
+
+If no issue number is found, ask the user.
+
+### 2. Understand the Change
+
+From the issue and diff, determine:
+
+- **What problem was being solved** (or what feature was requested)
+- **What approach was taken** (high-level concept, not file-by-file)
+- **Whether this is a UI change** (look for view/component/CSS changes)
+
+Read key changed files if the diff alone doesn't make the approach clear.
+
+### 3. Write the Description
+
+Use the template below. Adapt sections based on what's relevant — not every section is needed for every PR.
+
+**Style rules:**
+
+- Write in simple, direct language. Avoid jargon.
+- Focus on _why_ and _how at a high level_ — not what files changed.
+- No file change summaries or lists of modified files.
+- No checklists.
+- Succinct PR title: no "feat:" prefix, but "Fix:" is fine for bug fixes.
+- Keep it concise. A few clear sentences beat a wall of text.
+
+#### Template
+
+```markdown
+Fixes #<issue-number>
+
+## Problem
+
+[Why this change exists. What was broken or missing. 1-3 sentences max.]
+
+## Approach
+
+[High-level concept of the solution. What strategy was used and why.
+NOT a list of file changes. If there were alternative approaches considered,
+briefly explain why this one was chosen.]
+
+<!-- BEFORE/AFTER — include for UI/CSS changes, delete this section otherwise
+## Before/After
+
+Before:
+<!-- screenshot or video -->
+
+After:
+
+<!-- screenshot or video -->
+
+Include: Desktop (light + dark) and Mobile (light + dark) if applicable.
+-->
+
+<!-- TEST RESULTS — include a screenshot of test suite passing locally
+## Test Results
+
+<!-- screenshot -->
+
+-->
+
+---
+
+This PR was implemented with AI assistance using Claude Code for code generation. All code was self-reviewed.
+```
+
+See [references/example.md](references/example.md) for a well-received PR description example.
+
+### 4. Output the File
+
+Write the description to `gh-pr-draft.md` in the repo root. Do NOT stage or commit this file.
+
+If `gh-pr-draft.md` already exists, overwrite it.
+
+Tell the user the file was created and suggest they review it before posting.
+
+## Important
+
+- Use `gh` read-only only. Never create, comment on, or update PRs.
+- Always fetch the GitHub issue — it provides critical context for the Problem section.
+- Omit the Before/After section entirely for non-UI changes (remove the HTML comment too).
+- Omit the Test Results section if not applicable (remove the HTML comment too).
+- The AI disclaimer is always the last line, after a `---` separator.
diff --git a/.claude/skills/pr-description/references/example.md b/.claude/skills/pr-description/references/example.md
@@ -0,0 +1,43 @@
+# Example: Well-Received PR Description
+
+This PR was well-received by the Gumroad team. Use it as a style reference.
+
+```markdown
+Fixes #2562
+
+## Problem
+
+Inertia.js caches the entire `page.props` object in browser history state. When users navigate backward/forward, the browser restores the cached props including the flash message, causing it to re-render even though it was already displayed.
+
+## Approach
+
+Clear the flash prop from Inertia's cache immediately after displaying the message using `router.replaceProp("flash", null)`. This is a client-side operation that modifies the current page state without making a server request.
+
+Created a `useFlashMessage` hook that displays the flash and clears it from cache, then updated the layouts to use it.
+
+### Why This Approach
+
+Other open PRs for this issue:
+
+- **#2655** uses server-side ID generation + sessionStorage tracking (adds backend changes and storage management)
+- **#2614** removes flash from Inertia props entirely (invasive restructure)
+- **#2613** uses `router.replace({ props: ... })` (similar concept, older API)
+
+This PR uses `router.replaceProp()` — the direct Inertia v2 API designed for single-prop updates. No server changes, no storage management, minimal code.
+
+## Before/After
+
+Before:
+https://github.com/user-attachments/assets/46a53f8e-cb14-4930-8301-34943af3a5f2
+
+After:
+https://github.com/user-attachments/assets/23efb2b5-c533-4ec4-9a29-59ee7a07c1cd
+
+## Test Results
+
+<img width="602" height="141" alt="Screenshot 2026-01-06 at 23 10 31" src="https://github.com/user-attachments/assets/d7b2ba00-5007-4100-bb0a-85b6fb04d87f" />
+
+---
+
+This PR was implemented with AI assistance using Claude Code for code generation. All code was self-reviewed.
+```
diff --git a/.claude/skills/review-pr/SKILL.md b/.claude/skills/review-pr/SKILL.md
@@ -0,0 +1,115 @@
+---
+name: review-pr
+description: >
+  Review GitHub pull requests for the Gumroad codebase against project guidelines, code quality,
+  and correctness. Use when the user wants to review a PR, check new comments on a PR, provide
+  feedback on code changes, or asks about PR quality. Triggers on: "review PR", "review this PR",
+  "check PR #NNN", any GitHub PR URL (e.g. https://github.com/antiwork/gumroad/pull/NNNN),
+  "what's new on the PR", "check comments", "review the diff", "give feedback on this PR",
+  or requests to evaluate code changes in a pull request.
+---
+
+# PR Review
+
+Review pull requests for code quality, correctness, and CONTRIBUTING.md compliance.
+
+**Scope boundary**: This skill evaluates _how the code is written_. For evaluating _whether the PR solves the right problem_, use the `issue-detective` skill instead.
+
+## Workflow
+
+### 1. Fetch PR Context
+
+```bash
+gh pr view <number> --repo antiwork/gumroad
+gh pr diff <number> --repo antiwork/gumroad
+gh pr view <number> --repo antiwork/gumroad --comments
+gh api repos/antiwork/gumroad/pulls/<number>/comments
+```
+
+Also read `CONTRIBUTING.md` from the repo root — it's the source of truth for all guideline checks.
+
+Note PR status (draft, closed, merged). Skip review if merged or closed unless user insists.
+
+### 2. Understand the Change
+
+From the diff and description, determine:
+
+- What changed and why (read the linked issue if referenced)
+- Bug fix, feature, refactor, or chore
+- Which layers are affected (frontend, backend, both, tests only)
+- Size and complexity
+
+Read key modified files in full when the diff alone is insufficient to understand context.
+
+### 3. Review
+
+Run these review passes on the diff:
+
+**Pass 1 — Bugs and Logic Errors**
+Wrong conditionals, missing edge cases, race conditions, nil/null handling, off-by-one errors, security vulnerabilities (injection, XSS, CSRF). Focus on code paths introduced or modified by the PR.
+
+**Pass 2 — CONTRIBUTING.md Compliance**
+Check the diff against every applicable rule in CONTRIBUTING.md (code standards, naming conventions, testing standards, Sidekiq patterns, PR structure, etc.). The file is the single source of truth — do not maintain a separate checklist.
+
+**Pass 3 — Code Clarity**
+Evaluate readability and maintainability of new/modified code. See [references/review-guidance.md](references/review-guidance.md) for what to flag vs what to leave alone. The goal is clear, explicit code — not clever or compact code.
+
+**Pass 4 — PR Structure**
+AI disclosure, description quality (explains _why_), before/after for UI changes, test results, appropriate size — all per CONTRIBUTING.md.
+
+### 4. Score and Filter
+
+Assign each finding a confidence score (0–100): how likely is this a genuine problem?
+
+**Keep** findings >= 80. **Drop** findings below 80.
+
+See [references/review-guidance.md](references/review-guidance.md) for noise filtering rules and severity levels.
+
+### 5. Report
+
+```
+## Summary
+
+[1-2 sentences: what the PR does and overall assessment]
+
+## Issues
+
+### [critical|important|suggestion] Title
+**File:** `path/to/file.rb:NN`
+**Confidence:** NN/100
+
+[Concise explanation and fix suggestion if straightforward.]
+
+...
+
+## Checklist
+
+[CONTRIBUTING.md items that are missing — e.g., no AI disclosure, no before/after, missing tests]
+
+## Verdict
+
+[approve / request-changes / comment-only — with brief justification]
+```
+
+Write the review to `gh-pr-review.md` in the repo root. Do NOT stage or commit. Do NOT post to GitHub.
+
+### 6. Iterate
+
+When the user asks to re-check a PR (new comments, updated diff):
+
+```bash
+gh pr view <number> --repo antiwork/gumroad --comments
+gh api repos/antiwork/gumroad/pulls/<number>/comments
+gh pr diff <number> --repo antiwork/gumroad
+```
+
+Focus on what changed since the last review. Don't repeat prior findings unless still unaddressed.
+
+## Important
+
+- Use `gh` read-only only. Never approve, comment on, or request changes via CLI.
+- Review what the PR _introduces_ — not pre-existing code.
+- Be direct and concise. No filler praise.
+- Prioritize substantive issues over cosmetic ones.
+- When unsure, state uncertainty rather than false confidence.
+- For large PRs (1k+ lines), note the PR should be broken up.
diff --git a/.claude/skills/review-pr/references/review-guidance.md b/.claude/skills/review-pr/references/review-guidance.md
@@ -0,0 +1,41 @@
+# PR Review Guidance
+
+Supplementary review guidance beyond what CONTRIBUTING.md already covers. Read CONTRIBUTING.md first — this file adds the reviewer's lens.
+
+## Code Clarity Pass (inspired by code-simplifier philosophy)
+
+Evaluate readability and maintainability of new/modified code. The goal is clear, explicit code — not clever or compact code.
+
+Flag:
+
+- Unnecessary nesting that could be flattened (early returns, guard clauses)
+- Redundant code that could be consolidated without premature abstraction
+- Unclear variable/method names that require mental decoding
+- Nested ternaries — prefer if/else or case/switch for multiple conditions
+- Overly dense one-liners that sacrifice readability for brevity
+
+Do NOT flag:
+
+- Code that's already clear enough — don't suggest changes for marginal improvement
+- Three similar lines that could theoretically be abstracted — duplication is fine if the cases are independent
+- Missing type annotations or docstrings on code that's self-explanatory
+- Style preferences not backed by CONTRIBUTING.md
+
+## Noise Filtering
+
+Confidence scoring (0–100) for each finding. Only report findings >= 80.
+
+### Always drop (regardless of score)
+
+- Pre-existing issues not introduced by the PR
+- Issues a linter, formatter, or type checker would catch
+- Style nitpicks not covered by CONTRIBUTING.md
+- Changes to lines outside the PR diff
+- Suggestions that would add unnecessary complexity or abstraction
+- Speculation about potential future bugs without concrete evidence
+
+### Severity levels
+
+- **critical**: Would cause incorrect behavior, data loss, security vulnerability, or production breakage
+- **important**: Violates CONTRIBUTING.md, introduces tech debt, or has a meaningful quality impact
+- **suggestion**: Could improve clarity or maintainability but isn't wrong as-is
PATCH

echo "Gold patch applied."
