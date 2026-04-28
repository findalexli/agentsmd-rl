# Add UI instructions to AGENTS.md

Source: [tensorzero/tensorzero#3670](https://github.com/tensorzero/tensorzero/pull/3670)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- ELLIPSIS_HIDDEN -->



> [!IMPORTANT]
> Add UI modification instructions to `AGENTS.md`.
> 
>   - **Documentation**:
>     - Adds a new `# UI` section to `AGENTS.md`.
>     - Instructs to run `pnpm run format`, `pnpm run lint`, `pnpm run typecheck` from `ui/` directory after UI code changes.
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=tensorzero%2Ftensorzero&utm_source=github&utm_medium=referral)<sup> for 503607999d8322b13af0e70c7f265ac48bfe6941. You can [customize](https://app.ellipsis.dev/tensorzero/settings/summaries) this summary. It will automatically update as commits are pushed.</sup>

<!-- ELLIPSIS_HIDDEN -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
