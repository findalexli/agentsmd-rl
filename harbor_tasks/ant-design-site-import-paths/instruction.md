# Task: Fix Import Paths in Documentation Site

## Problem

The Ant Design documentation site (located in `.dumi/`) contains several files that use relative import paths to access internal utilities from the `components/` directory. These relative imports are fragile and should be replaced with proper package imports from the `antd` npm package.

## Affected Files

The following files in the `.dumi/` directory need their import paths updated:

1. `.dumi/hooks/useThemeAnimation.ts` - imports theme utility
2. `.dumi/pages/index/components/Theme/index.tsx` - imports copy utility
3. `.dumi/pages/index/components/ThemePreview/index.tsx` - imports copy utility
4. `.dumi/theme/builtins/Previewer/DesignPreviewer.tsx` - imports copy utility
5. `.dumi/theme/common/ThemeSwitch/PromptDrawer.tsx` - imports copy utility
6. `.dumi/theme/layouts/ResourceLayout/AffixTabs.tsx` - imports scrollTo utility
7. `.dumi/theme/slots/SiteContext.ts` - imports ConfigComponentProps type

## What Needs to Change

Currently, these files use relative imports like:
- `../../components/theme`
- `../../../../../components/_util/copy`
- `../../../../components/_util/copy`
- `../../../components/config-provider/context`

These should be changed to use proper package imports from the published `antd` package:
- The `theme` export should come from `'antd'`
- Utilities like `copy` and `scrollTo` should come from `'antd/lib/_util/*'`
- Types like `ConfigComponentProps` should come from `'antd/es/config-provider/context'`

## Requirements

1. All relative imports to `components/` from `.dumi/` files must be eliminated
2. TypeScript compilation (`npm run tsc` or `npx tsc --noEmit`) must pass
3. The documentation site must remain functional after the changes

## Hints

- The `antd` package exports a `theme` object that can be imported directly
- Internal utilities under `components/_util/` are available under `antd/lib/_util/`
- Type definitions under `components/` are available under `antd/es/`
- Some import order adjustments may be needed to maintain alphabetical ordering within import groups
