# Diffusion Dashboard Chart Display Issues

## Summary

The nightly diffusion comparison dashboard (`scripts/ci/utils/diffusion/generate_diffusion_dashboard.py`) has several chart display problems that make the trend data hard to read.

## Bug Details

### 1. Y-axis scaling makes data unreadable

The latency trend charts always start the y-axis at 0. For models where latency values are clustered in a narrow range far from zero (e.g., values between 45-50 seconds), all data points get squeezed into a thin band at the top of the chart, making it impossible to see trends or differences between runs.

The y-axis should scale to fit the actual data range with reasonable padding, so differences between data points are visually distinguishable.

### 2. Chart legend overlaps data labels

The legend is positioned in the upper-right corner, which frequently overlaps with the data point value annotations. It should be moved to a position that avoids this overlap.

### 3. Trend history too short

The dashboard only retains 7 historical runs, which covers roughly one week. This is insufficient for spotting longer-term performance trends. It should be extended to cover approximately two weeks of data.

### 4. Section header is hardcoded

The "SGLang Performance Trend" section header hardcodes "Last 7 Runs" rather than reflecting the actual number of runs being displayed.

## Files

- `scripts/ci/utils/diffusion/generate_diffusion_dashboard.py` — the dashboard generation script
