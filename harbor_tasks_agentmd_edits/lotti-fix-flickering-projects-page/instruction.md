# Flickering project detail page on related-task updates

## Problem

When a linked task or task-agent report updates, the project detail page
(`lib/features/projects/ui/pages/project_details_page.dart`) reloads the
derived `ProjectRecord` from its Riverpod async provider. During the reload,
the page shows a full-screen loading spinner — replacing all visible content.
This causes the page to flicker and resets the user's scroll position every
time a background update arrives.

## Expected Behavior

The page should keep showing the previously loaded project detail content while
the provider reloads. The user should not see a loading spinner or lose their
scroll position during live refreshes triggered by task or report changes.

## Hints

- Look at the `recordAsync.when(…)` call in `ProjectDetailsPage.build`.
  Riverpod's `AsyncValue.when` has parameters that control what happens during
  a reload versus the initial load.
- After fixing the code, update the feature README at
  `lib/features/projects/README.md` to document the new reload behavior.
  The project's documentation standards require feature READMEs to reflect
  actual runtime behavior.

## Files to Look At

- `lib/features/projects/ui/pages/project_details_page.dart` — the page widget
  that renders the async project record
- `lib/features/projects/README.md` — feature documentation that should describe
  the page's behavior during reloads
