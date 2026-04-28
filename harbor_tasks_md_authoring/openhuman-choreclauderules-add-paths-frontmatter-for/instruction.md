# chore(claude-rules): add paths frontmatter for conditional loading

Source: [tinyhumansai/openhuman#804](https://github.com/tinyhumansai/openhuman/pull/804)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/03-platform-setup-windows.md`
- `.claude/rules/04-platform-setup-macos.md`
- `.claude/rules/05-platform-setup-android.md`
- `.claude/rules/06-platform-setup-ios.md`
- `.claude/rules/07-rust-backend-guide.md`
- `.claude/rules/08-frontend-guide.md`
- `.claude/rules/09-permissions-capabilities.md`
- `.claude/rules/12-design-system.md`
- `.claude/rules/13-backend-auth-implementation.md`
- `.claude/rules/14-deep-link-platform-guide.md`
- `.claude/rules/15-settings-modal-system.md`
- `.claude/rules/16-macos-background-execution.md`
- `.claude/rules/17-skills-memory-inference-flow.md`

## What to add / change

## Summary

Adds \`paths:\` YAML frontmatter to 13 of the 18 files in \`.claude/rules/\` so they load conditionally based on what files the AI assistant is editing, instead of every session loading all ~55k tokens of rules unconditionally.

## Impact

- **Token savings**: ~25-30k tokens per session when working outside the scoped areas (most sessions).
- **No content changes**: only adds frontmatter; every rule file still auto-loads when you're editing files it applies to.
- **No effect on contributors without Claude Code**: YAML frontmatter is inert in Markdown renderers.

## Scope map

| File | Loads when editing |
|---|---|
| 03 platform-setup-windows | tauri src |
| 04 platform-setup-macos | tauri src |
| 05 platform-setup-android | \`gen/android\` |
| 06 platform-setup-ios | \`gen/apple\` |
| 07 rust-backend-guide | \`*.rs\` + Cargo |
| 08 frontend-guide | \`app/src/**\` |
| 09 permissions-capabilities | \`capabilities/**\`, \`tauri.conf.json\` |
| 12 design-system | tsx/css/tailwind |
| 13 backend-auth | auth files |
| 14 deep-link | deep-link + tauri conf |
| 15 settings-modal | \`components/settings\` |
| 16 macos-background | \`lib.rs\`, Info.plist |
| 17 skills-memory-inference | skills + memory + providers |

Always-loaded (no frontmatter, unchanged): \`00-project-vision\`, \`01-project-overview\`, \`02-development-commands\`, \`10-troubleshooting\`, \`11-tech-stack-detailed\`.

## Follow-up (not in this PR)

Several rule files reference stale architecture (e.g. MT

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
