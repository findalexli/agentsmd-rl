# Update AGENTS.md

Source: [AMReX-Codes/amrex#5304](https://github.com/AMReX-Codes/amrex/pull/5304)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

- reorganize AGENTS.md into a tighter field-manual-style structure
  - consolidate build/test instructions into one reference section
  - convert operating guidance into concise hard rules with AI safety notes
  - keep task playbooks but point them to the shared build reference

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
