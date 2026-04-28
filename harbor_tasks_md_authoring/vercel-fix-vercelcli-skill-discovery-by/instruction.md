# Fix vercel-cli skill discovery by adding description to SKILL.md

Source: [vercel/vercel#14981](https://github.com/vercel/vercel/pull/14981)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/vercel-cli/SKILL.md`

## What to add / change

The npx skills add command requires both name and description fields in the SKILL.md frontmatter. This fixes the "No valid skills found" error when installing the vercel-cli skill.

<!-- VADE_RISK_START -->
> [!NOTE]
> Low Risk Change
>
> This PR adds a description field to SKILL.md frontmatter metadata, which is a documentation-only change with no code logic impact.
> 
> - Adds description field to SKILL.md frontmatter for skill discovery
>
> <sup>Risk assessment for [commit 807f530](https://github.com/vercel/vercel/commit/807f53066904a4f84deca896b6ca614ab6959a6d).</sup>
<!-- VADE_RISK_END -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
