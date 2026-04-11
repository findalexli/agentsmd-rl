# Improve Project Detail Scroll Performance

## Problem

The project detail page (`/projects/:projectId`) uses a `SingleChildScrollView` wrapping a `Column` to render the entire detail view — header, health panel, AI report, and the full task list. When a project has many linked tasks (50+), fast downward scrolling causes visible shudder and jank because every task row is eagerly laid out, even those far off-screen.

## Expected Behavior

The task list portion of the project detail page should render lazily — only building task rows that are actually visible or near the viewport. The static header sections (project metadata, health panel, AI report) can remain eagerly rendered since they are always near the top.

Flutter's sliver-based scrolling APIs (`CustomScrollView`, `SliverList`, `SliverToBoxAdapter`, etc.) are the standard approach for mixing fixed header content with a lazily-rendered list within a single scrollable.

The existing `ProjectTasksPanel` used in other contexts (like the settings detail page) should remain functional — the lazy rendering is specifically for the top-level detail route.

## Files to Look At

- `lib/features/projects/ui/widgets/project_mobile_detail_content.dart` — the detail view scroll container that currently uses `SingleChildScrollView`
- `lib/features/projects/ui/widgets/project_tasks_panel.dart` — the task list panel widget; you'll likely need a sliver-compatible variant
- `lib/features/projects/README.md` — feature documentation; keep it up to date with architectural changes per project conventions
