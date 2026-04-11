# Fix Collapsible Entry Scroll Jumpiness and Header Layout

## Problem

The collapsible journal entry feature has two UX regressions:

1. **Scroll jumpiness**: Expanding or collapsing an entry causes the page to scroll erratically. After every toggle, the code unconditionally calls `Scrollable.ensureVisible`, which forcibly moves the viewport even when the entry is already fully visible. This is disorienting for the user.

2. **Header layout**: When a collapsible entry is expanded, the date disappears from the header and action icons (flag, AI menu, triple-dot) are placed on the left. The expanded header should match the default header layout: date on the left, action icons on the right.

Additionally, the collapse/expand animation uses `AnimatedSize` which causes content to visually squish from the center rather than smoothly clipping from top to bottom.

## Expected Behavior

1. **Scrolling**: Only auto-scroll when *expanding* an entry AND the card's top edge gets pushed above the visible viewport. Never scroll on collapse. Never scroll when the entry is already visible.

2. **Header layout (expanded)**: Date widget on the left, action icons + chevron grouped on the right — matching the default (non-collapsible) header convention.

3. **Animation**: Collapse/expand should clip content from the top edge, not squish from center. The `CollapsibleSection` widget should also align its `AnimatedSize` to the top.

4. **No duplicate date**: Since the date now appears in the expanded header, remove it from the expanded body content (below image/audio player).

## Files to Look At

- `lib/features/journal/ui/widgets/entry_details_widget.dart` — scroll logic after toggle, expanded body content
- `lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart` — collapsible header layout (`_buildCollapsibleHeader`)
- `lib/widgets/misc/collapsible_section.dart` — generic collapsible section widget with `AnimatedSize`

## Additional Notes

After making the code changes, review and update the project's agent instruction files (`AGENTS.md`) to capture any relevant development guidelines. If the project doesn't have a `CLAUDE.md`, consider creating one. Keep agent configuration files current with practical guidance for working in this codebase.
