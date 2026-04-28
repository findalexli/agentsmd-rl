# libcu++ Style `SKILL.md`

Source: [NVIDIA/cccl#8019](https://github.com/NVIDIA/cccl/pull/8019)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/licudacxx-style/SKILL.md`
- `.claude/skills/licudacxx-style/SKILL.md`

## What to add / change

## Description

After experimenting for a while, I created this PR to propose the first `SKILL.md` for CCCL.

The SKILL targets the high-level coding "style" of libcu++. 

Tested mostly with Claude, the agent was able to follow most of the rules at first attempt. When it was unable to do so, I used the failure to improve the skill.

Unfortunately, Codex and Claude use two different directories for skills. I'm not sure if there is a general solution that can address the problem on both Linux and Windows.

My aspiration for the future is to prevent CI errors in non-standard cases (e.g. old GCC and MSVC) by explaining how to address them before the code is pushed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
