# chore(claude): port skills + rules from shipping-platform (sub-PR 1 of 2026.5)

Source: [karrioapi/karrio#1069](https://github.com/karrioapi/karrio/pull/1069)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/code-style.md`
- `.claude/rules/commit-conventions.md`
- `.claude/rules/extension-patterns.md`
- `.claude/rules/testing.md`
- `.claude/skills/create-extension-module/SKILL.md`
- `.claude/skills/django-graphql/SKILL.md`
- `.claude/skills/django-rest-api/SKILL.md`
- `.claude/skills/review-implementation/SKILL.md`
- `.claude/skills/run-tests/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

Sub-PR **1** of the 2026.5.0 umbrella release ([#1065](https://github.com/karrioapi/karrio/pull/1065) / [`PRDs/RELEASE_2026_5_PLATFORM_UPGRADE.md`](./PRDs/RELEASE_2026_5_PLATFORM_UPGRADE.md)). Pure dev-tooling — no Python, YAML, Dockerfile, or package.json changes.

Brings karrio's `.claude/` skills + rules up to parity with sister repo `jtlshipping/shipping-platform` while preserving karrio-specific rules (\`import karrio.lib as lib\`, no pytest, 4-method carrier test pattern, no legacy \`DP/SF/NF/DF/XP\`).

## Changes

### Skills added (new)

| Skill | Source | Adaptation |
|---|---|---|
| `create-extension-module/` | JTL | Reframed around karrio's `modules/orders`, `modules/events`, `modules/documents` as canonical examples (JTL referenced its own \`entitlements\`). Dropped "JTL custom karrio modules" label. |
| `django-graphql/` | JTL | Portable as-is — all references were generic \`karrio.server.*\`. |
| `django-rest-api/` | JTL | Portable as-is. |
| `run-tests/` | karrio-specific (JTL has a version but needed full rewrite) | Decision table mapping \`modules/*\` paths to the right \`karrio test\` / \`./bin/run-*-tests\` / \`python -m unittest discover\` command. |

### Skills updated

| Skill | Change |
|---|---|
| `review-implementation/` | Expanded N+1 prevention checklist (per-model / per-serializer / per-view / bulk-ops bullets + grep red-flags), added extension-pattern gate, security check, migration safety. |

### Skills kept unchanged

`carrier-integra

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
