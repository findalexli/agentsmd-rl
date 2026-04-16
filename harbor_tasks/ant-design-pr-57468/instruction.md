# TimePicker Column Scroll Issue on Touch Devices

## Problem

Users on touch devices (tablets, mobile phones) cannot scroll through the time selection columns in the TimePicker component. The time columns appear frozen and do not respond to touch/swipe gestures.

Interestingly, after tapping on the time column area once, scrolling sometimes starts working temporarily. This inconsistent behavior suggests the issue is related to how touch interactions are handled.

## Affected Component

The issue is in the TimePicker panel styling, specifically in `components/date-picker/style/panel.ts`. The time panel columns (hours, minutes, seconds) are affected.

## Expected Behavior

Users should be able to scroll through time options using touch gestures on mobile and tablet devices without needing to tap first.

## Steps to Reproduce

1. Open a page with a TimePicker component on a touch device (or use mobile emulation in browser dev tools)
2. Click/tap to open the time picker dropdown
3. Try to scroll through the hour/minute/second columns using touch gestures
4. Observe that scrolling does not work initially

## Technical Context

The TimePicker uses CSS-in-JS styling via `@ant-design/cssinjs`. The time panel columns have specific overflow styling that controls scrolling behavior. The issue appears to be related to how CSS pseudo-selectors interact with touch events.
