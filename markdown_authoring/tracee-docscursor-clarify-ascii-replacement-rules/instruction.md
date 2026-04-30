# docs(cursor): clarify ASCII replacement rules

Source: [aquasecurity/tracee#5290](https://github.com/aquasecurity/tracee/pull/5290)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/shell-style-guide.mdc`
- `.cursor/rules/text-ascii-safety.mdc`

## What to add / change

### 1. Explain what the PR does

0bb1fb4d6 **docs(cursor): clarify ASCII replacement rules**

> Separate bullets and arrows into distinct replacement
> items with specific guidance for each. Fix extra space
> in shell style guide comment.

--

### 2. Explain how to test it

<!--
Maintainer will review the code, and test the fix/feature, how to run Tracee ?
Give a full command line example and what to look for.
-->

### 3. Other comments

<!--
Links? References? Anything pointing to more context about the change.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
