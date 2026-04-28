# feat(skills): add /dependabot-fix skill

Source: [axsaucedo/kaos#148](https://github.com/axsaucedo/kaos/pull/148)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/dependabot-fix/SKILL.md`

## What to add / change

Adds a new Copilot CLI skill at `.github/skills/dependabot-fix/SKILL.md` that systematically diagnoses and fixes failing Dependabot PRs.

## Context
Proven out on PR #142 → #147. This skill encodes the repeatable workflow so future Dependabot failures can be addressed with a single `/dependabot-fix <pr-number>` invocation.

## What it does
1. Fetch PR metadata, diff, and failing-check logs
2. Classify root cause via a pattern table (unpinned `@latest`, Node version, artifact name collisions, CRD drift, flakes, etc.)
3. Branch from latest `main` and cherry-pick dependabot commit
4. Apply targeted fix (version pins, CRD regen, etc.)
5. Local validation with narrowest relevant test suite
6. Push replacement PR, monitor CI (rerun-on-flake logic)
7. Merge replacement, close original

## Invariants
- Always branches from latest `main`, never from dependabot branch
- Cherry-picks to preserve authorship
- Uses `./tmp/` for scratch files (per repo convention)
- Conventional-commit style with co-author trailer

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
