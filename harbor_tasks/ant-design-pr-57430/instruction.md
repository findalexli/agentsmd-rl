# Add itemContent semantic styling support for Calendar

The Calendar component in Ant Design supports semantic styling through `classNames` and `styles` props, allowing developers to customize different parts of the calendar. Currently, semantic keys exist for `root`, `header`, `body`, `content`, and `item`.

However, there's a missing capability: developers cannot style the **content area inside calendar cells** (the container that holds custom content from `cellRender` / `dateCellRender` / `monthCellRender`). This area has a specific DOM element with the class `ant-picker-calendar-date-content`, but there's no semantic API to customize it.

## The Problem

When using `cellRender` to add custom content to calendar cells, developers need to control the styling of the container div that wraps their custom content (for example, to set a specific height, control overflow behavior, or add padding). Currently, they must resort to CSS overrides targeting internal class names, which is fragile and not aligned with the semantic styling API design.

## What Needs to Be Done

Add support for an `itemContent` semantic key in the Calendar component's `classNames` and `styles` props. This should:

1. Accept custom class names via `classNames.itemContent`
2. Accept custom inline styles via `styles.itemContent`
3. Apply these to the date-content container element in both month view and year view modes

## Files to Modify

- `components/calendar/generateCalendar.tsx` - The main Calendar component implementation

## Acceptance Criteria

- The Calendar component accepts `itemContent` in both `classNames` and `styles` props
- Custom classes are properly merged with the existing `date-content` class using `clsx`
- Custom styles are applied as inline styles to the date-content element
- Both date cells (month view) and month cells (year view) support this customization
- TypeScript types are properly updated in `CalendarSemanticType`
