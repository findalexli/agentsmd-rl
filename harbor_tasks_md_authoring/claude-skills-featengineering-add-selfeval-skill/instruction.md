# feat(engineering): add self-eval skill

Source: [alirezarezvani/claude-skills#436](https://github.com/alirezarezvani/claude-skills/pull/436)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering/self-eval/SKILL.md`

## What to add / change

## Summary

Adds a self-eval skill for honest AI work quality evaluation. Uses a two-axis scoring system (ambition × execution) with a fixed composite matrix, mandatory devil's advocate reasoning, and cross-session score persistence that enables real anti-inflation detection.

Born from 60+ runs of autonomous agent self-evaluation where we discovered that without structural anti-inflation mechanisms, AI self-assessment converges to "everything is a 4."

**Key mechanisms:**
- Two independent axes: task ambition (Low/Medium/High) and execution quality (Poor/Adequate/Strong)
- Fixed scoring matrix that the model cannot override — Low ambition caps at 2/5 regardless of execution
- Mandatory devil's advocate: must argue for both higher AND lower scores before finalizing
- Score persistence to `.self-eval-scores.jsonl` — flags clustering when 4+ of last 5 scores are identical

## Checklist

- [x] **Target branch is `dev`** (not `main`)
- [x] Skill has `SKILL.md` with valid YAML frontmatter (`name`, `description`, `license`)
- [x] Scripts (if any) run with `--help` without errors — N/A, prompt-only skill
- [x] No hardcoded API keys, tokens, or secrets
- [x] No vendor-locked dependencies without open-source fallback
- [x] Follows existing directory structure (`engineering/self-eval/SKILL.md`)

## Type of Change

- [x] New skill

## Testing

- Tested by installing to `~/.claude/skills/self-eval/SKILL.md` and invoking `/self-eval` in Claude Code sessions
- Scoring matrix verified again

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
