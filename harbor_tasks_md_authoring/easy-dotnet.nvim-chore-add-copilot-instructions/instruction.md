# chore: add copilot instructions

Source: [GustavEikaas/easy-dotnet.nvim#879](https://github.com/GustavEikaas/easy-dotnet.nvim/pull/879)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

I started trying out copilot in this repository and it keeps struggling so I thought ill attempt to add copilot instructions. This file doesnt tell users all that much but the instructions file in server does actually help contributors in understanding the architecture I think

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
