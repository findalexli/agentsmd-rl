# Fix clipped label filters on the Tasks page

## Problem

On the Tasks page, when label filters are active, the selected label chips are placed inside the `SliverAppBar`'s `title` column (via `TaskLabelQuickFilter`). The app bar has a fixed `toolbarHeight: 100`, so when multiple labels are selected and the chips wrap to multiple rows, they get clipped — the user cannot see or interact with them.

## Expected Behavior

1. **Active label filters should always be fully visible** below the search bar, even when many labels are selected and chips wrap to multiple rows.
2. The quick filter section should have a **compact, polished design** — a filter icon, a count of active filters in the title, compact chip density, and a compact Clear button with an icon.
3. The filter section should **animate smoothly** when filters appear or disappear.
4. When no filters are active, no empty container should be rendered.

## Files to Look At

- `lib/widgets/app_bar/journal_sliver_appbar.dart` — The app bar that currently embeds `TaskLabelQuickFilter` in its `title` column, causing the clipping
- `lib/features/journal/ui/pages/infinite_journal_page.dart` — The page that renders the `CustomScrollView` with sliver children; this is where the filter section should live
- `lib/features/tasks/ui/filtering/task_label_quick_filter.dart` — The quick filter widget itself, which needs visual redesign (icon, count, compact layout)

## Additional Context

The project's `AGENTS.md` guidelines require updating feature README files alongside code changes to reflect the current state of the codebase. After fixing the clipping issue and redesigning the quick filter, update the relevant feature documentation to describe the new behavior and placement. The CHANGELOG should also be updated.
