# Task: Add Icon Semantic Support to Popconfirm Component

## Problem Description

The Popconfirm component currently supports semantic styling through `classNames` and `styles` props for the root, container, title, content, and arrow elements. However, the **icon element** is missing from this semantic styling system.

When users pass `classNames={{ icon: 'my-class' }}` or `styles={{ icon: { color: 'blue' } }}` to Popconfirm, these values should be applied to the confirmation icon element, but currently they have no effect.

## Expected Behavior

Users should be able to customize the icon element through the semantic API. The following usage pattern should work:

```tsx
<Popconfirm
  title="Confirm?"
  classNames={{ icon: 'my-custom-icon-class' }}
  styles={{ icon: { color: 'blue', fontSize: '24px' } }}
>
  <Button>Click me</Button>
</Popconfirm>
```

The icon wrapper element should receive both the base styling class (e.g., `ant-popconfirm-message-icon`) and any custom class name passed via `classNames.icon`. The inline styles passed via `styles.icon` should be applied to the icon wrapper's style attribute.

## Type Definition Requirements

The semantic type definitions must be updated to include `icon` support:

- The type definition must be named `PopconfirmSemanticType`
- It must also export `PopconfirmSemanticAllType` for use in component props
- `classNames` should accept an `icon` field with type `string`
- `styles` should accept an `icon` field with type `React.CSSProperties`

## Files to Modify

The implementation should modify files within `components/popconfirm/`:

1. The main component entry file that defines the semantic types
2. The panel implementation file that renders the icon element
3. The demo file `demo/_semantic.tsx` that documents semantic elements
4. The test file `__tests__/semantic.test.tsx` that validates semantic styling

## Test Fixture Requirements

The semantic test file must include assertions with these exact fixture values:

**Static tests:**
- `icon: 'custom-icon'` for classNames testing
- `icon: { color: 'blue' }` for styles testing

**Dynamic (function-based) tests:**
- `icon: 'dynamic-icon'` for classNames testing
- `icon: { color: props.placement === 'top' ? 'green' : 'transparent' }` for styles testing

The demo documentation must include `icon` in the semantics list with the name `'icon'`.

## Verification

You can verify your changes work by running:

```bash
npm test -- --testPathPattern=popconfirm/__tests__/semantic
```

All repository tests (lint, TypeScript, unit tests) should also pass after your changes.
