# feat(skills): add blueprint skill for multi-session construction planning

Source: [affaan-m/everything-claude-code#374](https://github.com/affaan-m/everything-claude-code/pull/374)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/blueprint/SKILL.md`

## What to add / change

## Summary

Adds the [Blueprint](https://github.com/antbotlab/blueprint) skill to the skills collection.

## Type

- [x] Skill

## What Blueprint Does

Blueprint turns a one-line objective into a step-by-step construction plan that any coding agent can execute cold. It's purpose-built for multi-session, multi-agent engineering projects — the kind that are too large for a single Claude Code session.

**Key differentiators:**

- **Cold-start execution**: Every step includes a self-contained context brief. A fresh agent in a new session can execute any step without reading prior steps or conversation history.
- **Adversarial review gate**: Every plan is reviewed by a strongest-model sub-agent (e.g., Opus) against a checklist covering completeness, dependency correctness, cold-start viability, and anti-pattern detection.
- **Zero runtime risk**: Pure markdown skill — no hooks, no shell scripts, no executable code. No `PreToolUse`/`PostToolUse` hooks that run on every tool call. What you install is what you read.
- **Branch/PR/CI workflow**: Built into every step. Detects git/gh availability and degrades gracefully to direct mode when absent.
- **Plan mutation protocol**: Steps can be split, inserted, skipped, reordered, or abandoned with formal protocols and an audit trail.
- **Parallel step detection**: Dependency graph identifies steps with no shared files or output dependencies.

## Testing

1. Install: `git clone https://github.com/antbotlab/blueprint.git ~/.claude/skills/blu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
