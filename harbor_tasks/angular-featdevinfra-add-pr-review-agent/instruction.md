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
   - Helper bash scripts under `scripts/` for PR review operations:
     - Determining whether a review should be local or remote (based on PR authorship)
     - Fetching existing PR comments (to avoid duplicate feedback)
     - Staging inline comments locally to a file
     - Replying to existing PR comment threads
     - Submitting all staged comments as a single batched review

3. **Scripts must validate arguments** and print usage information when called incorrectly. They should use `set -euo pipefail` for safety.

## Files to Look At

- `.agent/skills/` — existing skills directory (currently a symlink)
- `.gemini/skills/` — where existing skill files currently live
- `.agent/rules/agents.md` — existing agent rules for context on Angular conventions

After implementing the code changes, make sure the agent skill documentation is thorough and covers the workflows described above.
