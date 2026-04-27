# feat(git-commit-push-pr): precompute shield badge version via skill preprocessing

Source: [EveryInc/compound-engineering-plugin#464](https://github.com/EveryInc/compound-engineering-plugin/pull/464)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`
- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

Eliminates 5+ second agent delay when resolving the plugin version for the Compound Engineering shield badge in PR descriptions.

**Problem:** The badge section in `git-commit-push-pr` instructed the agent to run `jq` at runtime to read the plugin version from `plugin.json`. This triggered multiple tool calls (env var check, file discovery, jq execution) adding 5+ seconds of overhead every time.

**Fix:** Uses Claude Code's `!`backtick`` dynamic context injection to resolve the version at skill load time — the shell command runs during preprocessing and the output replaces the placeholder before the model sees the content. Zero agent tool calls needed.

For non-Claude Code platforms (Codex, Gemini CLI), the `!` syntax isn't processed, so the agent sees a literal command string, recognizes it's not a version, and uses the versionless badge variant. This is the correct behavior since the version badge is only meaningful in Claude Code's plugin ecosystem.

Also updates the quality checklists in `ce-work` and `ce-work-beta` to drop "and version" from the badge requirement, since version is now conditionally resolved rather than mandatory.

---

[![Compound Engineering](https://img.shields.io/badge/Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
