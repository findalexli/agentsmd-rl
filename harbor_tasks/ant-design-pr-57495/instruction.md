# Missing Default Colors for Solid Variants

## Problem

When using the `solid` variant for Button and Tag components without explicitly specifying a `color` prop, the components render without proper color styling.

**Button issue:**
- `<Button variant="solid">Click me</Button>` does not apply the expected `ant-btn-color-primary` class
- The same issue occurs when using ConfigProvider: `<ConfigProvider button={{ variant: 'solid' }}><Button>Click me</Button></ConfigProvider>`

**Tag issue:**
- `<Tag variant="solid">Label</Tag>` does not apply the expected `ant-tag-default` class  
- The same issue occurs when using ConfigProvider: `<ConfigProvider tag={{ variant: 'solid' }}><Tag>Label</Tag></ConfigProvider>`

## Expected Behavior

When `variant="solid"` is specified without an explicit `color` prop:
- Button should default to `primary` color (applying `ant-btn-color-primary` class)
- Tag should default to `default` color (applying `ant-tag-default` class)

This should work both when the variant is set directly on the component and when it's set via ConfigProvider.

## Files to Investigate

- `components/button/Button.tsx` - Button component implementation with color/variant logic
- `components/tag/hooks/useColor.ts` - Tag's color resolution hook

## Notes

- When an explicit `color` prop is provided, it should always take precedence over the default
- Non-solid variants (like `outlined`) should continue to work as before without automatic default colors
