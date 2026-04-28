# docs(claude): grant agents feature-branch autonomy, keep master guardrail

Source: [FastLED/FastLED#2294](https://github.com/FastLED/FastLED/pull/2294)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Agents were leaving uncommitted changes dangling on `master` because the old rule only said "never commit to master" without telling them where changes *should* go.
- Rewrites the Git and Code Publishing section of `CLAUDE.md`:
  - **Default mindset:** finish the job — never leave a dirty `master`.
  - **Feature branches:** full autonomy to commit, push, and open PRs without user consent.
  - **`master`/`main`:** extra caution — never commit, push, or force-push directly.
  - Adds an explicit **recovery pattern** for the common case: `git checkout -b <branch>` carries working-tree changes off `master` cleanly.

Motivating example: sibling PR #2293 (autoresearch `--frames`) was dangling as uncommitted changes on `master` until an agent recovered it using the new pattern documented here.

## Test plan
- [ ] Docs-only change — no build/test impact
- [ ] Review the new language in `CLAUDE.md` for clarity

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated development guidelines to clarify repository management practices for `master`/`main` branches and feature branch workflows, including enhanced safety requirements and step-by-step remediation procedures for repository state management.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
