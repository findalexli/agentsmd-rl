# React DevTools: Empty State for Root Elements Without Suspenders

## Problem

In React DevTools, when inspecting the root element of an application, the "Inspected Element" pane shows nothing if there are no Suspense-related components that have suspended rendering. This happens in several common scenarios:

- Using older versions of React without Suspense support
- Applications that don't use Suspense boundaries
- Simple UIs that don't have any components that suspend

This creates a confusing user experience where the DevTools appears to not be working correctly—the panel is simply empty with no indication of why or what state the application is in.

## Your Task

Modify the `InspectedElementSuspendedBy` component in React DevTools to show a helpful empty state message when inspecting root elements that have no suspended components. Instead of rendering nothing, the component should display an informative message explaining that nothing has suspended the initial paint.

## Relevant Files

- `packages/react-devtools-shared/src/devtools/views/Components/InspectedElementSuspendedBy.js` - The component that displays what has suspended an element

## Expected Behavior

When a root element is inspected and there are no suspenders:
1. The component should detect that the inspected element is a root type
2. Display a message indicating that nothing has suspended the initial paint
3. Use consistent styling with the rest of the DevTools UI

## Notes

- The component already handles various cases for displaying suspension information
- You may need to check what type of element is being inspected
- The existing styling classes should be reused for consistency
