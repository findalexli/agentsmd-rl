# Fix Cascader Menu Item Ellipsis Styles

## Problem Description

The Cascader component's menu items do not correctly display ellipsis for long option labels when used within flex layouts. When option labels exceed the available column width, they should be truncated with an ellipsis (`...`), but instead the text either overflows or the layout breaks.

## Issue Details

The CSS-in-JS styles in the Cascader component have the ellipsis (`text-overflow: ellipsis`) styles applied to the wrong element:

- **Current (broken)**: The ellipsis styles are applied to the parent `&-item` flex container
- **Expected (fixed)**: The ellipsis styles should be applied to the `&-content` element that actually holds the text

In flex layouts, applying `text-overflow: ellipsis` to a flex container doesn't work properly because:
1. The flex container doesn't properly constrain its children's width
2. The text node needs `min-width: 0` to allow proper overflow calculation in flex contexts

## Files to Modify

- `components/cascader/style/columns.ts` - Contains the CSS-in-JS style definitions

## Required Changes

In the `getColumnsStyle` function within `columns.ts`:

1. **Remove** `...textEllipsis` from the `&-item` block
2. **Add** `maxWidth: 400` to the `&-item` block (to constrain the flex container)
3. **Add** `minWidth: 0` to the `&-content` block (required for flexbox ellipsis)
4. **Add** `...textEllipsis` to the `&-content` block (the actual ellipsis styles)

## Example

The fix transforms the style structure from:

```typescript
'&-item': {
  ...textEllipsis,  // WRONG: applied to flex container
  display: 'flex',
  // ...
  '&-content': {
    flex: 'auto',
  },
}
```

To:

```typescript
'&-item': {
  display: 'flex',
  maxWidth: 400,     // NEW: constrain the flex container
  // ...
  '&-content': {
    flex: 'auto',
    minWidth: 0,     // NEW: required for ellipsis in flex
    ...textEllipsis,  // FIXED: applied to text container
  },
}
```

## Testing

The fix should be verified by:
1. Ensuring the TypeScript file compiles without errors
2. Confirming `textEllipsis` is now in `&-content` and not in `&-item`
3. Verifying `minWidth: 0` is present in `&-content`
4. Verifying `maxWidth: 400` is present in `&-item`

## Related

- Issue #57539 - Original bug report about Cascader ellipsis not working
- This is a CSS-in-JS styling fix, no public API changes
