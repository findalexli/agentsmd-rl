# fix(create-agent-skills): remove literal dynamic context directives that break skill loading

Source: [EveryInc/compound-engineering-plugin#252](https://github.com/EveryInc/compound-engineering-plugin/pull/252)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/create-agent-skills/SKILL.md`

## What to add / change

## Problem

The `create-agent-skills` skill fails to load via the Skill tool with:

```
Bash command failed for pattern "!`command`": (eval):1: redirection with no command
```

### Root cause

The SKILL.md file contained literal `!`command`` dynamic context injection directives as documentation examples (lines 100, 111–112). Claude Code's preprocessor scans the **entire** SKILL.md as plain text before sending it to the model — it does not parse markdown. Fenced code blocks (` ```yaml `) and inline code spans (`` `` ``) offer **no protection** from execution.

When loading this skill, the preprocessor attempted to execute three directives:
1. `` !`command` `` → shell error (`command` is not a valid command)
2. `` !`gh pr diff` `` → fails outside a PR context
3. `` !`gh pr diff --name-only` `` → same

This caused the skill to fail on every invocation, forcing Claude to fall back to manually reading the SKILL.md file — losing the benefits of skill-based loading.

### Upstream references

- [anthropics/claude-code#27149](https://github.com/anthropics/claude-code/issues/27149) — "Preprocessor executes `!`command`` directives inside markdown code spans" (closed, wontfix). Resolution: *"The double backtick escaping was broken, so the content was never actually inside a code span. The preprocessor was correctly executing bare text. Workaround: describe the syntax in prose instead of using the literal syntax."*
- [anthropics/claude-code#28024](https://github.com/anthropics/claude-code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
