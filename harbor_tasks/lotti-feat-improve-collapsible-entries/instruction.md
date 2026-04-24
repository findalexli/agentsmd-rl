# Fix Collapsible Entry Scroll Jumpiness, Header Layout, and Animation

## Problem

The collapsible journal entry feature has several UX regressions:

1. **Scroll jumpiness**: Expanding or collapsing an entry causes erratic scrolling. After every toggle, `Scrollable.ensureVisible` is called unconditionally, moving the viewport even when the entry is already fully visible.

2. **Header layout**: When a collapsible entry is expanded, the date disappears from the header and action icons are placed on the left. The expanded header should show `EntryDatetimeWidget` (date) on the left and action icons on the right — matching the default (non-collapsible) header.

3. **Animation squish**: The collapse/expand animation uses `AnimatedSize` which causes content to squish from the center rather than clipping smoothly from the top edge. Additionally, the generic `CollapsibleSection` widget's `AnimatedSize` lacks top alignment, so content expands from center instead of downward from the header.

4. **Duplicate date**: The date currently appears in both the expanded header area and in the expanded body content below the image/audio player.

## Expected Behavior

### 1. Viewport-Aware Conditional Scroll (`entry_details_widget.dart`)

After toggling an entry's collapse state, the scroll logic must be conditional — only auto-scroll when expanding AND the entry's top edge is pushed above the visible viewport. The implementation must:

- Import `package:flutter/rendering.dart` to access viewport APIs.
- Determine whether the toggle is an expand or collapse, storing this as a `final isExpanding` variable.
- Use `RenderAbstractViewport.maybeOf` for a safe (nullable) viewport lookup and `Scrollable.maybeOf` for a safe scrollable lookup.
- Guard the `Scrollable.ensureVisible` call inside an `if (isExpanding)` block — never scroll on collapse.

### 2. Expanded Header Shows Date (`entry_detail_header.dart`)

The expanded (non-collapsed) header must include `EntryDatetimeWidget`. The widget should appear in at least one `if (!widget.isCollapsed)` conditional block so that both collapsed and expanded states render the date widget. The expanded header should show date on the left, action icons on the right.

### 3. SizeTransition-Based Collapse Animation (`entry_details_widget.dart`)

Replace the bare `AnimatedSize` body animation with a private `_CollapsibleBody` StatefulWidget (and corresponding `_CollapsibleBodyState`). This widget must:

- Use Flutter's `SizeTransition` widget (not bare `AnimatedSize`) for the collapse/expand animation, configured with `sizeFactor` (bound to an `AnimationController`) and `axisAlignment` for top-aligned expansion.
- Layer a `FadeTransition` on top (bound to an opacity animation) for smooth fade during collapse/expand.
- Implement `didUpdateWidget` in the state class to call `_controller.forward()` when expanding and `_controller.reverse()` when collapsing, responding to `isCollapsed` property changes.
- The build tree must instantiate `_CollapsibleBody(...)` where the body content is rendered.

### 4. AnimatedSize Top Alignment (`collapsible_section.dart`)

The `AnimatedSize` widget in the generic `CollapsibleSection` must use `Alignment.topCenter` (or equivalent top alignment) as its alignment parameter so content expands downward from the header rather than squishing from the center.

### 5. Remove Duplicate Date from Expanded Body (`entry_details_widget.dart`)

Since the date now appears in the expanded header:
- Remove the `datePadding` variable.
- Remove the `entry_datetime_widget.dart` import from this file (the widget is used in the header file instead).
- Ensure `EntryDatetimeWidget` does not appear in the `expandedContent` section.

## Files

- `lib/features/journal/ui/widgets/entry_details_widget.dart`
- `lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart`
- `lib/widgets/misc/collapsible_section.dart`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
