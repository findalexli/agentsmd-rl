# Bug Report: Task Tracking Shows Misleading Loading Animation

## Problem Description

In the OpenHands frontend task tracking component, tasks with `status="in_progress"` display a `LoadingIcon` with the `animate-spin` class. This animated spinner continues spinning even after a task completes, creating a confusing user experience because the animation suggests ongoing activity when the task has actually finished.

## Affected Components

There are two TaskItem component implementations with this issue:

1. `frontend/src/components/features/chat/task-tracking/task-item.tsx`
2. `frontend/src/components/v1/chat/task-tracking/task-item.tsx`

Both have a `getTaskIcon` function that returns icons for three states:
- `"todo"` - returns `CircleIcon`
- `"in_progress"` - returns `LoadingIcon` with `animate-spin` class (problematic)
- `"done"` - returns `CheckCircleIcon`

## Expected Behavior

1. **New icon file**: Create `frontend/src/icons/u-check-circle-half.svg` containing an SVG that visually represents a "half-checked" or "in progress" state. The icon should use `currentColor` for stroke/fill and follow the same 16x16 viewBox pattern as existing circle icons in the project.

2. **Icon imports**: The component imports should reference `CheckCircleHalfIcon` from `#/icons/u-check-circle-half.svg?react` instead of `LoadingIcon`.

3. **in_progress state rendering**: When `status === "in_progress"`, the component should render `CheckCircleHalfIcon` with className containing `w-4 h-4` and appropriate text color, but WITHOUT the `animate-spin` class.

4. **Other states unchanged**: The `"todo"` case should continue using `CircleIcon` and the `"done"` case should continue using `CheckCircleIcon`.

## Acceptance Criteria

- [ ] New SVG icon file exists at `frontend/src/icons/u-check-circle-half.svg`
- [ ] Both TaskItem components import `CheckCircleHalfIcon` (not `LoadingIcon`)
- [ ] The `"in_progress"` case returns `CheckCircleHalfIcon` without `animate-spin` class
- [ ] The `"todo"` and `"done"` cases continue using their respective icons (`CircleIcon`, `CheckCircleIcon`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Linting passes (`npm run lint`)
- [ ] TypeScript type checking passes (`npx tsc --noEmit`)
