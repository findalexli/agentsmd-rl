# docs: update AGENTS.md

Source: [ant-design/ant-design#57480](https://github.com/ant-design/ant-design/pull/57480)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!--
First of all, thank you for your contribution! 😄
For requesting to pull a new feature or bugfix, please send it from a feature/bugfix branch based on the `master` branch.
Before submitting your pull request, please make sure the checklist below is filled out.
Your pull requests will be merged after one of the collaborators approves.
Thank you!
-->

[中文版模板 / Chinese template](https://github.com/ant-design/ant-design/blob/master/.github/PULL_REQUEST_TEMPLATE_CN.md?plain=1)

### 🤔 This is a ...

- [ ] 🆕 New feature
- [ ] 🐞 Bug fix
- [x] 📝 Site / documentation improvement
- [ ] 📽️ Demo improvement
- [ ] 💄 Component style improvement
- [ ] 🤖 TypeScript definition improvement
- [ ] 📦 Bundle size optimization
- [ ] ⚡️ Performance optimization
- [ ] ⭐️ Feature enhancement
- [ ] 🌐 Internationalization
- [ ] 🛠 Refactoring
- [ ] 🎨 Code style optimization
- [ ] ✅ Test Case
- [ ] 🔀 Branch merge
- [ ] ⏩ Workflow
- [ ] ⌨️ Accessibility improvement
- [ ] ❓ Other (about what?)

### 🔗 Related Issues

> - Describe the source of related requirements, such as links to relevant issue discussions.
> - For example: close #xxxx, fix #xxxx

### 💡 Background and Solution

> - The specific problem to be addressed.
> - List the final API implementation and usage if needed.
> - If there are UI/interaction changes, consider providing screenshots or GIFs.

### 📝 Change Log

> - Read [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)! Track your changes, 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
