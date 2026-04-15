# Improve due date display for completed and rejected tasks

## Problem

In the Lotti task management app, due dates are shown with urgency styling (red/orange colors) on task cards and in the entry detail view regardless of whether the task is completed or rejected. This is confusing — once a task is done or rejected, the due date is no longer actionable, so showing it with urgent styling (or showing it at all on the card) creates visual noise and misleads the user into thinking action is needed.

## Required Changes

### 1. Task Card Due Date Visibility

**File**: `lib/features/journal/ui/widgets/list_cards/modern_task_card.dart`

The `_buildDateRow` method currently renders due dates for all tasks. Modify it such that:
- The due date chip is **completely hidden** for tasks with `TaskDone` or `TaskRejected` status
- The implementation must reference `TaskDone` and/or `TaskRejected` types from `lib/classes/task.dart`
- The `hasDueDate` variable assignment must be gated by completion status (check `!isCompleted` or equivalent before showing due date)

### 2. Entry Detail Due Date Styling

**File**: `lib/features/tasks/ui/header/task_due_date_wrapper.dart`

The `build` method currently applies `isUrgent` and `urgentColor` styling for all tasks. Modify it such that:
- Import `package:lotti/classes/task.dart` for status type checking
- The due date chip remains **visible** for historical context, but uses grayed-out / neutral styling
- `isUrgent` must be gated by completion status (e.g., `!isCompleted && status.isUrgent` pattern)
- `urgentColor` must be `null` for completed/rejected tasks (ternary check for `isCompleted`)
- The implementation must reference `TaskDone` and/or `TaskRejected` types

### 3. Test Files

Create or verify the following test files exist and contain test definitions (`testWidgets`, `test()`, or `group()`):

- `test/features/journal/ui/widgets/list_cards/modern_task_card_test.dart`
- `test/features/tasks/ui/header/task_due_date_wrapper_test.dart`

### 4. Documentation Updates

**CHANGELOG.md**:
- Must mention "due date" changes
- Must reference "completed" and/or "rejected" tasks in context of due date visibility changes

**README.md**:
- Replace "Coming Soon: Deep Dive" text (must be removed entirely)
- Add reference to "meet-lotti" blog series
- Include link to `matthiasnehlsen.substack.com/p/meet-lotti`

### 5. Flatpak Metadata

**flatpak/com.matthiasn.lotti.metainfo.xml**:
- Must be valid XML with root `<component>` element
- Must contain `<id>com.matthiasn.lotti</id>`

**flatpak/com.matthiasn.lotti.source.yml**:
- Must be valid YAML
- Must contain `app-id: com.matthiasn.lotti`

### 6. CI Validation

The following commands must pass in `flatpak/manifest_tool`:

```bash
# Python linting
flake8 . --count --max-line-length=120 --extend-ignore=E203,W503

# Manifest tool tests
pytest tests/ -v --tb=short
pytest tests/test_validation.py -v --tb=short
```

## Files to Look At

- `lib/features/journal/ui/widgets/list_cards/modern_task_card.dart`
- `lib/features/tasks/ui/header/task_due_date_wrapper.dart`
- `lib/classes/task.dart` — Contains `TaskDone` and `TaskRejected` status types
- `test/features/journal/ui/widgets/list_cards/modern_task_card_test.dart`
- `test/features/tasks/ui/header/task_due_date_wrapper_test.dart`
- `README.md`
- `CHANGELOG.md`
- `flatpak/com.matthiasn.lotti.metainfo.xml`
- `flatpak/com.matthiasn.lotti.source.yml`
- `flatpak/manifest_tool/`

## Additional Context

The "Meet Lotti" blog series has launched on Substack and the README and related project metadata should be updated to reflect its live status. Follow the project's AGENTS.md guidelines for documentation updates.
