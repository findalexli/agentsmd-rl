# Add Cooldown Parameter to Constraints Version Check

## Problem

The `breeze release-management constraints-version-check` command compares package versions in the constraints file against the latest versions on PyPI. However, very recently released package versions may lack stability or wide availability, causing false positives when flagging packages as outdated.

## Task

Implement a cooldown feature that filters out package versions released within a configurable time window when determining the "latest" version. This allows the version checker to ignore packages that were just released and give them time to stabilize before considering them as upgrade targets.

## Requirements

1. Add a function to find the latest non-prerelease version whose release date is outside a cooldown period
2. The function should:
   - Filter out pre-release and dev versions
   - Skip versions released within the cooldown period
   - Return the latest qualifying version, or None if no version qualifies
3. Add a `--cooldown-days` parameter to the relevant functions (default: 4 days)
4. When no version satisfies the cooldown filter, fall back to PyPI's reported latest version
5. Display the cooldown period in the console output

## Files to Modify

- `dev/breeze/src/airflow_breeze/utils/constraints_version_check.py`

## Hints

- You'll need to work with datetime calculations to compare release dates against the cooldown cutoff
- The release data from PyPI includes `upload_time_iso_8601` for each version
- Look at how existing version filtering functions handle pre-release detection
