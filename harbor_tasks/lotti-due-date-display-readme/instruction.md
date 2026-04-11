# Improve due date display for completed and rejected tasks

## Problem

In the Lotti task management app, due dates are shown with urgency styling (red/orange colors) on task cards and in the entry detail view regardless of whether the task is completed or rejected. This is confusing — once a task is done or rejected, the due date is no longer actionable, so showing it with urgent styling (or showing it at all on the card) creates visual noise and misleads the user into thinking action is needed.

## Expected Behavior

1. **Task cards** (`ModernTaskCard`): Due dates should be **hidden entirely** for tasks with "Done" or "Rejected" status. The date row should not render the due date chip for these tasks.

2. **Entry detail view** (`TaskDueDateWrapper`): The due date chip should still be visible (for historical context), but it should use **grayed-out / neutral styling** instead of red/orange urgency colors. The `isUrgent` flag and `urgentColor` should be suppressed for completed/rejected tasks.

## Files to Look At

- `lib/features/journal/ui/widgets/list_cards/modern_task_card.dart` — The `_buildDateRow` method controls whether the due date is shown on task cards
- `lib/features/tasks/ui/header/task_due_date_wrapper.dart` — The `build` method controls urgency styling for the due date in the detail view
- `lib/classes/task.dart` — Contains `TaskDone` and `TaskRejected` status types

## Additional Context

The "Meet Lotti" blog series has launched on Substack. The README and related project metadata still reference it as "coming soon" and should be updated to reflect its live status. Don't forget to update documentation to match the current state of the project, as the project's AGENTS.md guidelines require.
