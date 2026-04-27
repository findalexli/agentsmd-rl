# docs: AGENTS.md section on goose2 desktop backend architecture

Source: [aaif-goose/goose#8732](https://github.com/aaif-goose/goose/pull/8732)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ui/goose2/AGENTS.md`

## What to add / change

Addresses #8699

In the goose2 AGENTS.md this replaces the "Backend Architecture" section with a fuller "Architecture" section that (1) states the single communication path explicitly, (2) walks through the skills-as-sources PR as a canonical worked example, (3) calls out the typed SDK methods as the preferred shape with `extMethod` as an escape hatch, (4) enumerates the narrow cases where `invoke()` is still correct, and (5) lists the specific anti-patterns to avoid. The goal is that an agent picking up a new feature has enough guidance to structure it correctly given the still mixed state of client <-> server interactions in goose2.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
