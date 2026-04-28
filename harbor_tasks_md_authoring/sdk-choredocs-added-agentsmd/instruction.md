# chore(docs): added AGENTS.MD

Source: [kubeflow/sdk#106](https://github.com/kubeflow/sdk/pull/106)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**What this PR does / why we need it**:
adds `AGENTS.MD` file for AI-assisted development 


Fixes #86 

**Checklist:**

- [ ] [Docs](https://www.kubeflow.org/docs/) included if any changes are user facing

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
