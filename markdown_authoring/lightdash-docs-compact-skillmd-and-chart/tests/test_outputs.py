"""Behavioral checks for lightdash-docs-compact-skillmd-and-chart (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lightdash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/SKILL.md')
    assert 'Dashboards arrange charts and content in a grid layout. See [Dashboard Reference](./resources/dashboard-reference.md) for YAML structure, tile types, tabs, and filters.' in text, "expected to find: " + 'Dashboards arrange charts and content in a grid layout. See [Dashboard Reference](./resources/dashboard-reference.md) for YAML structure, tile types, tabs, and filters.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/SKILL.md')
    assert '| Define metrics & dimensions | Edit dbt YAML or Lightdash YAML | [Metrics](./resources/metrics-reference.md), [Dimensions](./resources/dimensions-reference.md) |' in text, "expected to find: " + '| Define metrics & dimensions | Edit dbt YAML or Lightdash YAML | [Metrics](./resources/metrics-reference.md), [Dimensions](./resources/dimensions-reference.md) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/SKILL.md')
    assert 'Build and deploy Lightdash analytics projects. This skill covers the **semantic layer** (metrics, dimensions, joins) and **content** (charts, dashboards).' in text, "expected to find: " + 'Build and deploy Lightdash analytics projects. This skill covers the **semantic layer** (metrics, dimensions, joins) and **content** (charts, dashboards).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/big-number-chart-reference.md')
    assert '4. **Flip colors appropriately**: Use `flipColors: true` for metrics where increases are negative (costs, errors, response times, churn rate).' in text, "expected to find: " + '4. **Flip colors appropriately**: Use `flipColors: true` for metrics where increases are negative (costs, errors, response times, churn rate).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/big-number-chart-reference.md')
    assert '| `style` | string | Number formatting style: `"K"`, `"M"`, `"B"`, `"T"` (or `"thousands"`, `"millions"`, `"billions"`, `"trillions"`) |' in text, "expected to find: " + '| `style` | string | Number formatting style: `"K"`, `"M"`, `"B"`, `"T"` (or `"thousands"`, `"millions"`, `"billions"`, `"trillions"`) |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/big-number-chart-reference.md')
    assert '5. **Comparison context**: Always provide a `comparisonLabel` when using `showComparison` to make the context clear.' in text, "expected to find: " + '5. **Comparison context**: Always provide a `comparisonLabel` when using `showComparison` to make the context clear.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cartesian-chart-reference.md')
    assert 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/cartesianChart`.' in text, "expected to find: " + 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/cartesianChart`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cartesian-chart-reference.md')
    assert '2. **Stacking**: Use the same `stack` value for series you want stacked. Only bar and area charts support stacking.' in text, "expected to find: " + '2. **Stacking**: Use the same `stack` value for series you want stacked. Only bar and area charts support stacking.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cartesian-chart-reference.md')
    assert '5. **Pivot data**: Use `pivotValues` in `yRef` to create series from pivoted dimensions.' in text, "expected to find: " + '5. **Pivot data**: Use `pivotValues` in `yRef` to create series from pivoted dimensions.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/chart-types-reference.md')
    assert '| `table` | Data tables with column formatting and conditional styling | [Table Chart Reference](./table-chart-reference.md) |' in text, "expected to find: " + '| `table` | Data tables with column formatting and conditional styling | [Table Chart Reference](./table-chart-reference.md) |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/chart-types-reference.md')
    assert '| `cartesian` | Bar, line, area, scatter charts with X/Y axes | [Cartesian Chart Reference](./cartesian-chart-reference.md) |' in text, "expected to find: " + '| `cartesian` | Bar, line, area, scatter charts with X/Y axes | [Cartesian Chart Reference](./cartesian-chart-reference.md) |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/chart-types-reference.md')
    assert '| `treemap` | Hierarchical treemaps for nested categorical data | [Treemap Chart Reference](./treemap-chart-reference.md) |' in text, "expected to find: " + '| `treemap` | Hierarchical treemaps for nested categorical data | [Treemap Chart Reference](./treemap-chart-reference.md) |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cli-reference.md')
    assert '**Warning:** The delete command will warn you if any charts being deleted are referenced by dashboards.' in text, "expected to find: " + '**Warning:** The delete command will warn you if any charts being deleted are referenced by dashboards.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cli-reference.md')
    assert 'Permanently delete charts and dashboards from the server and remove their local YAML files.' in text, "expected to find: " + 'Permanently delete charts and dashboards from the server and remove their local YAML files.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/cli-reference.md')
    assert "Execute raw SQL queries against the warehouse using the current project's credentials." in text, "expected to find: " + "Execute raw SQL queries against the warehouse using the current project's credentials."[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/custom-viz-reference.md')
    assert 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/customVis`.' in text, "expected to find: " + 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/customVis`.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/custom-viz-reference.md')
    assert 'Lightdash automatically provides your query results to the Vega-Lite specification:' in text, "expected to find: " + 'Lightdash automatically provides your query results to the Vega-Lite specification:'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/custom-viz-reference.md')
    assert '## Configuration' in text, "expected to find: " + '## Configuration'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/dashboard-best-practices.md')
    assert 'Filters with no default value (`values: []`) mean "any value" - the filter is visible but not applied. This is useful for **suggested filters** that users can optionally apply without affecting the in' in text, "expected to find: " + 'Filters with no default value (`values: []`) mean "any value" - the filter is visible but not applied. This is useful for **suggested filters** that users can optionally apply without affecting the in'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/dashboard-best-practices.md')
    assert "**Tip:** Prefer a filter with a sensible default over a required filter with no value - it's a better user experience to show data immediately rather than forcing a selection." in text, "expected to find: " + "**Tip:** Prefer a filter with a sensible default over a required filter with no value - it's a better user experience to show data immediately rather than forcing a selection."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/dashboard-best-practices.md')
    assert 'A guide to building effective, user-friendly dashboards in Lightdash based on data visualization principles and BI best practices.' in text, "expected to find: " + 'A guide to building effective, user-friendly dashboards in Lightdash based on data visualization principles and BI best practices.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/funnel-chart-reference.md')
    assert 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/funnelChart`.' in text, "expected to find: " + 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/funnelChart`.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/funnel-chart-reference.md')
    assert "**Solution**: Ensure you're using valid hex color codes with the `#` prefix." in text, "expected to find: " + "**Solution**: Ensure you're using valid hex color codes with the `#` prefix."[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/funnel-chart-reference.md')
    assert '**Solution**: Use `labelOverrides` to provide user-friendly names.' in text, "expected to find: " + '**Solution**: Use `labelOverrides` to provide user-friendly names.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/gauge-chart-reference.md')
    assert 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/gaugeChart`.' in text, "expected to find: " + 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/gaugeChart`.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/gauge-chart-reference.md')
    assert '- **`sections`**: Array of colored ranges indicating performance zones. Each section requires:' in text, "expected to find: " + '- **`sections`**: Array of colored ranges indicating performance zones. Each section requires:'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/gauge-chart-reference.md')
    assert '- **`selectedField`**: Field ID for the gauge value (a metric from your `metricQuery`)' in text, "expected to find: " + '- **`selectedField`**: Field ID for the gauge value (a metric from your `metricQuery`)'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/map-chart-reference.md')
    assert '> For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/mapChart`.' in text, "expected to find: " + '> For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/mapChart`.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/map-chart-reference.md')
    assert '| Regions not showing data | Check `geoJsonPropertyKey` matches data exactly (case-sensitive) |' in text, "expected to find: " + '| Regions not showing data | Check `geoJsonPropertyKey` matches data exactly (case-sensitive) |'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/map-chart-reference.md')
    assert '| `scatter` | Points at lat/lon coordinates | Store locations, customer addresses |' in text, "expected to find: " + '| `scatter` | Points at lat/lon coordinates | Store locations, customer addresses |'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/pie-chart-reference.md')
    assert '> **Schema Reference**: For the complete schema definition, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/pieChart`.' in text, "expected to find: " + '> **Schema Reference**: For the complete schema definition, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/pieChart`.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/pie-chart-reference.md')
    assert '| `groupLabelOverrides` | `Record<string, string>` | Custom display labels for slices |' in text, "expected to find: " + '| `groupLabelOverrides` | `Record<string, string>` | Custom display labels for slices |'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/pie-chart-reference.md')
    assert '| `valueLabel` | `"hidden" \\| "inside" \\| "outside"` | Position of labels on slices |' in text, "expected to find: " + '| `valueLabel` | `"hidden" \\| "inside" \\| "outside"` | Position of labels on slices |'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/table-chart-reference.md')
    assert '1. **Freeze identifier columns**: Keep key columns like IDs or names frozen for easier navigation when scrolling horizontally.' in text, "expected to find: " + '1. **Freeze identifier columns**: Keep key columns like IDs or names frozen for easier navigation when scrolling horizontally.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/table-chart-reference.md')
    assert '3. **Use "auto" for gradient ranges**: When values vary significantly, use `min: "auto"` and `max: "auto"` for gradient rules.' in text, "expected to find: " + '3. **Use "auto" for gradient ranges**: When values vary significantly, use `min: "auto"` and `max: "auto"` for gradient rules.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/table-chart-reference.md')
    assert '4. **Hide comparison columns**: When using field-to-field comparisons, hide the target field with `visible: false`.' in text, "expected to find: " + '4. **Hide comparison columns**: When using field-to-field comparisons, hide the target field with `visible: false`.'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/treemap-chart-reference.md')
    assert 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/treemapChart`.' in text, "expected to find: " + 'For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/treemapChart`.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/treemap-chart-reference.md')
    assert '3. **Set explicit thresholds**: `startColorThreshold` and `endColorThreshold` for clear ranges' in text, "expected to find: " + '3. **Set explicit thresholds**: `startColorThreshold` and `endColorThreshold` for clear ranges'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/developing-in-lightdash/resources/treemap-chart-reference.md')
    assert '| `useDynamicColors` | boolean | Enable dynamic color scaling based on values | No |' in text, "expected to find: " + '| `useDynamicColors` | boolean | Enable dynamic color scaling based on values | No |'[:80]

