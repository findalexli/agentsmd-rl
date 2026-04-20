# Bug Fix Task: mantinedev/mantine#8488

## Repository
`mantinedev/mantine` - Mantine React component library, a monorepo using Yarn workspaces.

## PR Context
PR #8488 fixes a bug in the `@mantine/dates` package where `getMonthControlProps` and `getYearControlProps` callbacks do not properly override the default `children` content in date picker components.

## Bug Description

When using `MonthsList` or `YearsList` components with the `getMonthControlProps` or `getYearControlProps` callbacks respectively, returning `{ children: <customContent> }` in the callback result should render the custom children instead of the default formatted month/year label. Currently, the custom children are ignored and the default formatted label is always displayed.

### Affected Components
- `packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx`
- `packages/@mantine/dates/src/components/YearsList/YearsList.tsx`

### Expected Behavior
```tsx
// When getMonthControlProps returns children, they should be rendered
<MonthsList
  year="2022-01-01"
  getMonthControlProps={(date) => ({
    children: <strong>{date}</strong>,  // This should be rendered as the month cell content
  })}
/>
```

### Actual Behavior (Bug)
The custom `children` returned from `getMonthControlProps` is silently ignored. The default formatted month label (e.g., "Jan", "Feb", etc.) is always rendered regardless of what `children` is provided in the callback result.

## Task
Fix the bug so that when `getMonthControlProps` or `getYearControlProps` returns a `children` property, those children are rendered instead of the default formatted month/year label.

## Files to Modify
- `packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx`
- `packages/@mantine/dates/src/components/YearsList/YearsList.tsx`

## Verification
After fixing:
1. Custom children returned from `getMonthControlProps`/`getYearControlProps` are rendered instead of the default formatted label
2. ESLint passes on the modified files (`yarn eslint packages/@mantine/dates/src/components/MonthsList/ packages/@mantine/dates/src/components/YearsList/`)
3. Prettier passes on the modified files (`yarn prettier --check packages/@mantine/dates/src/components/MonthsList/ packages/@mantine/dates/src/components/YearsList/`)