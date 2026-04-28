# Fix yarn command format in CLAUDE.md to use local yarn version

Source: [mlflow/mlflow#18553](https://github.com/mlflow/mlflow/pull/18553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

`yarn --cwd` doesn't respect `.yarnrc.yml` in the target directory, causing commands to use the global yarn (1.22.22) instead of the project's local version (4.9.1) specified in `mlflow/server/js/yarn/releases/yarn-4.9.1.cjs`.

## Changes

Replaced all `yarn --cwd mlflow/server/js` commands with `(cd mlflow/server/js && yarn ...)` to ensure `.yarnrc.yml` is properly read:

```bash
# Before
yarn --cwd mlflow/server/js test

# After
(cd mlflow/server/js && yarn test)
```

Updated 7 command examples across testing, linting, and type-checking sections.

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> Replace `yarn --cwd mlflow/server/js ...` with `(cd mlflow/server/js && yarn ...)` in `CLAUDE.md`. `yarn --cwd` does not use `mlflow/server/js/yarn/releases/yarn-4.9.1.cjs`. It uses the globally installed yarn, which may lead to version mismatch issues.


</details>



<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/mlflow/mlflow/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documented%20in%20%5BBest%20practices%20for%20Copilot%20coding%20agent%20in%20your%20repository%5D%28https://gh.io/copilot-coding-agent-tips%29%2E%0A%0A%3COnboard%20this%20repo%3E&assignees=copilot) — coding agent works faster and does higher quality work when set up for your repo.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
