# fix(apm-review-panel): restore in-context persona model (per agentskills.io)

Source: [microsoft/apm#908](https://github.com/microsoft/apm/pull/908)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.apm/skills/apm-review-panel/SKILL.md`
- `.github/skills/apm-review-panel/SKILL.md`

## What to add / change

## Problem

PR #907 added a 'do not delegate' clause for emission, but the panel still fails. Run [24899623301](https://github.com/microsoft/apm/actions/runs/24899623301?pr=889): **2 personas (Growth Hacker, Supply Chain) posted their findings as separate comments via `safeoutputs-add_comment`**, no synthesized CEO verdict. Earlier run 24897368527: zero comments.

## Root cause

The user noted: **the panel was working way better before #882**. Confirmed via git history.

PR #882 changed the skill from a clean progressive-disclosure model into a sub-agent dispatch model:

- *'Do not open linked persona files in the orchestrator thread.'*
- *'Dispatch one sub-agent per persona via the task tool.'*

This breaks two ways:

1. **Sub-agents launched via the `task` tool inherit the parent's MCP gateway** -- including `safeoutputs`. They will happily call `safeoutputs-add_comment` themselves. The 'instruct each sub-agent: do not post' clause from #905 was lossy guidance, not enforcement. Result: per-persona comment spam.

2. **The orchestrator hangs waiting on background sub-agents.** It frequently times out before all 5 return, and the session ends without ever reaching CEO arbitration or single-comment emission.

## Per agentskills.io

> Agents load skills through **progressive disclosure**, in three stages:
> 1. **Discovery**: load only the name and description
> 2. **Activation**: read the full `SKILL.md` instructions into context
> 3. **Execution**: follow the instructions, opti

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
