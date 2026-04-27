#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git comman" "plugins/compound-engineering/AGENTS.md" && grep -qF "- **Describe the net result, not the journey**: The PR description is about the " "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/AGENTS.md b/plugins/compound-engineering/AGENTS.md
@@ -114,7 +114,7 @@ Why: shell-heavy exploration causes avoidable permission prompts in sub-agent wo
 
 - [ ] Never instruct agents to use `find`, `ls`, `cat`, `head`, `tail`, `grep`, `rg`, `wc`, or `tree` through a shell for routine file discovery, content search, or file reading
 - [ ] Describe tools by capability class with platform hints — e.g., "Use the native file-search/glob tool (e.g., Glob in Claude Code)" — not by Claude Code-specific tool names alone
-- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no chaining (`&&`, `||`, `;`), pipes, or redirects
+- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no chaining (`&&`, `||`, `;`) and no error suppression (`2>/dev/null`, `|| true`). Simple pipes (e.g., `| jq .field`) and output redirection (e.g., `> file`) are acceptable when they don't obscure failures
 - [ ] Do not encode shell recipes for routine exploration when native tools can do the job; encode intent and preferred tool classes instead
 - [ ] For shell-only workflows (e.g., `gh`, `git`, `bundle show`, project CLIs), explicit command examples are acceptable when they are simple, task-scoped, and not chained together
 
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -30,20 +30,35 @@ Follow this priority order for commit messages *and* PR titles:
 2. **Recent commit history** -- If no explicit convention exists, match the pattern visible in the last 10 commits.
 3. **Default: conventional commits** -- `type(scope): description` as the fallback.
 
-### Step 3: Branch, stage, and commit
+### Step 3: Check for existing PR
+
+Before committing, check whether a PR already exists for the current branch:
+
+```bash
+command gh pr view --json url,title,state
+```
+
+Interpret the result:
+
+- If it **returns PR data with `state: OPEN`**, note the URL and continue to Step 4 (commit) and Step 5 (push). Then skip to Step 7 (existing PR flow) instead of creating a new PR.
+- If it **returns PR data with a non-OPEN state** (CLOSED, MERGED), treat this the same as "no PR exists" -- the previous PR is done and a new one is needed.
+- If it **errors with "no pull requests found"**, no PR exists. Continue to Step 4 through Step 8 as normal.
+- If it **errors for another reason** (auth, network, repo config), report the error to the user and stop.
+
+### Step 4: Branch, stage, and commit
 
 1. If on `main` or the repo's default branch, create a descriptive feature branch first (`command git checkout -b <branch-name>`). Derive the branch name from the change content.
 2. Before staging everything together, scan the changed files for naturally distinct concerns. If modified files clearly group into separate logical changes (e.g., a refactor in one set of files and a new feature in another), create separate commits for each group. Keep this lightweight -- group at the **file level only** (no `git add -p`), split only when obvious, and aim for two or three logical commits at most. If it's ambiguous, one commit is fine.
 3. Stage relevant files by name. Avoid `git add -A` or `git add .` to prevent accidentally including sensitive files.
 4. Commit following the conventions from Step 2. Use a heredoc for the message.
 
-### Step 4: Push
+### Step 5: Push
 
 ```bash
 command git push -u origin HEAD
 ```
 
-### Step 5: Write the PR description
+### Step 6: Write the PR description
 
 This is the most important step. The description must be **adaptive** -- its depth should match the complexity of the change. A one-line bugfix does not need a table of performance results. A large architectural change should not be a bullet list.
 
@@ -69,6 +84,7 @@ Use this to select the right description depth:
 #### Writing principles
 
 - **Lead with value**: The first sentence should tell the reviewer *why this PR exists*, not *what files changed*. "Fixes timeout errors during batch exports" beats "Updated export_handler.py and config.yaml".
+- **Describe the net result, not the journey**: The PR description is about the end state -- what changed and why. Do not include work-product details like bugs found and fixed during development, intermediate failures, debugging steps, iteration history, or refactoring done along the way. Those are part of getting the work done, not part of the result. If a bug fix happened during development, the fix is already in the diff -- mentioning it in the description implies it's a separate concern the reviewer should evaluate, when really it's just part of the final implementation. Exception: include process details only when they are critical for a reviewer to understand a design choice (e.g., "tried approach X first but it caused Y, so went with Z instead").
 - **Explain the non-obvious**: If the diff is self-explanatory, don't narrate it. Spend description space on things the diff *doesn't* show: why this approach, what was considered and rejected, what the reviewer should pay attention to.
 - **Use structure when it earns its keep**: Headers, bullet lists, and tables are tools -- use them when they aid comprehension, not as mandatory template sections. An empty "## Breaking Changes" section adds noise.
 - **Markdown tables for data**: When there are before/after comparisons, performance numbers, or option trade-offs, a table communicates density well. Example:
@@ -103,18 +119,62 @@ Write:
 
 When referencing actual GitHub issues or PRs, use the full format: `org/repo#123` or the full URL. Never use bare `#123` unless you have verified it refers to the correct issue in the current repository.
 
-### Step 6: Create the PR
+#### Compound Engineering badge
+
+Append a badge footer to the PR description, separated by a `---` rule. Do not add one if the description already contains a Compound Engineering badge (e.g., added by another skill like ce-work).
+
+```markdown
+---
+
+[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
+🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
+```
+
+Fill in at PR creation time:
+
+| Placeholder | Value | Example |
+|-------------|-------|---------|
+| `[MODEL]` | Model name | Claude Opus 4.6, GPT-5.4 |
+| `[CONTEXT]` | Context window (if known) | 200K, 1M |
+| `[THINKING]` | Thinking level (if known) | extended thinking |
+| `[HARNESS]` | Tool running you | Claude Code, Codex, Gemini CLI |
+| `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |
+| `[VERSION]` | `plugin.json` -> `version` | 2.40.0 |
+
+### Step 7: Create or update the PR
+
+#### New PR (no existing PR from Step 3)
 
 ```bash
 command gh pr create --title "the pr title" --body "$(cat <<'EOF'
 PR description here
+
+---
+
+[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
+🤖 Generated with [MODEL] ([CONTEXT] context, [THINKING]) via [HARNESS](HARNESS_URL)
 EOF
 )"
 ```
 
 Keep the PR title under 72 characters. The title follows the same convention as commit messages (Step 2).
 
-### Step 7: Report
+#### Existing PR (found in Step 3)
+
+The new commits are already on the PR from the push in Step 5. Report the PR URL, then ask the user whether they want the PR description updated to reflect the new changes. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the option and wait for the user's reply before proceeding.
+
+- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits), including the Compound Engineering badge unless one is already present in the existing description. Apply it:
+
+  ```bash
+  command gh pr edit --body "$(cat <<'EOF'
+  Updated description here
+  EOF
+  )"
+  ```
+
+- If **no** -- done. The push was all that was needed.
+
+### Step 8: Report
 
 Output the PR URL so the user can navigate to it directly.
 
PATCH

echo "Gold patch applied."
