# chore: update uloop skills

Source: [hatayama/unity-cli-loop#999](https://github.com/hatayama/unity-cli-loop/pull/999)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/uloop-clear-console/SKILL.md`
- `.agents/skills/uloop-compile/SKILL.md`
- `.agents/skills/uloop-control-play-mode/SKILL.md`
- `.agents/skills/uloop-execute-dynamic-code/SKILL.md`
- `.agents/skills/uloop-find-game-objects/SKILL.md`
- `.agents/skills/uloop-focus-window/SKILL.md`
- `.agents/skills/uloop-get-hierarchy/SKILL.md`
- `.agents/skills/uloop-get-logs/SKILL.md`
- `.agents/skills/uloop-launch/SKILL.md`
- `.agents/skills/uloop-record-input/SKILL.md`
- `.agents/skills/uloop-record-input/references/deterministic-replay.md`
- `.agents/skills/uloop-replay-input/SKILL.md`
- `.agents/skills/uloop-replay-input/references/deterministic-replay.md`
- `.agents/skills/uloop-run-tests/SKILL.md`
- `.agents/skills/uloop-screenshot/SKILL.md`
- `.agents/skills/uloop-screenshot/references/annotated-elements.md`
- `.agents/skills/uloop-simulate-keyboard/SKILL.md`
- `.agents/skills/uloop-simulate-mouse-input/SKILL.md`
- `.agents/skills/uloop-simulate-mouse-ui/SKILL.md`
- `.claude/skills/uloop-clear-console/SKILL.md`
- `.claude/skills/uloop-compile/SKILL.md`
- `.claude/skills/uloop-control-play-mode/SKILL.md`
- `.claude/skills/uloop-execute-dynamic-code/SKILL.md`
- `.claude/skills/uloop-execute-menu-item/SKILL.md`
- `.claude/skills/uloop-find-game-objects/SKILL.md`
- `.claude/skills/uloop-focus-window/SKILL.md`
- `.claude/skills/uloop-get-hierarchy/SKILL.md`
- `.claude/skills/uloop-get-logs/SKILL.md`
- `.claude/skills/uloop-launch/SKILL.md`
- `.claude/skills/uloop-record-input/SKILL.md`
- `.claude/skills/uloop-record-input/references/deterministic-replay.md`
- `.claude/skills/uloop-replay-input/SKILL.md`
- `.claude/skills/uloop-replay-input/references/deterministic-replay.md`
- `.claude/skills/uloop-run-tests/SKILL.md`
- `.claude/skills/uloop-screenshot/SKILL.md`
- `.claude/skills/uloop-screenshot/references/annotated-elements.md`
- `.claude/skills/uloop-simulate-keyboard/SKILL.md`
- `.claude/skills/uloop-simulate-mouse-input/SKILL.md`
- `.claude/skills/uloop-simulate-mouse-ui/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
