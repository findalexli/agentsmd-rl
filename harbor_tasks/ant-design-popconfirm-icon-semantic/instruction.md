# Task: Add Icon Semantic Support to Popconfirm Component

## Problem Description

The Popconfirm component currently supports semantic styling through `classNames` and `styles` props for various elements (root, container, title, content, arrow). However, the **icon element** is missing from this semantic styling system.

Users cannot apply custom CSS classes or inline styles to the confirmation icon via the semantic API.

## Files to Modify

You need to modify the following files in `components/popconfirm/`:

1. **index.tsx** - Define `PopconfirmSemanticType` with `icon` field support in both `classNames` and `styles`
2. **PurePanel.tsx** - Apply `classNames?.icon` and `styles?.icon` to the icon `<span>` element
3. **demo/_semantic.tsx** - Add icon to the semantics documentation list

## Expected Behavior

After your changes, users should be able to:

```tsx
<Popconfirm
  title="Confirm?"
  classNames={{ icon: 'my-custom-icon-class' }}
  styles={{ icon: { color: 'blue', fontSize: '24px' } }}
>
  <Button>Click me</Button>
</Popconfirm>
```

The icon element should receive both the custom class name and the inline styles.

## Type Requirements

The type definition should extend the base semantic types:

```typescript
type PopconfirmSemanticType = {
  classNames?: PopoverSemanticType['classNames'] & {
    icon?: string;
  };
  styles?: PopoverSemanticType['styles'] & {
    icon?: React.CSSProperties;
  };
};
```

## Implementation Notes

- The icon span in `PurePanel.tsx` currently has a static className: `\`${prefixCls}-message-icon\``
- Use `clsx()` to combine the base class with the optional `classNames?.icon`
- Apply `styles?.icon` to the style prop of the icon span
- The `OverlayProps` interface in `PurePanel.tsx` should reference `PopconfirmSemanticAllType` instead of `PopoverSemanticAllType`

## Testing

The repository has existing tests in `components/popconfirm/__tests__/semantic.test.tsx`. Your implementation should pass these tests when they are updated to check for icon semantic styling.

You can verify your changes work by running:

```bash
npm test -- --testPathPattern=popconfirm/__tests__/semantic
```
