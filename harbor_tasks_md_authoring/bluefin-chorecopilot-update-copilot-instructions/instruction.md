# chore(copilot): update copilot instructions

Source: [ublue-os/bluefin#3505](https://github.com/ublue-os/bluefin/pull/3505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- Remove Fedora 41 references (being removed tomorrow)
- Change GTS from 'Go-To-Stable' to 'Grand Touring Support'
- Update all Fedora version examples to only show 42/43
- Update stream tag descriptions to reflect F42 for stable/gts

<!--

## Thank you for contributing to the Universal Blue project!

Please [read the Contributor's Guide](https://docs.projectbluefin.io/contributing) before submitting a pull request.

-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
