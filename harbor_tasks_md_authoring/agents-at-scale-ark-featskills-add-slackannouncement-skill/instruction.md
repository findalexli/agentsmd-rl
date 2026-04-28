# feat(skills): add slack-announcement skill

Source: [mckinsey/agents-at-scale-ark#1954](https://github.com/mckinsey/agents-at-scale-ark/pull/1954)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/slack-announcement/SKILL.md`

## What to add / change

## Summary

Adds a Claude Code skill at `.claude/skills/slack-announcement/SKILL.md` that codifies the process for producing themed Slack posts announcing Ark releases.

The skill:

- Pulls releases from **both** the core repo (`mckinsey/agents-at-scale-ark`) and the Marketplace (`mckinsey/agents-at-scale-marketplace`).
- Filters out ops/CI/test-infra noise (CVEs, dependabot, flaky-test fixes, release-please plumbing).
- Derives docs links per feature by inspecting the PR's file diff for changed `docs/content/**/*.mdx` or component `README.md` files, then mapping the source path to its published URL.
- Validates linked URLs by confirming the source MDX still exists on `main` (curl-on-the-rendered-site is unreliable for Next.js SPA shells).
- Blocklists generic pages (currently `/user-guide/dashboard/`) so bullets pick a more specific page or drop the link.
- Hoists shared docs links to the section heading when multiple bullets point to the same page, avoiding link repetition.
- Groups features into eight fixed themes (Protocol & core runtime → CLI & dev experience).
- Writes user-benefit bullets, not changelog restatements.
- Surfaces breaking changes from `docs/content/reference/upgrading.mdx` commits in the window, plus a fallback scan for conventional-commit `!:` markers.
- Ends with a **Coming next** section sourced from the currently-active iteration on the ARK GitHub Project (iteration field `Sprint`, project number 10) via a GraphQL query.

No code changes, no runtime 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
