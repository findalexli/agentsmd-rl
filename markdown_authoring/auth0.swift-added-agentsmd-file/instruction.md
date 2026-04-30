# Added Agents.md file

Source: [auth0/Auth0.swift#1027](https://github.com/auth0/Auth0.swift/pull/1027)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

### 📋 Changes

-  Added AGENTS.md file to the repo 

AGENTS.md complements this by containing the extra, sometimes detailed context coding agents need: build steps, tests, and conventions that might clutter a README or aren’t relevant to human contributors.


### 📎 References
https://agents.md/

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
