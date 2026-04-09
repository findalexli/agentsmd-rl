# Task: Add Default Colors for Solid Variants

## Problem

When using `variant="solid"` on Button or Tag components without explicitly specifying a `color` prop, the components do not receive a default color assignment. This causes styling issues where the solid variant doesn't have proper color styling applied.

## Expected Behavior

1. **Button** with `variant="solid"` and no explicit `color` should automatically get `color="primary"`
2. **Tag** with `variant="solid"` and no explicit `color` should automatically get `color="default"`
3. These defaults should also apply when using **ConfigProvider** to set the variant globally
4. Non-solid variants should NOT receive default colors (to avoid breaking existing behavior)

## Files to Modify

- `components/button/Button.tsx` - Add default color logic for Button
- `components/tag/hooks/useColor.ts` - Add default color logic for Tag

## Hints

Look for where the color/variant pairs are computed in both components. The logic should:
- Check if `variant === 'solid'` and `color` is not explicitly set
- Return the appropriate default color in that case
- Handle both direct prop usage and ConfigProvider context values

## Verification

When fixed, the components should have these CSS classes applied:
- `<Button variant="solid">` → should have `ant-btn-variant-solid` AND `ant-btn-color-primary`
- `<Tag variant="solid">` → should have `ant-tag-solid` AND `ant-tag-default`
- ConfigProvider with `button={{ variant: 'solid' }}` → Button gets same classes
- ConfigProvider with `tag={{ variant: 'solid' }}` → Tag gets same classes
- `<Tag variant="outlined">` → should NOT have `ant-tag-default`
