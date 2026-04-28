# chore: remove GitHub Copilot skills

Source: [sozercan/kaset#110](https://github.com/sozercan/kaset/pull/110)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/swift-concurrency/SKILL.md`
- `.github/skills/swift-concurrency/references/actors.md`
- `.github/skills/swift-concurrency/references/async-await-basics.md`
- `.github/skills/swift-concurrency/references/async-sequences.md`
- `.github/skills/swift-concurrency/references/core-data.md`
- `.github/skills/swift-concurrency/references/glossary.md`
- `.github/skills/swift-concurrency/references/linting.md`
- `.github/skills/swift-concurrency/references/memory-management.md`
- `.github/skills/swift-concurrency/references/migration.md`
- `.github/skills/swift-concurrency/references/performance.md`
- `.github/skills/swift-concurrency/references/sendable.md`
- `.github/skills/swift-concurrency/references/tasks.md`
- `.github/skills/swift-concurrency/references/testing.md`
- `.github/skills/swift-concurrency/references/threading.md`
- `.github/skills/swiftui-liquid-glass/SKILL.md`
- `.github/skills/swiftui-performance-audit/SKILL.md`
- `.github/skills/swiftui-ui-patterns/SKILL.md`
- `.github/skills/swiftui-view-refactor/SKILL.md`

## What to add / change

Remove the `.github/skills/` directory containing Copilot skill definitions that are no longer needed.

### Removed
- `swift-concurrency` skill (SKILL.md + 13 reference docs)
- `swiftui-liquid-glass` skill
- `swiftui-performance-audit` skill
- `swiftui-ui-patterns` skill
- `swiftui-view-refactor` skill

18 files deleted, ~6800 lines removed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
