# chore:Added AGENTS.md file for ai agents

Source: [auth0/Auth0.Android#872](https://github.com/auth0/Auth0.Android/pull/872)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

### Changes
This PR adds an `AGENTS.md` file replacing the `copilot-instructions.md` for giving the repo context for AI agents
### References 
https://agents.md/


### Checklist

- [X] I have read the [Auth0 general contribution guidelines](https://github.com/auth0/open-source-template/blob/master/GENERAL-CONTRIBUTING.md)

- [X] I have read the [Auth0 Code of Conduct](https://github.com/auth0/open-source-template/blob/master/CODE-OF-CONDUCT.md)

- [X] All existing and new tests complete without errors

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
