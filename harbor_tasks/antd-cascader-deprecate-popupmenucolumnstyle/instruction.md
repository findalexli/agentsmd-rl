# Task: Fix Cascader Deprecation Documentation Inconsistency

## Problem

The Cascader component has a circular deprecation path that confuses users.

When users use the deprecated `dropdownMenuColumnStyle` property, they receive a deprecation warning suggesting `popupMenuColumnStyle` as the replacement. However, `popupMenuColumnStyle` is itself also deprecated. Following the deprecation guidance leads users in circles.

According to the v6 migration documentation, the correct replacement API is `styles.popup.listItem`. All deprecation warnings, JSDoc comments, and API documentation should consistently guide users to this specific replacement.

## Files Involved

- `components/cascader/index.tsx` - Contains JSDoc comments and deprecation mappings
- `components/cascader/__tests__/index.test.tsx` - Contains unit test expectations for deprecation warnings
- `components/cascader/index.en-US.md` - English API documentation
- `components/cascader/index.zh-CN.md` - Chinese API documentation
- `docs/react/migration-v6.en-US.md` - English v6 migration guide
- `docs/react/migration-v6.zh-CN.md` - Chinese v6 migration guide

## Required Behavior

Fix the circular deprecation documentation so that all references consistently point to `styles.popup.listItem`:

1. **Deprecation Mapping**: The `deprecatedProps` object (which defines which properties are deprecated and what replacements to suggest) must map both `dropdownMenuColumnStyle` and `popupMenuColumnStyle` to the replacement value `styles.popup.listItem`.

2. **JSDoc Comments**: All JSDoc `@deprecated` comments for these properties must reference `styles.popup.listItem` as the replacement.

3. **English API Documentation**: The `index.en-US.md` file must reference `styles.popup.listItem` as the replacement for both `dropdownMenuColumnStyle` and `popupMenuColumnStyle`.

4. **Chinese API Documentation**: The `index.zh-CN.md` file must reference `styles.popup.listItem` as the replacement for both `dropdownMenuColumnStyle` and `popupMenuColumnStyle`.

5. **Migration Documentation**: Both `migration-v6.en-US.md` and `migration-v6.zh-CN.md` must reference `styles.popup.listItem` as the replacement for `dropdownMenuColumnStyle`.

6. **Unit Test Expectations**: The unit tests in `__tests__/index.test.tsx` must expect the warning message: "`dropdownMenuColumnStyle` is deprecated. Please use `styles.popup.listItem` instead."

## Constraints

- Do NOT change any functional behavior of the Cascader component
- Do NOT add new features or properties
- Do NOT suggest `popupMenuColumnStyle` as a replacement anywhere
