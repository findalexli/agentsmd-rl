# docs: skill of diff change-log

Source: [ant-design/ant-design#57227](https://github.com/ant-design/ant-design/pull/57227)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/changelog-collect/SKILL.md`
- `AGENTS.md`

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

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
