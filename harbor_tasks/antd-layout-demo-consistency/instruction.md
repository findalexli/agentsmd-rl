# Fix Layout Demo Code Consistency

## Problem

The layout demo files in `components/layout/demo/` have inconsistent variable declaration patterns. Some demos declare the Footer year variable outside the App component while others declare it inside. This inconsistency makes the demos harder to maintain and contradicts React best practices.

## Expected Behavior

The `currentYear` variable used in the Footer should be declared inside the `App` component for consistency with React best practices. The demos should follow a uniform structure.

## Files to Update

All six layout demo files in `components/layout/demo/`:
- `fixed-sider.tsx`
- `fixed.tsx`
- `responsive.tsx`
- `side.tsx`
- `top-side.tsx`
- `top.tsx`

## Verification

After the fix:
1. The demos should continue to compile and pass all tests (TypeScript, ESLint, Prettier, Jest)
2. The Footer in each demo should still display the current year correctly
3. The `currentYear` variable should be declared inside the App component (not at module level)
4. All demos should follow the same consistent structure

## Notes

- This is a code style/consistency improvement
- The functional behavior (displaying the current year in the footer) must be preserved
- Follow the pattern established by the majority of the demo files