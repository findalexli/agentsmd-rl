# Add AGENTS.md file

Source: [BLAST-WarpX/warpx#6482](https://github.com/BLAST-WarpX/warpx/pull/6482)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

For LLM-based coding assistants, it has become standard practice to have a file named [`AGENTS.md`](https://agents.md/) that contains project-specific rules. (For instance, Cursor [automatically reads](https://cursor.com/docs/context/rules#agentsmd) this file. So does [Codex](https://developers.openai.com/codex/guides/agents-md/))

The file is concise (~100 lines) and focuses on what an AI assistant needs to be productive: build/test commands, architectural "big picture", and project-specific conventions.

The current file in this PR has been largely written by Claude code, using the [`\init` command](https://code.claude.com/docs/en/best-practices#write-an-effective-claude-md), whose function is to explore the code base and write a corresponding `.md` file.

As an example rule, since most of the developers use `conda` environments, and create the environment `warpx-cpu-mpich-dev` as per the [installation instructions](https://warpx.readthedocs.io/en/latest/install/cmake.html#install-with-conda-forge), I added the a rule to activate this environment to compile WarpX. This solves the following issue:

- **Without AGENTS.md:** Cursor does not know in which environment to run requests, and thus fails to find `cmake`:
<img width="402" height="209" alt="Screenshot 2026-01-11 at 6 43 56 AM" src="https://github.com/user-attachments/assets/04662561-4951-4b6c-9e16-be6dc5eaf265" />

- **With AGENTS.md:** Cursor is able to use the correct environment:
<img width="421" height=

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
