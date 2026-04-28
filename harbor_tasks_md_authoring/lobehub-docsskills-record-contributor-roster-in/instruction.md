# 📝 docs(skills): record contributor roster in version-release

Source: [lobehub/lobehub#14219](https://github.com/lobehub/lobehub/pull/14219)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/version-release/SKILL.md`

## What to add / change

## Summary

Captures the contributor-section conventions surfaced during the v2.1.53 weekly release writeup so future runs of `/version-release` produce the same output without back-and-forth.

- Add a **Contributor Ordering** section with the canonical LobeHub team roster (10 handles) and a flat-list rule (community first, team after, sorted by PR count desc).
- Note the git-author-name vs GitHub-handle pitfall (e.g. `YuTengjing` → `@tjx666`) and how to resolve it via `gh pr view <PR> --json author` / `gh api search/users`.
- Update the changelog template: drop commits count from both the metadata and contributors lines; reword the contributors intro to a `Huge thanks to N contributors who shipped N merged PRs` pattern.

## Test plan

- [x] Skill markdown renders cleanly (Markdown lint via prettier hook passes)
- [ ] Next weekly release uses the new conventions without manual nudging

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
