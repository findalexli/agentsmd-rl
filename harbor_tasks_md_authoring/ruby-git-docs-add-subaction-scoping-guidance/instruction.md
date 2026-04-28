# docs: add sub-action scoping guidance to command skills

Source: [ruby-git/ruby-git#1202](https://github.com/ruby-git/ruby-git/pull/1202)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/command-implementation/REFERENCE.md`
- `.github/skills/review-arguments-dsl/CHECKLIST.md`

## What to add / change

## Summary

When a git command is split into sub-command classes (e.g., `Branch::Create` vs. `Branch::List`), each class should only include options that apply to its specific sub-action — not every option on the man page. The existing skills had no guidance for this, so an agent following the "enumerate every option" rule literally could add options like `--sort`, `--format`, or `--merged` to `Branch::Create`, which would be incorrect.

## Changes

### `command-implementation` REFERENCE.md

- Expanded the options-completeness decision table from 2 rows to 3, adding **"Exclude (wrong sub-action)"** between Include and Exclude (execution-model conflict)
- Added new **"Scoping options to sub-command classes"** subsection with:
  - 3-step process: read SYNOPSIS, cross-reference DESCRIPTION/OPTIONS, identify shared options
  - Example table showing `git branch` option distribution across Create/List/Delete/Move modes
  - Clarification that this rule only applies to split commands
- Updated table of contents

### `review-arguments-dsl` CHECKLIST.md

- Added new **"Options excluded because they belong to a different sub-action"** subsection in §1 (Determine scope and exclusions), before the existing execution-model exclusions
  - Same 3-step process in condensed form
  - Clarification that single-class commands are unaffected
- Updated table of contents

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
