# Improve due date display for completed and rejected tasks

## Problem

In the Lotti task management app, due dates are shown with urgency styling (red/orange colors) on task cards and in the entry detail view regardless of whether the task is completed or rejected. Once a task is done or rejected, the due date is no longer actionable, so showing it with urgent styling creates visual noise and misleads the user into thinking action is needed.

## Required Changes

### 1. Task Card Due Date Visibility

**File**: `lib/features/journal/ui/widgets/list_cards/modern_task_card.dart`

The date rendering on task cards must be updated so that tasks with `TaskDone` or `TaskRejected` status do not display a due date chip at all. This requires importing `lib/classes/task.dart` to access the task status types and gating the due date display behind a completion status check.

### 2. Entry Detail Due Date Styling

**File**: `lib/features/tasks/ui/header/task_due_date_wrapper.dart`

The due date chip in the entry detail view must be updated so that completed or rejected tasks display a neutral, grayed-out style instead of urgency styling (no red/orange colors). The due date remains visible for historical context. This requires importing `lib/classes/task.dart` and checking the task's completion status before applying urgency styling.

### 3. Test Files

Create or verify the following test files exist and contain test definitions (`testWidgets`, `test()`, or `group()`):

- `test/features/journal/ui/widgets/list_cards/modern_task_card_test.dart`
- `test/features/tasks/ui/header/task_due_date_wrapper_test.dart`

### 4. Documentation Updates

**CHANGELOG.md**:
- Must mention "Due Date Visibility Refinements" heading for the new version entry
- Must document that due dates are hidden on task cards for completed/rejected tasks and shown with grayed-out styling in entry details

**README.md**:
- Replace "Coming Soon: Deep Dive Series" text with content referencing the live "Meet Lotti" blog series
- Add reference to the blog series and include the Substack link: `https://matthiasnehlsen.substack.com/p/meet-lotti`

### 5. Flatpak Metadata

**flatpak/com.matthiasn.lotti.metainfo.xml**:
- Must be valid XML with root `<component>` element
- Must contain `<id>com.matthiasn.lotti</id>`

**flatpak/com.matthiasn.lotti.source.yml**:
- Must be valid YAML
- Must contain `app-id: com.matthiasn.lotti`

### 6. CI Validation

The following commands must pass (run from the `flatpak/manifest_tool/` directory):

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

The "Meet Lotti" blog series has launched on Substack and the README and related project metadata should be updated to reflect its live status.