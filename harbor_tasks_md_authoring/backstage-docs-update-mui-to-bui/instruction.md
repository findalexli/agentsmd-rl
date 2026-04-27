# docs: update MUI to BUI migration skill

Source: [backstage/backstage#33548](https://github.com/backstage/backstage/pull/33548)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/.well-known/skills/mui-to-bui-migration/SKILL.md`

## What to add / change

## Hey, I just made a Pull Request!

This updates the MUI to BUI migration skill (`docs/.well-known/skills/mui-to-bui-migration/SKILL.md`) to reflect the current state of `@backstage/ui`. The skill had gotten a bit out of date with several rounds of breaking changes in the UI package.

Changes include:

- **Added missing components** to the available components list: `Alert`, `FullPage`, `FieldLabel`, `PluginHeader`, `List`/`ListRow`, `SearchAutocomplete`, `TablePagination`, `BUIProvider`, `TooltipTrigger`
- **Added missing hooks**: `useTable`
- **Fixed outdated CSS variable names**: `--bui-bg-surface-1` → `--bui-bg-neutral-1`, `--bui-bg-surface-0` → `--bui-bg-app`, `--bui-bg-hover` → `--bui-bg-neutral-1-hover`, `--bui-border` → `--bui-border-1`, `--bui-fg-link` → `--bui-fg-info`
- **Updated Tooltip pattern**: `TooltipTrigger` is now exported from `@backstage/ui` directly (no longer needs `react-aria-components` import)
- **Updated List pattern**: replaced manual HTML list approach with the new BUI `List` and `ListRow` components
- **Added Alert migration pattern** (section 14): BUI now has an `Alert` component
- **Updated Known Limitations**: removed Alert and Pagination (both now exist in BUI)
- **Updated component details**: `Button` tertiary variant, `destructive`/`loading` props, `Accordion` sub-components, `Menu` sub-components, etc.
- **Updated migration checklist**: added Alert and List migration items, removed `react-aria-components` dependency step



## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
