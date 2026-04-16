# Cascader Component Deprecation Warning Inconsistency

## Problem Description

The Cascader component has a problematic deprecation migration path for column styling props. When developers use the deprecated `dropdownMenuColumnStyle` prop, the deprecation warning directs them to use `popupMenuColumnStyle` as the replacement. However, `popupMenuColumnStyle` is itself also deprecated in the codebase, creating a confusing migration path where developers are instructed to migrate from one deprecated API to another deprecated API.

The correct behavior should be: both `dropdownMenuColumnStyle` and `popupMenuColumnStyle` should direct users to a single, consistent, non-deprecated replacement API, so developers are pointed to the final answer rather than caught in a deprecation chain.

## Files to Investigate

- `components/cascader/index.tsx` - Contains the Cascader component implementation, deprecation warning mappings, and TypeScript interface with JSDoc comments
- `components/cascader/index.en-US.md` - English API documentation
- `components/cascader/index.zh-CN.md` - Chinese API documentation
- `docs/react/migration-v6.en-US.md` - v6 migration guide documentation

## Expected Behavior

### 1. Deprecation Warning Mappings (in `components/cascader/index.tsx`)

The deprecation mapping object in the component should map both properties to the same final replacement API. Both `dropdownMenuColumnStyle` and `popupMenuColumnStyle` should have entries in the deprecation mapping that point to this replacement. The replacement API uses the pattern `styles.popup.listItem` (a `styles.popup.*` token).

### 2. JSDoc Comments (in `components/cascader/index.tsx`)

The TypeScript interface should have JSDoc `@deprecated` tags on both `popupMenuColumnStyle` and `dropdownMenuColumnStyle` that reference the same replacement API (using the same literal string format for both).

### 3. English API Documentation (in `components/cascader/index.en-US.md`)

In the API property table, both `popupMenuColumnStyle` and `dropdownMenuColumnStyle` should appear with strikethrough markdown syntax (~~propName~~) to indicate they are deprecated. The description for each should reference the final replacement API.

### 4. Chinese API Documentation (in `components/cascader/index.zh-CN.md`)

In the API property table, both `popupMenuColumnStyle` and `dropdownMenuColumnStyle` should appear with strikethrough markdown syntax. The description for each should reference the final replacement API.

### 5. Migration Guide (in `docs/react/migration-v6.en-US.md`)

The migration documentation for the Cascader component should state that `dropdownMenuColumnStyle` is deprecated and describe the correct replacement. It should clearly indicate what developers should use instead.

## Current Incorrect Behavior

Currently, the deprecation chain creates a two-step migration:
1. `dropdownMenuColumnStyle` → points to `popupMenuColumnStyle`
2. `popupMenuColumnStyle` → was not deprecated (no warning mapping exists)

This means developers following the first warning would end up using another deprecated API instead of going directly to the final replacement.