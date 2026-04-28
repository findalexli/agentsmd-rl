# chore: add Claude Code skills for debugging and testing

Source: [genlayerlabs/genlayer-studio#1407](https://github.com/genlayerlabs/genlayer-studio/pull/1407)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/argocd-debug/SKILL.md`
- `.claude/skills/discord-community-feedback/SKILL.md`
- `.claude/skills/hosted-studio-debug/SKILL.md`
- `.claude/skills/integration-tests/SKILL.md`

## What to add / change

# What

- Renamed `argocd-debug` skill to `hosted-studio-debug` with enhanced multi-replica log aggregation support
- Added `discord-community-feedback` skill for monitoring Discord channel for user-reported bugs
- Updated `integration-tests` skill with improved workflow and `--leader-only` flag for faster execution

# Why

- **hosted-studio-debug**: Production environment has 4 consensus workers and 2 JSON-RPC replicas. The skill now documents how to get logs from all replicas and includes a full status check workflow.
- **discord-community-feedback**: Enables monitoring the GenLayer Discord community for user-reported issues, with integration to cross-reference with hosted studio logs.
- **integration-tests**: Clearer step-by-step workflow (start studio → setup venv → run tests) and documents the `--leader-only` flag for faster test execution.

# Testing done

- Verified skill files are valid markdown with proper frontmatter
- Confirmed skill names and descriptions are accurate

# Decisions made

- Discord skill requires external MCP server setup ([discordmcp](https://github.com/v-3/discordmcp)) - documented in prerequisites
- Included production replica counts (4 consensus workers, 2 JSON-RPC) in hosted-studio-debug for reference

# Checks

- [x] I have tested this code
- [x] I have reviewed my own PR
- [ ] I have created an issue for this PR
- [x] I have set a descriptive PR title compliant with conventional commits

# Reviewing tips

- Skills are in `.claude/skills/` dir

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
