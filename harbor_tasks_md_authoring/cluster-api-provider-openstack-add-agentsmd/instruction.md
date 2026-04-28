# 🌱 Add AGENTS.md

Source: [kubernetes-sigs/cluster-api-provider-openstack#2807](https://github.com/kubernetes-sigs/cluster-api-provider-openstack/pull/2807)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**What this PR does / why we need it**:

This adds a file with instructions for AI agents. [AGENTS.md](https://agents.md/) is a vendor agnostic way of providing these instructions that seems to be supported by many of the popular models. It is also being adopted by other projects in the ecosystem:
- https://github.com/kubernetes-sigs/cluster-api-provider-azure/pull/5899
- https://github.com/kubernetes/org/blob/main/AGENTS.md
- https://github.com/kubernetes/kubernetes/pull/133386

**Which issue(s) this PR fixes** *(optional, in `fixes #<issue number>(, fixes #<issue_number>, ...)` format, will close the issue(s) when PR gets merged)*:
Fixes #

**Special notes for your reviewer**:

1. Please confirm that if this PR changes any image versions, then that's the sole change this PR makes.

**TODOs**:
<!-- Put an "X" character inside the brackets of each completed task. Some may be optional depending on the PR. -->

- [x] squashed commits
- if necessary:
  - [x] includes documentation
  - [ ] adds unit tests

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
