# H-5877: Add MIR builder testing framework to HashQL skill documentation

Source: [hashintel/hash#8197](https://github.com/hashintel/hash/pull/8197)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/testing-hashql/SKILL.md`
- `.claude/skills/testing-hashql/references/mir-builder-guide.md`

## What to add / change

# Add MIR Builder Testing Support to HashQL Testing Documentation

## 🌟 What is the purpose of this PR?

This PR adds documentation and skill configuration for the MIR Builder testing approach in HashQL. It introduces a new testing strategy for MIR passes that allows programmatic construction of MIR bodies for unit testing.

## 🔍 What does this change?

- Adds MIR Builder to the skill-rules.json description for HashQL testing
- Updates the testing-hashql skill documentation to include MIR Builder as a fourth testing approach
- Adds a comprehensive MIR Builder guide with examples and patterns
- Updates the testing strategy table to include MIR pass unit tests

## 🛡 What tests cover this?

- Documentation changes only, no tests required

## ❓ How to test this?

1. Review the new MIR Builder guide to ensure it provides clear instructions
2. Verify the skill rules correctly identify MIR Builder related keywords and patterns
3. Check that the main skill documentation properly introduces the MIR Builder approach

## Pre-Merge Checklist 🚀

### 🚢 Has this modified a publishable library?

This PR:

- [x] does not modify any publishable blocks or libraries, or modifications do not need publishing

### 📜 Does this require a change to the docs?

The changes in this PR:

- [x] are internal and do not require a docs change

### 🕸️ Does this require a change to the Turbo Graph?

The changes in this PR:

- [x] do not affect the execution graph

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
