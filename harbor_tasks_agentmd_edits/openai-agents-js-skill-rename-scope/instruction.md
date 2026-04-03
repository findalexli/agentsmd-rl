# Rename and Scope the Verification Skill, Add OpenAI Knowledge Skill

## Problem

The repository's `.codex/skills/verify-changes` skill currently runs the full verification stack (install, build, lint, type-check, test) on **every** change, including documentation-only edits. This wastes time and creates unnecessary friction. The skill's name (`verify-changes`) is also too generic — it doesn't convey that it's specifically for **code** changes.

Additionally, there is no skill to help contributors look up authoritative OpenAI API documentation when working on platform integrations in this repo.

## What Needs to Change

1. **Rename the skill**: Move `.codex/skills/verify-changes/` to a more descriptive name that reflects its purpose of verifying **code** changes specifically. Update all internal references (SKILL.md frontmatter, script output messages) to match.

2. **Scope the skill**: The skill's description and documentation should make clear that it applies when changes affect runtime code, tests, or build/test configuration — not for docs-only or repo-meta changes.

3. **Add a new skill**: Create an OpenAI knowledge skill under `.codex/skills/` that guides contributors to use the OpenAI Developer Documentation MCP server (`openaiDeveloperDocs`) for looking up API docs, schemas, and platform features. Include setup instructions for when the MCP server isn't configured.

4. **Update AGENTS.md**: The Mandatory Skill Usage section and all references to the old skill name must be updated. Document when to run (and when to skip) the verification skill. Add a section for the new knowledge skill.

## Files to Look At

- `.codex/skills/verify-changes/` — the skill to rename (SKILL.md, scripts/run.sh, scripts/run.ps1)
- `AGENTS.md` — contributor guide with mandatory skill usage instructions
