# Update CLAUDE.md

Source: [screenpipe/screenpipe#3108](https://github.com/screenpipe/screenpipe/pull/3108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

---
name: pull request
about: submit changes to the project
title: "[pr] "
labels: ''
assignees: ''

---

## description

brief description of the changes in this pr.

related issue: #

## how to test

add a few steps to test the pr in the most time efficient way.

1. 
2. 
3. 

if relevant add screenshots or screen captures to prove that this PR works to save us time (check [Cap](https://cap.so)).

if you are not the author of this PR and you see it and you think it can take more than 30 mins for maintainers to review, we will tip you between $20 and $200 for you to review and test it for us.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
