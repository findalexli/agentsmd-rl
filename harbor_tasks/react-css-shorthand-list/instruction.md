# Bug Report: Missing CSS logical and shorthand properties in React DOM shorthand-to-longhand mapping

## Problem

React's CSS shorthand property expansion is missing many modern CSS shorthand properties. When using CSS logical properties like `borderBlock`, `borderInline`, `inset`, `marginBlock`, `paddingInline`, `scrollMarginBlock`, and others as inline styles, React does not correctly recognize them as shorthands. This causes issues when transitioning between shorthand and longhand properties — React cannot properly clear previously set longhand values because it doesn't know which longhands a given shorthand expands to.

The shorthand-to-longhand mapping was derived from an older version of the Firefox/Gecko source and has not been updated to reflect newer CSS properties that browsers now widely support.

## Expected Behavior

All standard CSS shorthand properties — including logical properties (`borderBlock`, `borderInline`, `inset`, `marginBlock`, `paddingBlock`, `marginInline`, `paddingInline`, `scrollMargin`, `scrollPadding`, etc.), `container`, `containIntrinsicSize`, `fontSynthesis`, and others — should be recognized as shorthands and correctly expand to their constituent longhand properties.

## Actual Behavior

Modern CSS shorthand properties are absent from the mapping, so React does not track their longhand expansions. This can lead to stale longhand values persisting when switching between shorthand and longhand forms in inline styles.

## Files to Look At

- `packages/react-dom-bindings/src/client/CSSShorthandProperty.js`
