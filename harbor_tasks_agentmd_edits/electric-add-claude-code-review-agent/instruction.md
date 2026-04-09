# Add Claude Code review agent

## Task

Add a Claude Code review agent for automated PR reviews in the Electric repository. This involves creating GitHub Actions workflows and a command file that defines the review process.

## Changes Required

1. **Create `.github/workflows/claude-code-review.yml`** — Workflow that triggers when PRs are labeled with `claude` or when new commits are pushed to labeled PRs. This workflow should:
   - Run on `pull_request` events with types `labeled` and `synchronize`
   - Filter paths to only include relevant code changes (`packages/**`, `.github/**`, source files)
   - Execute only when the `claude` label is present
   - Gather PR context (previous reviews, conversation, linked issues)
   - Run the Claude Code review action with appropriate permissions

2. **Create `.github/workflows/claude.yml`** — Workflow for interactive `@claude` mentions in comments, issues, and PR reviews. This workflow should:
   - Trigger on `issue_comment`, `pull_request_review_comment`, `issues`, and `pull_request_review` events
   - Execute when `@claude` is mentioned
   - Run the Claude Code action for interactive assistance

3. **Create `.claude/commands/pr-review.md`** — Comprehensive 5-phase review command document covering:
   - Phase 1: Context gathering (PR details, linked issues, affected packages)
   - Phase 2: Analysis against project conventions (Elixir/OTP and TypeScript patterns)
   - Phase 3: Iteration awareness for incremental reviews
   - Phase 4: Structured review composition with severity guidelines
   - Phase 5: Posting the review via GitHub CLI

4. **Create `CLAUDE.md`** — Root-level agent instruction file that links to `AGENTS.md`

5. **Update `.gitignore`** — Change `.claude` to `.claude/settings.local.json` to allow tracking of command files while ignoring local settings

## Files to Look At

- `AGENTS.md` — Project conventions, architecture, and coding guidelines (read this to understand what CLAUDE.md should reference)
- `.github/workflows/` — Existing workflow patterns to follow
- `.gitignore` — Current ignore patterns

## Notes

- The `claude-code-review.yml` workflow uses the `anthropics/claude-code-action@v1` action
- The review command references `.review-context/` files that are prepared by the workflow
- Both workflows require `ANTHROPIC_API_KEY` secret (documented in PR description, not part of this fix)
