# [py] Add in rules to agents around python 3.10+

Source: [SeleniumHQ/selenium#17102](https://github.com/SeleniumHQ/selenium/pull/17102)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `py/AGENTS.md`

## What to add / change

This tells the agent to favour union types instead of notation. Also telling it to explicitly check the python version locally when running things in the terminal

<!-- Thanks for Contributing to Selenium! -->
<!-- Please read our contribution guidelines: https://github.com/SeleniumHQ/selenium/blob/trunk/CONTRIBUTING.md -->

### 🔗 Related Issues
<!-- Example: Fixes #1234 or Closes #5678 -->
<!-- If the reason for this PR is not obvious, consider creating an issue for it first -->

### 💥 What does this PR do?
Updates the rules for agents that are working on this code base in the python part of the tree

### 🔧 Implementation Notes
<!--- Why did you implement it this way? -->
<!--- What alternatives to this approach did you consider? -->

### 💡 Additional Considerations
<!--- Are there any decisions that need to be made before accepting this PR? -->
<!--- Is there any follow-on work that needs to be done? (e.g., docs, tests, etc.) -->
Nope

### 🔄 Types of changes
<!-- ✂️ Please delete anything that doesn't apply -->
- Cleanup (formatting, renaming)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
