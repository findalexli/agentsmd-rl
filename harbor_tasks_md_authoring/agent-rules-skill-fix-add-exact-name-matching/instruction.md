# fix: add exact name matching and command verification requirements

Source: [netresearch/agent-rules-skill#5](https://github.com/netresearch/agent-rules-skill/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agents/SKILL.md`

## What to add / change

## Summary

Adds stricter verification requirements for AGENTS.md accuracy based on learnings from t3x-cowriter comprehensive review.

## Problem Discovered

During t3x-cowriter review, we found AGENTS.md files with:
- **Wrong controller name**: Documented `CowriterAjaxController.php` but actual file was `AjaxController.php`
- **Non-existent make targets**: Documented `make test-mutation` and `make phpstan` but neither existed (actual was `make typecheck`)
- **PHPStan level mismatch**: Root AGENTS.md said level 8, Classes/AGENTS.md said level 10

These mismatches caused agents to fail when trying to use documented information.

## Changes

Added to verification requirements:
- File names must match **exactly**, not just exist
- Numeric values (PHPStan level, coverage %) must come from actual config files
- Commands must be **tested** before documenting (not just grepped)
- Real-world examples showing the problems and correct approach

## Checklist

- [x] Follows skill documentation standards
- [x] Real-world example included
- [x] Actionable verification commands provided

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
