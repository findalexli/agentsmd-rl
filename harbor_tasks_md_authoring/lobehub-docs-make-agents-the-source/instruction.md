# 📝 docs: make AGENTS the source of truth

Source: [lobehub/lobehub#14180](https://github.com/lobehub/lobehub/pull/14180)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

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

N/A

#### 🔀 Description of Change

- Move the latest agent guidance into `AGENTS.md` so it is the single source of truth.
- Replace `CLAUDE.md` with the Claude Code import wrapper for `AGENTS.md`.

#### 🧪 How to Test

- [ ] Tested locally
- [ ] Added/updated tests
- [x] No tests needed

Documentation-only change.

#### 📸 Screenshots / Videos

N/A

#### 📝 Additional Information

N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
