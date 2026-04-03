# Align Design-System Typography and Spacing with Exported Tokens

## Problem

Several design-system components under `lib/features/design_system/components/` use hardcoded pixel values for spacing (e.g., `const SizedBox(width: 16)`, `const EdgeInsets.all(8)`) and reach into `Theme.of(context).textTheme` with manual `fontSize`/`fontWeight` overrides instead of using the project's design-token system (`context.designTokens`).

This makes the components drift from the Figma-exported token definitions and breaks the single-source-of-truth principle for the design system.

Additionally, the time picker hardcodes `'AM'` and `'PM'` strings instead of using the locale-aware labels from `MaterialLocalizations`, so the picker ignores the device language setting.

## Expected Behavior

1. **Token-sourced spacing**: All hardcoded spacing constants in these components should be replaced with references to `tokens.spacing.stepN` (the design-token spacing scale).
2. **Token-sourced typography**: Text styles that currently use `Theme.of(context).textTheme.*?.copyWith(fontSize: ..., fontWeight: ...)` should instead use the appropriate token typography style (e.g., `tokens.typography.styles.others.caption`, `tokens.typography.styles.subtitle.subtitle1`, `tokens.typography.styles.body.bodyMedium`).
3. **Token-sourced font weight**: Hardcoded `FontWeight.wNNN` values should use `tokens.typography.weight.*` instead.
4. **Localized AM/PM**: The 12-hour time picker should use `MaterialLocalizations.of(context).anteMeridiemAbbreviation` and `postMeridiemAbbreviation` for the period labels.
5. **README update**: The design-system feature README should be updated to reflect the current set of implemented components and the design-token sourcing convention.

## Files to Look At

- `lib/features/design_system/components/calendar_pickers/design_system_time_calendar_picker.dart` — calendar/date picker with weekday labels, month headers, day buttons
- `lib/features/design_system/components/navigation/design_system_navigation_tab_bar.dart` — bottom navigation with icon + label tabs
- `lib/features/design_system/components/task_filters/design_system_task_filter_sheet.dart` — filter sheet with sort options, selection fields, action buttons
- `lib/features/design_system/components/task_list_items/design_system_task_list_item.dart` — task list row with priority metadata
- `lib/features/design_system/components/time_pickers/design_system_time_picker.dart` — drum-style time picker with AM/PM column
- `lib/features/design_system/components/toasts/design_system_toast.dart` — toast notification component
- `lib/features/design_system/README.md` — feature README documenting scope and components
