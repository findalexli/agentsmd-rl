# docs: add AGENTS.md and CLAUDE.md for AI agent guidance

Source: [kubernetes-sigs/cluster-api-provider-azure#5899](https://github.com/kubernetes-sigs/cluster-api-provider-azure/pull/5899)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

**What type of PR is this?**
/kind documentation
<!--
Add one of the following kinds:
/kind feature
/kind bug
/kind api-change
/kind cleanup
/kind deprecation
/kind design
/kind documentation
/kind failing-test
/kind flake
-->

**What this PR does / why we need it**:
- Introduce `AGENTS.md` with guidelines for using AI coding assistants
- Add `CLAUDE.md` as initial placeholder for Claude-specific setup/notes
- No code or behavior changes

**Which issue(s) this PR fixes** *(optional, in `fixes #<issue number>(, fixes #<issue_number>, ...)` format, will close the issue(s) when PR gets merged)*:
N/A

**Special notes for your reviewer**:
This seems to be the way the industry/upstream is approaching including AI helper files that work with different agents:
- https://github.com/kubernetes/kubernetes/pull/133386
- https://agents.md/


**TODOs**:
<!-- Put an "X" character inside the brackets of each completed task. Some may be optional depending on the PR. -->

- [ ] squashed commits
- [ ] includes documentation
- [ ] adds unit tests
- [ ] cherry-pick candidate

**Release note**:
<!--  Write your release note:
1. Enter your extended release note in the below block. If the PR requires additional action from users switching to the new release, include the string "action required".
2. If no release note is required, just write "NONE".
-->
```release-note
NONE
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
