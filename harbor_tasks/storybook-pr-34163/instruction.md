# Fix Link Component Keyboard Accessibility

## Problem

The `Link` component in Storybook's component library has an accessibility issue. When a `Link` is used without an `href` prop (typically as a click handler with `onClick`), it renders as an anchor element (`<a>`) without an `href` attribute. Anchor elements without `href` are **not keyboard-focusable**, making these "link buttons" inaccessible to keyboard users who navigate via Tab key.

## File to Modify

`code/core/src/components/components/typography/link/link.tsx`

## Required Behaviors

### 1. Conditional Element Rendering

The component must dynamically render as either an `<a>` or `<button>` element based on the presence of the `href` prop:

- When `href` is provided: render as an anchor (`<a>`) element with the `href` attribute passed through
- When `href` is not provided: render as a `<button>` element (which is naturally keyboard-focusable)

The component must use styled-components' `as` prop or equivalent mechanism to dynamically change the rendered element.

### 2. Focus Indicator Styles

Button-styled links must have visible focus indicators for keyboard navigation. Required styles:

- Add `&:focus-visible` CSS selector with visible focus indicator styles
- Include an `outline` property that uses `theme.color.secondary` for the focus color
- Include a `zIndex` property to ensure the focus outline appears above sibling elements

### 3. Deprecation Warning for `isButton` Prop

The `isButton` prop is now obsolete because button behavior is automatic based on `href` presence. Implement deprecation:

- Import the deprecation utility from `storybook/internal/client-logger` (the `deprecate` function)
- The `isButton` prop should default to `undefined` (not `false`) so the component can detect when it was explicitly provided vs. not provided
- When `isButton` is explicitly passed (i.e., not left as the default), call `deprecate()` with a warning message explaining that `isButton` is deprecated

### 4. Verification

After making changes, verify:
1. The component compiles: `yarn nx compile core`
2. TypeScript check passes: `yarn nx run-many -t check --projects=core`
3. Code formatting passes: `yarn prettier --check code/core/src/components/components/typography/link/link.tsx`

## Context

This fix ensures that links styled as buttons (like "View error" links that open popovers) are accessible to keyboard users. Without this fix, these elements are unreachable via keyboard navigation, violating WCAG accessibility guidelines. The automatic element switching removes the need for users to manually specify `isButton`, while the deprecation warning helps existing code migrate.
