# Add a PR Review Agent Skill

## Problem

The Angular repository uses agent skills under `.agent/skills/` to guide AI agents working in the codebase. Currently, there is no skill for reviewing pull requests. The existing skills cover writing guides and reference documentation for specific packages, but agents have no structured guidance for conducting PR reviews.

Additionally, `.agent/skills` is currently a symlink pointing to `../.gemini/skills`. The skills should live directly under `.agent/skills/` as real files, not through a symlink.

## What Needs to Be Done

1. **Replace the `.agent/skills` symlink** with a real directory. Copy the existing skills from `.gemini/skills/` into `.agent/skills/` so they remain available.

2. **Create a new PR review skill** at `.agent/skills/pr_review/` with:
   - A `SKILL.md` that provides comprehensive guidelines for reviewing pull requests in the Angular repository. This should cover:
     - The importance of reviewing the **entire** PR, not just a user's specific area of concern
     - Key focus areas: code cleanliness, performance, testing, API design, payload size, commit messages
     - Both **local** review workflow (for PRs the reviewer authored) and **remote** review workflow (for others' PRs)
     - A strategy for **batching review comments** into a single review submission to avoid spamming the PR author with multiple notifications
     - Prefixing agent-generated comments with an identifier so they're distinguishable from human comments
   - A `reference/router.md` with package-specific review guidelines for the Angular Router, noting its sensitivity to timing changes
   - Helper bash scripts under `scripts/` for PR review operations. Create exactly these 5 executable scripts:
     - `determine_review_type.sh` - Determines whether a review should be local or remote based on PR authorship
     - `get_pr_comments.sh` - Fetches existing PR comments to avoid duplicate feedback
     - `post_inline_comment.sh` - Stages inline comments to a local JSON file (e.g., `/tmp/angular_pr_${PR_NUMBER}_comments.json`) for batching; does NOT post immediately
     - `reply_pr_comment.sh` - Replies to existing PR comment threads
     - `submit_pr_review.sh` - Submits all staged comments as a single batched review via the GitHub API

3. **Scripts must validate arguments** and print usage information when called incorrectly. They should use `set -euo pipefail` for safety. The scripts must:
   - Exit with non-zero status and print usage/error when called with insufficient arguments
   - The scripts `post_inline_comment.sh` and `submit_pr_review.sh` must use `jq` for JSON manipulation
   - `submit_pr_review.sh` must support three event types: `COMMENT`, `APPROVE`, and `REQUEST_CHANGES`

The 5 helper scripts are: `determine_review_type.sh`, `get_pr_comments.sh`, `post_inline_comment.sh`, `reply_pr_comment.sh`, and `submit_pr_review.sh`.

The existing skills that must be preserved under `.agent/skills/` are: `adev-writing-guide`, `reference-compiler-cli`, `reference-core`, and `reference-signal-forms`.

## Files to Look At

- `.agent/skills/` — existing skills directory (currently a symlink)
- `.gemini/skills/` — where existing skill files currently live
- `.agent/rules/agents.md` — existing agent rules for context on Angular conventions

After implementing the code changes, make sure the agent skill documentation is thorough and covers the workflows described above.
