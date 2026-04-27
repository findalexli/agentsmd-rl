# Fix the stale automerge claim in the running-tend skill

This repo (`PRQL/prql`) has a Claude Code skill at
`.claude/skills/running-tend/SKILL.md` that documents the CI / PR / issue
conventions an automated maintenance bot ("tend") relies on. Tend reads this
skill to plan its work — bullets in the skill are load-bearing inputs to its
decisions about whether bot PRs will merge, how issues should be closed, etc.

## The problem

Under the `## CI structure` section, the skill currently asserts:

> Automerge: `pull-request-target.yaml` auto-merges single-commit `prql-bot` PRs
> once CI passes

This statement is **stale**. The workflow at
`.github/workflows/pull-request-target.yaml` (in the current state of this
checkout) does not perform automerge. Inspect that workflow file in the repo
to confirm what it actually does — that file is the source of truth.

Because the skill says automerge happens, future tend runs will assume bot PRs
will land on their own once CI is green. They won't, so issues filed by the
bot or single-commit refactor PRs sit open indefinitely.

## What to fix

Edit `.claude/skills/running-tend/SKILL.md` so the `## CI structure` bullet
about automerge accurately describes the workflow's current behavior:

- Make clear that automatic merging is not in effect today (use a phrasing
  like *manual*, *removed*, *no longer*, *not configured*, *must be merged*,
  or *no automerge* — pick whatever reads naturally in the bullet).
- Replace the incorrect description with what the workflow actually does
  today, so a reader of the skill knows the current responsibilities of
  `pull-request-target.yaml`. Read the workflow yourself and reflect it
  faithfully — do not guess.

The fix is documentation-only. Do not change anything else: no edits to the
workflow file, no edits to other sections of the skill (`## PR conventions`,
`## Issue management`), and no changes anywhere outside the skill file.

## Constraints

- Keep the edit focused on the stale automerge bullet inside `## CI structure`.
  Other bullets in that section (`Main CI workflow`, `Dependency management`)
  are correct and should remain.
- Preserve the existing section headings (`## PR conventions`,
  `## CI structure`, `## Issue management`) unchanged.
- Do not duplicate content that already lives in `CLAUDE.md` (build commands,
  test strategy, error conventions). The running-tend skill is intentionally
  scoped to tend-specific PR/CI/issue policy.
- The new wording should be specific enough that a future tend run reading
  the skill will not incorrectly assume bot PRs merge on their own.
