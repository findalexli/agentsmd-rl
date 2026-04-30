# chore: convert .cursor/rules to .claude/skills

Source: [oven-sh/bun#25683](https://github.com/oven-sh/bun/pull/25683)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/implementing-jsc-classes-cpp/SKILL.md`
- `.claude/skills/implementing-jsc-classes-zig/SKILL.md`
- `.claude/skills/writing-bundler-tests/SKILL.md`
- `.claude/skills/writing-dev-server-tests/SKILL.md`
- `.claude/skills/zig-system-calls/SKILL.md`
- `.cursor/rules/building-bun.mdc`
- `.cursor/rules/dev-server-tests.mdc`
- `.cursor/rules/javascriptcore-class.mdc`
- `.cursor/rules/registering-bun-modules.mdc`
- `.cursor/rules/writing-tests.mdc`
- `.cursor/rules/zig-javascriptcore-classes.mdc`

## What to add / change

## Summary
- Migrate Cursor rules to Claude Code skills format
- Add 4 new skills for development guidance:
  - `writing-dev-server-tests`: HMR/dev server test guidance
  - `implementing-jsc-classes-cpp`: C++ JSC class implementation  
  - `implementing-jsc-classes-zig`: Zig JSC bindings generator
  - `writing-bundler-tests`: bundler test guidance with itBundled
- Remove all `.cursor/rules/` files

## Test plan
- [x] Skills follow Claude Code skill authoring guidelines
- [x] Each skill has proper YAML frontmatter with name and description
- [x] Skills are concise and actionable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
