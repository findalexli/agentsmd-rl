# chore: Add pull request review protocol to AGENTS.md (fix #7373)

Source: [neomjs/neo#7375](https://github.com/neomjs/neo/pull/7375)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Please make sure to read the Contributing Guidelines:

https://github.com/neomjs/neo/blob/dev/CONTRIBUTING.md

Added a simple but detailed PR Review Protocol for the agent.

**What kind of change does this PR introduce?** (check at least one)

- [ ] Bugfix
- [x] Feature
- [ ] Code style update
- [ ] Refactor
- [ ] Build-related changes
- [ ] Other, please describe:

**Does this PR introduce a breaking change?** (check one)

- [ ] Yes
- [x] No

If yes, please describe the impact and migration path for existing applications:

**The PR fulfills these requirements:**

- [x] It's submitted to the `dev` branch, _not_ the `main` branch
- [x] When resolving a specific issue, it's referenced in the PR's title (e.g. `fix #xxx[,#xxx]`, where "xxx" is the issue number)

If adding a **new feature**, the PR's description includes:
- [ ] A convincing reason for adding this feature (to avoid wasting your time, it's best to open a suggestion issue first and wait for approval before working on it)

**Other information:**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
