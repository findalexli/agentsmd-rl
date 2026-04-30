# agent_skills

Source: [DASDAE/dascore#613](https://github.com/DASDAE/dascore/pull/613)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/agents.md`
- `.agents/skills/draft-release/SKILL.md`
- `AGENTS.md`

## What to add / change

## Description

This PR adds an agents file to help coding agents like codex and claude code work effectively on the DASCore code base. It also adds a skill for generating release notes. 

## Checklist

I have (if applicable):

- [ ] referenced the GitHub issue this PR closes.
- [ ] documented the new feature with docstrings and/or appropriate doc page.
- [ ] included tests. See [testing guidelines](https://dascore.org/contributing/testing.html).
- [ ] added the "ready_for_review" tag once the PR is ready to be reviewed.


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive Agent Guide covering scope, contributor workflow, environment setup, linting/formatting, testing and test-authoring conventions, code and documentation standards, uncertainty handling, and quality criteria for agent changes.
  * Introduced a draft-release workflow to determine the next semantic version and generate a categorized changelog from merged PRs.
  * Added a root-level canonical reference instructing agents to load the canonical guide before making changes.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
