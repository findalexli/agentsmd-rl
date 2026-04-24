# Diffusion Dashboard Chart Display Issues

## Summary

The nightly diffusion comparison dashboard (`scripts/ci/utils/diffusion/generate_diffusion_dashboard.py`) has several chart display problems that make the trend data hard to read.

## Bug Details

### 1. Y-axis scaling makes data unreadable

The latency trend charts always start the y-axis at 0. For models where latency values are clustered in a narrow range far from zero (e.g., values between 45-50 seconds), all data points get squeezed into a thin band at the top of the chart, making it impossible to see trends or differences between runs.

The y-axis should scale to fit the actual data range with reasonable padding, so differences between data points are visually distinguishable. The padding formula must produce:
- `ymin > 10` for values in the 48-53 range
- `ymin > 50` for values in the 92-98 range
- `ymin >= 0` even for low values near zero (y-axis bottom must never be negative)

### 2. Chart legend overlaps data labels

The legend is positioned in the upper-right corner, which frequently overlaps with the data point value annotations. It should be moved to a position that avoids this overlap. Specifically, matplotlib legend loc code must not be `1` (upper-right).

### 3. Trend history too short

The dashboard only retains 7 historical runs, which covers roughly one week. This is insufficient for spotting longer-term performance trends. The `MAX_HISTORY_RUNS` constant (exported from the module) must be increased to cover approximately two weeks of data — specifically, it must be greater than 7 and at least 12.

### 4. Section header is hardcoded

The "SGLang Performance Trend" section header hardcodes "Last 7 Runs" rather than reflecting the actual number of runs being displayed. The header must use a dynamic count based on the number of runs available (e.g., "Last 5 Runs" when showing 5 runs total).

## Function Signature

The dashboard generator is called as:
```python
generate_dashboard(current_run, history_runs, charts_dir=<output_directory>)
```

Where:
- `current_run`: dict with `timestamp`, `commit_sha`, and `results` list containing latency data
- `history_runs`: list of similar run dicts
- `charts_dir`: directory path for PNG chart output files (optional)

The function returns markdown string. The module must also export `MAX_HISTORY_RUNS` as an integer constant.

## Files

- `scripts/ci/utils/diffusion/generate_diffusion_dashboard.py` — the dashboard generation script

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
