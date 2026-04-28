# [Internal] Update AGENTS.md

Source: [huggingface/huggingface_hub#4110](https://github.com/huggingface/huggingface_hub/pull/4110)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR updates `AGENTS.md` with instructions that I usually give to my local Claude. I think they can be relevant to everyone else.

In particular:
- adding specifics about how to deal with the CLI since it's one of the main focus at the moment. Especially:
  - mention `out.xxx` in detail and nudge the agent to add some nice `out.hints` to new commands
  - do not try/catch errors in most cases
  - update CLI guide + CLI package reference + any relate guide
  - CLI tests should not cover everything, just the main use cases
- some instructions around PRs and commit messages (casual, explicit [Topic] in title, etc.)

I also removed parts that felt useless for an AGENTS.md or not relevant for what we work on at the moment.

Any suggestion welcome!

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk: documentation-only changes that do not affect runtime behavior. Risk is limited to potentially incorrect guidance for future contributors.
> 
> **Overview**
> Updates `AGENTS.md` to emphasize **CLI-focused development conventions**, including how to structure Typer command groups, reuse standard option types, and use the `out` output helpers (including confirmations and hints).
> 
> Adds contribution guidance around **destructive operations**, user-facing error handling via `CLIError`, generated CLI docs regeneration, minimal CLI test expectations, and new conventions for **commit/PR titles and descriptions**, plus general Python 3.10+ style recommendations.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
