# improve claude tests skills

Source: [RediSearch/RediSearch#8312](https://github.com/RediSearch/RediSearch/pull/8312)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/rust-tests-guidelines/SKILL.md`
- `.skills/write-rust-tests/SKILL.md`

## What to add / change

## Describe the changes in the pull request

Couple of improvements on Claude skills related to tests.

#### Mark if applicable

- [ ] This PR introduces API changes
- [ ] This PR introduces serialization changes

#### Release Notes

- [ ] This PR requires release notes
- [x] This PR does not require release notes

If a release note is required (bug fix / new feature / enhancement), describe the **user impact** of this PR in the title.  

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation-only updates to internal testing guidelines; no production code or runtime behavior changes.
> 
> **Overview**
> Improves the Rust test-writing skill docs to reduce churn and redundant coverage. Adds guidance to avoid referencing exact line numbers in comments, and introduces a new section on *avoiding redundant tests* (focus on unique branches, avoid trivial delegation tests, and remove tests that don’t add new coverage).
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 9b09154e344ad6fd46aca742a6f612c4093003ed. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
