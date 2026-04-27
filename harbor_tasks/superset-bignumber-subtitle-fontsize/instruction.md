# Big Number chart: subtitle / subheader default font size is wrong

The Big Number chart (`plugin-chart-echarts`) renders a metric value with an optional smaller "subtitle" line below it. The subtitle line's font size is expressed as a proportion of the chart container — for example, `0.125` means roughly 12.5% of the available height.

## The bug

When the subtitle / subheader font size is **not configured** in the chart's form data, the resolved proportion is `1` (i.e. 100% of the container). That makes the subtitle text far larger than the chart can hold and pushes it outside the visible area. This regularly appears for Big Number charts produced through automated tooling that does not specify a font size at all.

The intended default is the same proportion the rest of the codebase uses for subheader-sized text: `0.125`. Around the codebase, font-size proportions for the various Big Number text elements (kicker, header, metric name, subheader, trendline) are co-located in a single object so that the viz component and its `transformProps` agree on the values.

## What the fix must do

Change the implementation so that, when callers do not set a font size for the subtitle line:

1. The default font size proportion resolves to **0.125** (the subheader proportion), not `1`. This must hold whether the subtitle field is empty, the subtitle field is non-empty, or only the legacy `subheader` field is populated.
2. The two font-size fields (`subtitleFontSize` and `subheaderFontSize`) must not disagree when only one of them is set. Concretely: when the subtitle text comes from the legacy `subheader` field but the caller has only supplied `subtitleFontSize`, the resolved size must still be `subtitleFontSize` (and not snap back to the default). The reverse — only `subheaderFontSize` is set, subtitle empty — must continue to use `subheaderFontSize`.
3. Explicit values supplied by the caller must continue to be honoured for both fields.

The proportion constants used elsewhere in the Big Number viz must remain the single source of truth; whatever default the subtitle resolver picks should reference the existing subheader proportion rather than duplicating the literal `0.125`.

## Where to look

The relevant code lives in:

- `superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/`

Inspect how the Big Number total chart resolves the subtitle font size from its form-data inputs. Inspect how the Big Number viz component declares its proportion constants. Both use the same proportion table — the fix must not introduce a second copy.

## Resolution priority for the subtitle font size

When the subtitle text is non-empty, the resolved size is:

```
explicit subtitleFontSize, otherwise the subheader proportion
```

When the subtitle text is empty (so the subheader text is shown), the resolved size is:

```
explicit subheaderFontSize, otherwise explicit subtitleFontSize, otherwise the subheader proportion
```

## How this is verified

A jest test in `plugins/plugin-chart-echarts/test/BigNumber/` calls the `BigNumberTotal` `transformProps` function with a variety of form-data shapes — no font size at all, only a subtitle, only a subheader, only `subtitleFontSize` with a `subheader` text — and asserts that the returned `subtitleFontSize` field on the viz props is `0.125` (or the explicitly supplied value), never `1`. The pre-existing `BigNumberWithTrendline` test suite must continue to pass.

## Code Style Requirements

- Follow the existing TypeScript style used elsewhere in `plugin-chart-echarts`. New `.ts` / `.tsx` files must include the standard Apache 2.0 license header that every other file in this directory carries.
- No `any` types in new or modified code; reuse existing types from the package.
- The constants file should `export` the proportion table so it can be imported from both the viz component and the `transformProps` resolver.
