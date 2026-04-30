# docs: add CLAUDE.md for AI assistant context

Source: [ant-design/ant-design#57223](https://github.com/ant-design/ant-design/pull/57223)

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

> N/A

### 💡 Background and Solution

Claude Code automatically loads `CLAUDE.md` from project root on each session. This helps AI assistants understand the project conventions and coding standards without needing to be told each time.

This PR adds a `CLAUDE.md` file that:
- Provides project overview (React component library, TypeScript, CSS-in-JS)
- Lists common commands
- Summarizes core coding standards (functional components, naming conventions)
- Documents PR and Changelog guidelines
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
