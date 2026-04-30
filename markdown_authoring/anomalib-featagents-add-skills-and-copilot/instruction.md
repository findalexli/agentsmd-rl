# feat(agents): add skills and copilot instructions

Source: [open-edge-platform/anomalib#3524](https://github.com/open-edge-platform/anomalib/pull/3524)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/benchmark-and-docs-refresh/SKILL.md`
- `.agents/skills/docs-changelog/SKILL.md`
- `.agents/skills/model-doc-sync/SKILL.md`
- `.agents/skills/model-sample-image-export/SKILL.md`
- `.agents/skills/models-data/SKILL.md`
- `.agents/skills/pr-workflow/SKILL.md`
- `.agents/skills/python-docstrings/SKILL.md`
- `.agents/skills/python-style/SKILL.md`
- `.agents/skills/testing/SKILL.md`
- `.agents/skills/third-party-code/SKILL.md`
- `.cursor/rules/python_docstrings.mdc`
- `.github/copilot-instructions.md`

## What to add / change

## 📝 Description

- Introduce skills and copilot instructions

## ✨ Changes

Select what type of change your PR is:

- [x] 🚀 New feature (non-breaking change which adds functionality)
- [ ] 🐞 Bug fix (non-breaking change which fixes an issue)
- [ ] 🔄 Refactor (non-breaking change which refactors the code base)
- [ ] ⚡ Performance improvements
- [ ] 🎨 Style changes (code style/formatting)
- [ ] 🧪 Tests (adding/modifying tests)
- [ ] 📚 Documentation update
- [ ] 📦 Build system changes
- [ ] 🚧 CI/CD configuration
- [ ] 🔧 Chore (general maintenance)
- [ ] 🔒 Security update
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)

## ✅ Checklist

Before you submit your pull request, please make sure you have completed the following steps:

- [ ] 📚 I have made the necessary updates to the documentation (if applicable).
- [ ] 🧪 I have written tests that support my changes and prove that my fix is effective or my feature works (if applicable).
- [x] 🏷️ My PR title follows conventional commit format.

For more information about code review checklists, see the [Code Review Checklist](https://github.com/open-edge-platform/anomalib/blob/main/docs/source/markdown/guides/developer/contributing.md).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
