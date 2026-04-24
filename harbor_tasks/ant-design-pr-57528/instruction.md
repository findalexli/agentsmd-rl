# Popconfirm Icon Semantic Styling Support

The Popconfirm component supports semantic styling through `classNames` and `styles` props. However, the confirmation icon element does not currently receive these semantic values when using `classNames.icon` or `styles.icon`.

## Problem

When using the Popconfirm component with semantic styling, developers cannot apply custom classes or styles to the confirmation icon element. The `icon` slot is missing from the Popconfirm semantic type definitions, and the icon element in the rendered output does not receive the semantic class or style values.

## Expected Behavior

The Popconfirm component must support `classNames.icon` and `styles.icon` properties for semantic styling of the confirmation icon element.

### Requirements

1. **Type definitions must include icon support**: The semantic type definitions should include an `icon` property in both `classNames` and `styles`, allowing developers to pass custom classes and inline styles to the icon element.

2. **Rendering must apply semantic values**: When `classNames.icon` is provided, the icon element's class attribute should include the custom class. When `styles.icon` is provided, the icon element should receive those inline styles.

3. **Backward compatibility**: The fix must not break existing functionality. All existing Jest tests, ESLint checks, and Biome linting should continue to pass.

## Testing

After implementing the fix:
- The Popconfirm component should pass all existing Jest tests
- ESLint checks should pass for modified files
- Biome linting should pass for modified files
