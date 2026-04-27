# chore(skills): better diagnostic advice

Source: [biomejs/biome#9830](https://github.com/biomejs/biome/pull/9830)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/diagnostics-development/SKILL.md`
- `.claude/skills/lint-rule-development/SKILL.md`

## What to add / change

<!--
  IMPORTANT!!
  If you generated this PR with the help of any AI assistance, please disclose it in the PR.
  https://github.com/biomejs/biome/blob/main/CONTRIBUTING.md#ai-assistance-notice
-->

<!--
	Thanks for submitting a Pull Request! We appreciate you spending the time to work on these changes.
	Please provide enough information so that others can review your PR.
	Once created, your PR will be automatically labeled according to changed files.
	Learn more about contributing: https://github.com/biomejs/biome/blob/main/CONTRIBUTING.md
-->

## Summary

<!-- Explain the **motivation** for making this change. What existing problem does the pull request solve?-->
Based on recent PR feedback i've gotten and had to give.

<!-- Link any relevant issues if necessary or include a transcript of any Discord discussion. -->

<!-- If you create a user-facing change, please write a changeset: https://github.com/biomejs/biome/blob/main/CONTRIBUTING.md#writing-a-changeset (your changeset is often a good starting point for this summary as well) -->

## Test Plan

<!-- What demonstrates that your implementation is correct? -->
gonna see if the agent does a better job

## Docs

<!-- If you're submitting a new rule or action (or an option for them), the documentation is part of the code. Make sure rules and actions have example usages, and that all options are documented. -->

<!-- For other features, please submit a documentation PR to the `next` branch of our website: https://github.com/

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
