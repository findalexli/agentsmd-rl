# Fix Button Accessibility: Make Disabled Buttons Keyboard-Focusable

## Problem

The Storybook Button component in `code/core/src/components/components/Button/Button.tsx` currently uses the native HTML `disabled` attribute when a button is disabled or in read-only mode. This causes a significant accessibility issue: **disabled buttons are not keyboard-focusable**, meaning screen reader users and keyboard-only users cannot navigate to them and may miss important UI context.

When a Button has `disabled={true}` or `readOnly={true}`, the native `disabled` attribute:
1. Removes the button from the keyboard tab order
2. Prevents screen readers from announcing the button's presence
3. Violates WCAG accessibility guidelines for disabled controls

## Requirements

Fix the Button component to meet these accessibility requirements:

### 1. Accessibility Attribute

Instead of using the native `disabled` attribute (which removes the button from the tab order), the button should use `aria-disabled` to indicate the disabled state while remaining focusable. The attribute should be set to `'true'` when either `disabled` or `readOnly` is true, and `undefined` otherwise.

### 2. Click Handler Blocking

When the button is in a disabled or read-only state, clicking it should not trigger the click handler. The onClick handler should be blocked when the button is disabled or readOnly.

### 3. Styled Component Transient Prop

The StyledButton component receives styling props from the Button component. When passing the disabled state to the styled component for CSS styling purposes, use a transient prop (prefixed with `$`) to prevent styled-components from forwarding it to the underlying DOM `<button>` element, which would cause React warnings.

The StyledButton prop interface should declare this transient prop appropriately.

### 4. Visual Styling Requirements

The styled component's CSS must maintain the current visual appearance for disabled buttons:
- When `readOnly` is true: cursor should be `'inherit'` and opacity should be normal (1)
- When the button is disabled (but not readOnly): cursor should be `'not-allowed'` and opacity should be 0.5
- When neither: cursor should be `'pointer'` and opacity should be normal (1)

The CSS should reference the transient `$disabled` prop to determine the styling state.

## Acceptance Criteria

1. The button renders `aria-disabled="true"` when disabled or readOnly, NOT the native `disabled` attribute
2. Disabled buttons remain keyboard-focusable (tabbable)
3. The click handler is blocked when the button is disabled or readOnly
4. Visual styling (opacity 0.5, cursor: not-allowed) remains for disabled buttons
5. The component compiles without TypeScript errors
6. No browser console warnings about invalid DOM attributes (achieved by using transient `$` prefix for styled-component props that shouldn't reach the DOM)

## Constraints

- Do not add new dependencies
- Do not modify test files
- Do not change the external API (props) of the Button component
- Do not break existing visual styling
