# fix(ce-pr-description): hand off PR body via temp file

Source: [EveryInc/compound-engineering-plugin#581](https://github.com/EveryInc/compound-engineering-plugin/pull/581)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/AGENTS.md`
- `plugins/compound-engineering/skills/ce-pr-description/SKILL.md`
- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

## Summary

Generating a PR description used to tokenize the body twice: once as the skill's returned text, then again when the caller heredoc'd it into `gh pr create/edit`. On large PRs that compounds. Now the skill writes the body to an OS temp file and the caller reads it back with `$(cat "$BODY_FILE")`. Body tokenized once, caller's tool input shrinks to just the path.

Reviewing that commit surfaced a second problem: the new Step 9 grew three bullets of design archaeology (why `mktemp -u`, why not `EOF`, why not the `Write` tool). Every line of `SKILL.md` loads on every invocation, so that archaeology carries forward forever. A new `AGENTS.md` rule, Rationale Discipline, formalizes the principle that drove the cuts so future skill authoring has the guardrail.

## What changed

- **`ce-pr-description` contract moved from `{title, body}` to `{title, body_file}`.** Step 9 writes the composed body via `mktemp -u` + heredoc and prints the path. `mktemp -u` sidesteps Claude Code's `Write` sandbox (which can't touch `/tmp` and refuses to overwrite unread files). The quoted heredoc sentinel keeps `$VAR`, backticks, and literal `EOF` in the body from clashing with the terminator. OS reaps `/tmp` on its own, so no cleanup.

- **`git-commit-push-pr` callers read the body from the returned path.** DU-3 (description-only) and Step 7 (full flow, both new and existing PR) substitute with `$(cat "$BODY_FILE")` inside `gh pr create/edit`. DU-3's compare-and-confirm note explicitly says n

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
