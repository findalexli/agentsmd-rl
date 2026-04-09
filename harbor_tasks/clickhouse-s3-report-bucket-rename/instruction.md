# Rename HTML_S3_PATH to S3_REPORT_BUCKET and Add Upstream Catalog Merge

## Problem

The CI system has a setting named `HTML_S3_PATH` that is used throughout the codebase to specify where CI reports are stored in S3. This name is misleading - it actually refers to an S3 bucket path for reports, not just HTML files. Additionally, forks of the repository need a way to merge their own issue catalogs with upstream catalogs for proper flaky test detection.

## What Needs to Change

### 1. Rename `HTML_S3_PATH` to `S3_REPORT_BUCKET`

The setting `HTML_S3_PATH` should be renamed to `S3_REPORT_BUCKET` for clarity. This affects:

- `ci/praktika/settings.py` - the setting definition and `_USER_DEFINED_SETTINGS` list
- `ci/praktika/hook_html.py` - usage of the setting
- `ci/praktika/html_prepare.py` - usage of the setting
- `ci/praktika/info.py` - multiple usages of the setting
- `ci/praktika/issue.py` - usage of the setting
- `ci/praktika/result.py` - multiple usages of the setting
- `ci/praktika/s3.py` - usage of the setting
- `ci/praktika/validator.py` - error messages and assertions
- `ci/settings/settings.py` - the setting definition
- `ci/jobs/collect_statistics.py` - should import from praktika.settings instead of ci.settings.settings and use `Settings.S3_REPORT_BUCKET`

### 2. Add `S3_UPSTREAM_REPORT_BUCKET` Setting

Add a new optional setting `S3_UPSTREAM_REPORT_BUCKET` to `ci/praktika/settings.py`:
- Define the setting with default value `''`
- Add it to the `_USER_DEFINED_SETTINGS` list

This setting allows forks to specify an upstream S3 bucket to pull issue catalogs from.

### 3. Implement Upstream Catalog Merge in `issue.py`

Modify `TestCaseIssueCatalog.from_s3()` in `ci/praktika/issue.py` to:

1. Add a new helper method `_download_catalog(cls, bucket, suffix="")` that downloads and decompresses a single catalog from an S3 bucket
2. Modify `from_s3()` to:
   - Download the main catalog from `Settings.S3_REPORT_BUCKET`
   - If `Settings.S3_UPSTREAM_REPORT_BUCKET` is set, also download the upstream catalog (using `_upstream` suffix for local files)
   - Merge upstream issues into the main catalog, deduplicating by issue number
   - Print a message showing how many issues were merged

The merge logic should:
- If only upstream is available (main catalog is None), return upstream
- If both are available, merge upstream issues into the main catalog, skipping duplicates
- If neither is available, return None

## Files to Modify

1. `ci/praktika/settings.py` - rename setting, add new setting
2. `ci/praktika/issue.py` - add `_download_catalog` method, modify `from_s3`, add Settings import
3. `ci/praktika/hook_html.py` - use new setting name
4. `ci/praktika/html_prepare.py` - use new setting name
5. `ci/praktika/info.py` - use new setting name
6. `ci/praktika/result.py` - use new setting name
7. `ci/praktika/s3.py` - use new setting name
8. `ci/praktika/validator.py` - use new setting name
9. `ci/settings/settings.py` - use new setting name
10. `ci/jobs/collect_statistics.py` - change import and use new setting

## Testing

After making changes, verify:
- No references to `HTML_S3_PATH` remain in the modified files
- `S3_REPORT_BUCKET` and `S3_UPSTREAM_REPORT_BUCKET` are defined in settings
- All Python files have valid syntax and imports work correctly
- The `_download_catalog` method exists and `from_s3` has merge logic
