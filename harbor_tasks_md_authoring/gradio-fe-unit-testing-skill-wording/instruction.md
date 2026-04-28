# fe unit testing skill wording update

Source: [gradio-app/gradio#13263](https://github.com/gradio-app/gradio/pull/13263)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/frontend-unit-testing/SKILL.md`

## What to add / change

## Description

Please include a concise summary, in clear English, of the changes in this pull request. If it closes an issue, please mention it here.

Closes: #(issue)

## AI Disclosure

We encourage the use of AI tooling in creating PRs, but the any non-trivial use of AI needs be disclosed. E.g. if you used Claude to write a first draft, you should mention that. Trivial tab-completion doesn't need to be disclosed. You should self-review all PRs, especially if they were generated with AI.

- [ ] I used AI to... [fill here]
- [ ] I did not use AI

## 🎯 PRs Should Target Issues

Before your create a PR, please check to see if there is [an existing issue](https://github.com/gradio-app/gradio/issues) for this change. If not, please create an issue before you create this PR, unless the fix is very small. 

Not adhering to this guideline will result in the PR being closed. 

## Testing and Formatting Your Code

1. PRs will only be merged if tests pass on CI. We recommend at least running the backend tests locally, please set up [your Gradio environment locally](https://github.com/gradio-app/gradio/blob/main/CONTRIBUTING.md) and run the backed tests: `bash scripts/run_backend_tests.sh`

2. Please run these bash scripts to automatically format your code: `bash scripts/format_backend.sh`, and (if you made any changes to non-Python files) `bash scripts/format_frontend.sh`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
