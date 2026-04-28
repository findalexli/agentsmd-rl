# NO-JIRA: docs(ai): add reference to AGENTS.md for AI agent guidance

Source: [openshift/hypershift#7085](https://github.com/openshift/hypershift/pull/7085)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## What this PR does / why we need it:
In #7074, the symlink from CLAUDE.md to AGENTS.md was removed and some specific content added to CLAUDE.md. This PR adds a directive to CLAUDE.md to instruct it to look and injest the information from AGENTS.md as well.

## Checklist:
- [x] Subject and description added to both, commit and PR.
- [x] Relevant issues have been referenced.
- [x] This change includes docs. 
- [x] This change includes unit tests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
