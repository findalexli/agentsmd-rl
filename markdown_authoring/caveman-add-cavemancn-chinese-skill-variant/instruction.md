# Add caveman-cn Chinese skill variant

Source: [JuliusBrussee/caveman#37](https://github.com/JuliusBrussee/caveman/pull/37)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `caveman-cn/SKILL.md`
- `plugins/caveman/skills/caveman-cn/SKILL.md`
- `skills/caveman-cn/SKILL.md`

## What to add / change

## Changes
- add a new `caveman-cn` skill for Chinese ultra-compressed communication
- mirror the skill into the repo's three existing distribution paths
- keep the same core guarantees as `caveman`: preserve technical accuracy, code blocks, exact errors, and clear fallback for risky/destructive flows

## Why
The repo currently ships English caveman mode only. This adds a Chinese variant with Chinese-specific compression rules and the same lite/full/ultra intensity model so Chinese-first users can get the same token and readability benefits.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
