# Improve Project Detail Scroll Performance

## Problem

The project detail page (`/projects/:projectId`) uses a `SingleChildScrollView` wrapping a `Column` to render the entire detail view — header, health panel, AI report, and the full task list. When a project has many linked tasks (50+), fast downward scrolling causes visible shudder and jank because every task row is eagerly laid out, even those far off-screen.

## Expected Behavior

The task list portion of the project detail page should render lazily — only building task rows that are actually visible or near the viewport. The static header sections (project metadata, health panel, AI report) can remain eagerly rendered since they are always near the top.

### Scroll container refactoring

The detail content file should replace `SingleChildScrollView` with a `CustomScrollView` that accepts a `slivers:` list. Within that list, the existing static header sections — specifically the `_ProjectMobileHeader` widget and the `HealthPanel` widget — should each be wrapped in a `SliverToBoxAdapter` so they remain eagerly rendered inside the sliver scroll view.

The detail content should reference the new sliver task panel (see below) instead of the old eager `ProjectTasksPanel` widget.

### New sliver-compatible task panel

Create a new widget class called `ProjectTasksSliverPanel` that extends `StatelessWidget` in the tasks panel file. It should have a `build` method returning a `Widget` and accept a `ProjectRecord` typed parameter.

Internally, `ProjectTasksSliverPanel` should use a `SliverList` with an `itemBuilder` callback and an `itemCount` property to lazily construct `TaskSummaryRow` widgets for each task. This is what enables lazy rendering — only rows near the viewport are built.

### Preserve existing code

The existing `ProjectTasksPanel` used in other contexts (like the settings detail page) should remain functional — the lazy rendering is specifically for the top-level detail route.

## Files to Look At

- `lib/features/projects/ui/widgets/project_mobile_detail_content.dart` — the detail view scroll container that currently uses `SingleChildScrollView`
- `lib/features/projects/ui/widgets/project_tasks_panel.dart` — the task list panel widget; add the new `ProjectTasksSliverPanel` class here
- `lib/features/projects/README.md` — feature documentation; keep it up to date with architectural changes per project conventions
