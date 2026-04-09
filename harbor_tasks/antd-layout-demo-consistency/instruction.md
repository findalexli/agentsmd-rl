# Task: Fix Layout Demo Code Consistency

## Problem

The Layout component demos in `components/layout/demo/` have inconsistent patterns for initializing the `currentYear` variable used in the Footer. Some demos declare `currentYear` at module level (outside the component), while it should be inside the App component for consistency with React best practices.

## Files to Fix

The following demo files need to be updated:
- `components/layout/demo/fixed-sider.tsx`
- `components/layout/demo/fixed.tsx`
- `components/layout/demo/responsive.tsx`
- `components/layout/demo/side.tsx`
- `components/layout/demo/top-side.tsx`
- `components/layout/demo/top.tsx`

## Requirements

1. Move the `currentYear` variable initialization from module level to inside the `App` component
2. Place it after the `theme.useToken()` call within the component function body
3. Ensure all 6 files follow the same consistent pattern
4. The Footer should continue to reference `currentYear` correctly

## Example of the Fix Pattern

Before (module level):
```tsx
const currentYear = new Date().getFullYear();

const App: React.FC = () => {
  const { token } = theme.useToken();
  // ...
}
```

After (inside component):
```tsx
const App: React.FC = () => {
  const { token } = theme.useToken();
  const currentYear = new Date().getFullYear();
  // ...
}
```

## Notes

- This is a code style/consistency improvement
- The demos should follow React best practices by avoiding module-level side effects
- All files should have the same structure for maintainability
