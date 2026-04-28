# github: add US English check to copilot-instructions.md

Source: [canonical/lxd#18133](https://github.com/canonical/lxd/pull/18133)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Per Canonical style guidelines, all user-facing copy should use US English instead of UK English. This should be reflected not only in documentation but in CLI output and any other text shown to users. This PR adds reinforcement of this to `copilot-instructions.md` for future PR reviews.

## Checklist

- [x] I have read the [contributing guidelines](https://github.com/canonical/lxd/blob/main/CONTRIBUTING.md) and attest that all commits in this PR are [signed off](https://github.com/canonical/lxd/blob/main/CONTRIBUTING.md#including-a-signed-off-by-line-in-your-commits), [cryptographically signed](https://github.com/canonical/lxd/blob/main/CONTRIBUTING.md#commit-signature-verification), and follow this project's [commit structure](https://github.com/canonical/lxd/blob/main/CONTRIBUTING.md#commit-structure).
- [x] I have checked and added or updated relevant documentation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
