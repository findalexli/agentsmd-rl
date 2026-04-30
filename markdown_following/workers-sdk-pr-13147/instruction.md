# Improve Bonk to Read Triggering Comments and Act on Fixup Requests

## Task

The Bonk agent in this repository has two behavioral problems that need to be fixed through updates to its agent instruction file.

### Problem 1: Ignoring the Triggering Comment

When invoked via `/bonk` or `@ask-bonk`, Bonk sometimes ignores the specific request in the triggering comment and falls back to performing a generic full PR review. For example, if a maintainer comments `/bonk fix the formatting on this PR and commit the result`, Bonk might post a review listing formatting problems instead of running the formatter and pushing the fix.

Add a new non-negotiable rule with a heading like **"Triggering comment is the task"** that establishes: the comment that invoked the agent (`/bonk` or `@ask-bonk`) is its primary instruction. The agent must read the triggering comment first, parse exactly what it asks for, then gather only the context needed to execute that request. It must not fall back to a generic PR review when a specific action was requested.

### Problem 2: Re-reviewing Instead of Fixing

When Bonk has previously reviewed a PR and a maintainer then asks it to fix something (e.g., `/bonk address the review comments`), Bonk sometimes performs a second full review and restates the same findings rather than reading its own prior review comments and fixing each one in code.

Add a new non-negotiable rule with a heading like **"No re-reviewing on fixup requests"** that states: if the agent previously reviewed the PR and the maintainer now asks it to fix something, it must not review again. It must act on the specific request in the triggering comment.

### Additional Requirement: Workflow Restructuring

The implementation workflow should be reorganized so that the first two steps are:
1. **"Start from the triggering comment"** — Parse what it asks for and identify the concrete action(s) requested (e.g., "fix the formatting", "address the review comments", "add a changeset"). This is the task; everything else is context-gathering in service of it.
2. **"Gather only the context you need"** — Only pull in context required for the task identified in step 1 (e.g., read review comments if the request references feedback; a self-contained request like "run the formatter" may not need the full PR at all).

The workflow should also include a step instructing the agent not to re-review the PR when the request is to fix something.

### Examples Section

The examples section should be updated to include negative examples demonstrating the incorrect behaviors described above, along with their correct counterparts:

- A fixup formatting request where Bonk previously reviewed: the incorrect behavior is doing a second full review; the correct behavior is reading the triggering comment, running the formatter, committing, and pushing.
- An "address the review comments" request where Bonk previously reviewed: the incorrect behavior is re-reviewing and restating findings; the correct behavior is reading its own prior review comments, fixing each in code, committing, and pushing.

## Target File

The file to modify is the Bonk agent instruction file at `.opencode/agents/bonk.md`. It is a markdown file with YAML frontmatter that defines the agent's role, non-negotiable rules, mode selection logic, implementation workflow, examples, and anti-patterns.

## Requirements

- Preserve all existing rules, conventions, and structure that are not explicitly mentioned for change
- Maintain the YAML frontmatter block unchanged
- The non-negotiable rules section should gain two new rules
- The implementation workflow should be renumbered to 14 steps (from 13)
- The examples section heading should be pluralized ("Negative examples")
- All existing positive examples must remain unchanged
