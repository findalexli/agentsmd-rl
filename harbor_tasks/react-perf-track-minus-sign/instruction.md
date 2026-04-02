# React Performance Tracks: Incorrect character for removed props

In the performance tracking visualization, when props are removed from a component, the diff view shows them with an incorrect character prefix. This causes inconsistency with other diff displays in React (like hydration diffs) and with standard diff tools like git.

The issue is in the performance track properties rendering code. When a prop is removed, it should display with a standard minus sign (the `-` character, ASCII 45) rather than a typographic en dash. This ensures visual consistency across all React diff outputs and matches developer expectations.

Look at `packages/shared/ReactPerformanceTrackProperties.js` where removed props are prefixed for display in the performance tracks.
