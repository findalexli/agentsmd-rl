# [Agents] Update agents to make sure do linting.

Source: [SeleniumHQ/selenium#17366](https://github.com/SeleniumHQ/selenium/pull/17366)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.local.md`
- `CLAUDE.md`
- `dotnet/AGENTS.md`
- `java/AGENTS.md`
- `javascript/selenium-webdriver/AGENTS.md`
- `py/AGENTS.md`
- `rb/AGENTS.md`
- `rust/AGENTS.md`

## What to add / change

### 🔗 Related Issues
<!-- Example: Fixes #1234 or Closes #5678 -->
<!-- If the reason for this PR is not obvious, consider creating an issue for it first -->

### 💥 What does this PR do?
<!-- Describe what this change includes and how it works -->
Agents have a bad habit of doing things which don't align with our formatting rules. This change updates the agents to make sure they follow the rules and as added extra run `./go format` as that will clean up.

### 🔧 Implementation Notes
<!--- Why did you implement it this way? -->
<!--- What alternatives to this approach did you consider? -->

### 💡 Additional Considerations
<!--- Are there any decisions that need to be made before accepting this PR? -->
<!--- Is there any follow-on work that needs to be done? (e.g., docs, tests, etc.) -->

### 🔄 Types of changes
<!-- ✂️ Please delete anything that doesn't apply -->
- Agent Changes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
