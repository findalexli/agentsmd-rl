# Add machine-readable skill index to root SKILL.md

Source: [austintgriffith/ethskills#19](https://github.com/austintgriffith/ethskills/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Fixes #18

AI agents fetching `/SKILL.md` could not discover sub-skill URLs because the homepage renders links via JavaScript. Bots using `web_fetch`/`curl` got `href="#"` and had to guess paths — often wrong (`/why-ethereum/` instead of `/why/`, `/money-legos/` instead of `/building-blocks/`).

Adds a discoverable index at the top of `SKILL.md` with direct URLs to all 9 sub-skills, plus the onchain terminology note. The full concatenated content follows below the index.

Now any bot can `fetch("https://ethskills.com/SKILL.md")` and immediately find every skill path.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
