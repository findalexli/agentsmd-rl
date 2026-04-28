# 添加独立 SKILL.md，兼容 skills.sh 和 clawhub.ai 平台

Source: [star23/Day1Global-Skills#4](https://github.com/star23/Day1Global-Skills/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

从 zip 内 767 行原版精简至 286 行，保留完整 16 模块框架、
6 大投资哲学、估值矩阵、反偏见框架和决策输出模板，
通过 progressive disclosure 引用 references/ 详细文件。

https://claude.ai/code/session_01SjBQfRh6amw1qofqP4VfNX

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
