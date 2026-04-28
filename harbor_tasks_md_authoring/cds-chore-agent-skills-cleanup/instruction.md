# chore: Agent skills cleanup

Source: [coinbase/cds#608](https://github.com/coinbase/cds/pull/608)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/design-system-researcher.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/components.best-practices/SKILL.md`
- `.claude/skills/components.styles/README.md`
- `.claude/skills/components.styles/SKILL.md`
- `.claude/skills/components.write-docs/README.md`
- `.claude/skills/components.write-docs/SKILL.md`
- `.claude/skills/dev.cds-mobile/SKILL.md`
- `.claude/skills/dev.cds-web/SKILL.md`
- `.claude/skills/feature-planner/SKILL.md`
- `.claude/skills/figma.audit-connect/SKILL.md`
- `.claude/skills/figma.connect-best-practices/SKILL.md`
- `.claude/skills/figma.create-connect/SKILL.md`
- `.claude/skills/git.detect-breaking-changes/SKILL.md`
- `.claude/skills/git.repo-manager/SKILL.md`
- `.claude/skills/research.component-libs/SKILL.md`
- `.claude/skills/research.deprecation-usage/SKILL.md`
- `.claude/skills/summarize-commits/SKILL.md`

## What to add / change

<!-- Please ensure your pull request title adheres to our [PR Title Convention](https://github.com/coinbase/cds/blob/master/CONTRIBUTING.md#pr-title-convention). -->

## What changed? Why?

1. A new skill for checking for usage of a deprecated CDS export
2. General skill cleanup

### Root cause (required for bugfixes)

## UI changes

| iOS Old        | iOS New        |
| -------------- | -------------- |
| old screenshot | new screenshot |

| Android Old    | Android New    |
| -------------- | -------------- |
| old screenshot | new screenshot |

| Web Old        | Web New        |
| -------------- | -------------- |
| old screenshot | new screenshot |

## Testing

### How has it been tested?

- [ ] Unit tests
- [ ] Interaction tests
- [ ] Pseudo State tests
- [ ] Manual - Web
- [ ] Manual - Android (Emulator / Device)
- [ ] Manual - iOS (Emulator / Device)

### Testing instructions

## Illustrations/Icons Checklist

Required if this PR changes files under `packages/illustrations/**` or `packages/icons/**`

- [ ] verified visreg changes with Terran (include link to visreg run/approval)
- [ ] all illustration/icons names have been reviewed by Dom and/or Terran

## Change management

type=routine <!-- {routine,nonroutine,emergency} -->
risk=low <!-- {low,medium,high} -->
impact=sev5 <!--{sev1,sev2,sev3,sev4,sev5} -->

automerge=false

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
