# fix: update cursorrules detailing efficient patterns, function complexity & design

Source: [recallnet/js-recall#1168](https://github.com/recallnet/js-recall/pull/1168)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/api-specific-config.mdc`
- `.cursor/rules/org-general-practices.mdc`
- `.cursor/rules/org-typescript-standards.mdc`

## What to add / change

# Cursor Rules Enhancement Based on PR Feedback

## Overview

Updated organization-wide cursor rules to codify code quality patterns. These changes ensure future development naturally follows best practices for code readability, efficiency, and maintainability.

## Changes by File

### 1. `.cursor/rules/org-general-practices.mdc`

**Added two new sections:**

#### Function Design & Complexity Management
- Extract helper methods when functions exceed ~30-40 lines or have distinct logical sections
- Single responsibility principle: Each function should do ONE thing well
- Fail-fast pattern: Check error conditions early and return immediately
- Avoid redundant checking across different functions
- Clear method contracts: Helper names should indicate their assumptions

#### Efficient Code Patterns
- Don't compute what you don't need: Avoid building intermediate data structures just to check properties
- Choose appropriate loops: Use `for` when iteration count is known, `while` for conditional iteration
- Early exit strategies: Prefer `.some()`, `.every()`, `.find()` over `.filter().length` or `.map()` when you just need a boolean
- Separation of concerns: Separate detailed logging from control flow logic

### 2. `.cursor/rules/org-typescript-standards.mdc`

**Added new section: Code Efficiency Patterns**

#### Array Method Selection
- Use `.some()` to check if ANY element matches (stops on first match)
- Use `.every()` to check if ALL elements match

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
