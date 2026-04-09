# Improve MLflow Traces Table Column Selector UI

## Problem

The current traces table column selector in the MLflow UI uses a flat `DialogCombobox` structure that becomes unwieldy when there are many assessment and expectation columns. Users struggle to:
- Navigate and understand column organization
- Select/deselect groups of columns efficiently
- Find specific columns in large lists

The component also has UI lag when expanding/collapsing sections.

## Expected Behavior

Convert the flat column selector to a hierarchical tree structure with the following improvements:

1. **Tree-based Column Selector**: Replace `DialogCombobox` with a `Tree` component using `Dropdown` + `Input` for search. Group columns into collapsible categories (Attributes, Assessments, Expectations, Parameters, Tags).

2. **Search Functionality**: Add a search input with icon that filters both group names and column names, with matching text highlighted.

3. **Performance Optimization**: Use `useCallback` for event handlers, disable tree animations (`motion: null`), and memoize dropdown content to eliminate UI lag.

4. **Apply Throughout**: Update `GenAITracesTable.tsx` to use the improved `EvaluationsOverviewColumnSelectorGrouped` component with the new props (`toggleColumns`, `setSelectedColumns`).

## Files to Modify

- `mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx` - Main component rewrite with tree structure, search, and performance optimizations
- `mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx` - Update to use improved component with correct props

## Key Implementation Details

1. Import new components from `@databricks/design-system`: `Dropdown`, `Input`, `SearchIcon`, `Tree`
2. Add `useCallback` import from React
3. Create `getGroupKey()` helper for group identifiers
4. Implement `createHighlightedNode()` for search highlighting
5. Replace `DialogCombobox` + `DialogComboboxContent` with `Dropdown` + memoized `dropdownContent`
6. Add search input with `SearchIcon` prefix
7. Use `Tree` component with `mode="checkable"`, `motion: null` for performance
8. Handle both group-level and individual column selection in `handleCheck`
