# Forbid pushing to origin in AGENTS.md

Source: [isaac-sim/IsaacLab#5344](https://github.com/isaac-sim/IsaacLab/pull/5344)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# Description

The origin remote points to the public isaac-sim/IsaacLab repo. Agents and contributors should push to their own fork remote or to the remote of the PR they are working on instead.

## Type of change

- Documentation update

## Checklist

- [ ] I have read and understood the [contribution guidelines](https://isaac-sim.github.io/IsaacLab/main/source/refs/contributing.html)
- [ ] I have run the [`pre-commit` checks](https://pre-commit.com/) with `./isaaclab.sh --format`
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have updated the changelog and the corresponding version in the extension's `config/extension.toml` file
- [ ] I have added my name to the `CONTRIBUTORS.md` or my name already exists there

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
