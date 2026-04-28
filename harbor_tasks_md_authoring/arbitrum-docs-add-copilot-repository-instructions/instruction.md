# Add Copilot repository instructions

Source: [OffchainLabs/arbitrum-docs#3238](https://github.com/OffchainLabs/arbitrum-docs/pull/3238)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Description

Adds `.github/copilot-instructions.md` so GitHub Copilot (cloud agent, code review, and IDE) has repo-specific context. Without it, Copilot guesses at our conventions and reviewers end up correcting the same issues on every PR.

The file encodes what the existing `PR_REVIEW_RUBRIC` (derived from 6,852 review comments across 1,181 PRs) flags most often:

- Ordered build / format / typecheck / lint commands matching `build.yml`, `main.yml`, and `test.yml`.
- Pre-commit hook behavior, Node `22.x` pin, `docs/sdk/**` is auto-generated.
- Content-tree map of `docs/` and the standard + glossary frontmatter shapes.
- House-style rules: sentence-case, descriptive link text, `:::` admonitions (not `> [!NOTE]`), `parent chain` / `child chain` over `L1` / `L2`, Orbit vs. Arbitrum chain distinction, actor distinctions.
- The four-step checklist when moving or renaming a page (`sidebars.js`, `vercel.json`, internal links, `i18n/` mirrors).

## Document type

- [x] Codebase changes

## Checklist

- [x] Passes `yarn prettier --check`
- [x] Passes `yarn markdownlint`
- [x] No content changes under `docs/`
- [x] No sidebar, redirect, or navigation impact

## Additional notes

Kept under ~2 pages per GitHub's guidance for Copilot instructions files. The "trust these instructions" closer tells Copilot not to re-explore the repo unless something here is wrong or missing.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
