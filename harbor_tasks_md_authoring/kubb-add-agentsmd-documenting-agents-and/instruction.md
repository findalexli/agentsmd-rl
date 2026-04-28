# Add AGENTS.md documenting agents and docs layout

Source: [kubb-labs/kubb#2051](https://github.com/kubb-labs/kubb/pull/2051)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `docs/AGENTS.md`

## What to add / change

Adds documentation for automated agent usage (AI assistants, CI bots, Dependabot) and docs contribution guidelines.

## Files Added

- **`/AGENTS.md`** — Repository-level guidance on:
  - Which agents are used (Dependabot, GitHub Actions, AI assistants)
  - Review checklist for agent-generated PRs
  - Security expectations (no secrets, credential handling)
  - Merge guidelines
  - Changelog and documentation requirements (update changelog.md after versions, use pnpm changeset, update docs after plugin changes)

- **`/docs/AGENTS.md`** — Docs-site version with additional:
  - Docs folder conventions (structure, naming, frontmatter)
  - Example docs tree layout
  - PR guidance for documentation changes
  - Review criteria for agent-created docs

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

Add two new files to the repository to document how automated agents are used and to clarify the docs layout and contribution guidelines.

Files to add:

1) AGENTS.md (root)
- Path: /AGENTS.md
- Purpose: high-level repository-level explanation of what "agents" (AI assistants, CI bots, Dependabot, etc.) are used, expectations when they make changes, review practices, and a short checklist for maintainers when accepting agent-generated changes.
- Content: See exact contents below (Markdown). The file should include sections: Purpose, Which agents we use, How we treat agent contributions, Review checklist, Security & secrets, Contact / Questions.



## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
