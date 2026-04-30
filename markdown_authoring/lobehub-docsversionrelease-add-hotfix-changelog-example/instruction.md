# 📝 docs(version-release): add hotfix changelog example and patch scenario [skip ci]

Source: [lobehub/lobehub#14242](https://github.com/lobehub/lobehub/pull/14242)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/version-release/reference/changelog-example/hotfix.md`
- `.agents/skills/version-release/reference/patch-release-scenarios.md`

## What to add / change

#### 💻 Change Type

- [ ] ✨ feat
- [ ] 🐛 fix
- [ ] ♻️ refactor
- [ ] 💄 style
- [ ] 👷 build
- [ ] ⚡️ perf
- [ ] ✅ test
- [x] 📝 docs
- [ ] 🔨 chore

#### 🔗 Related Issue

N/A (internal agent skill / release documentation)

#### 🔀 Description of Change

- Adds a **hotfix changelog example** under `version-release` reference material.
- Updates **patch release scenarios** to point at the new example where relevant.

This only touches `.agents/skills/version-release/reference/`; no product code.

#### 🧪 How to Test

- [ ] Tested locally
- [ ] Added/updated tests
- [x] No tests needed

#### 📸 Screenshots / Videos

N/A (documentation only)

#### 📝 Additional Information

Branch created from current `canary` and contains a single documentation commit.

Made with [Cursor](https://cursor.com)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
