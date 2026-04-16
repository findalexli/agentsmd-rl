# Rename HTML_S3_PATH Setting and Add Upstream Catalog Merge

## Problem

The CI system uses a setting called `HTML_S3_PATH` to specify the S3 location for CI reports. This name is misleading — it refers to an S3 bucket path for reports, not just HTML files. It should be renamed to `S3_REPORT_BUCKET` throughout the codebase.

Additionally, repository forks need to merge local issue catalogs with upstream catalogs for better flaky test detection. This requires a new optional setting and merge logic in the `TestCaseIssueCatalog` class.

## Requirements

### 1. Setting Rename: `HTML_S3_PATH` → `S3_REPORT_BUCKET`

Rename the `HTML_S3_PATH` setting to `S3_REPORT_BUCKET` everywhere it is used. After the rename:

- The `Settings` class must have a `S3_REPORT_BUCKET` attribute (type `str`, default empty string)
- The `_USER_DEFINED_SETTINGS` list must contain `"S3_REPORT_BUCKET"`
- All code that previously referenced `HTML_S3_PATH` must use `S3_REPORT_BUCKET` instead
- The validator must produce an error message that references `S3_REPORT_BUCKET`
- No non-comment references to `HTML_S3_PATH` may remain in any source file
- The legacy compatibility module must export `S3_REPORT_BUCKET`

The file that currently imports `S3_REPORT_BUCKET_NAME` from `ci.settings.settings` must be updated to use `Settings.S3_REPORT_BUCKET` instead.

### 2. New Setting: `S3_UPSTREAM_REPORT_BUCKET`

Add a new optional setting to the `Settings` class:

- Attribute name: `S3_UPSTREAM_REPORT_BUCKET` (type `str`, default empty string)
- Must be listed in `_USER_DEFINED_SETTINGS`

When non-empty, this setting specifies an upstream S3 bucket from which to pull and merge issue catalogs.

### 3. Upstream Catalog Merge in `TestCaseIssueCatalog`

The `TestCaseIssueCatalog` class must support downloading and merging catalogs from an upstream bucket:

- Import `Settings` from the praktika settings module
- Add a classmethod that downloads a catalog from a given S3 bucket
- The `to_s3()` method must use the `S3_REPORT_BUCKET` setting for the bucket portion of the upload path
- The `from_s3()` method must use `S3_REPORT_BUCKET` for the main catalog, and if `S3_UPSTREAM_REPORT_BUCKET` is set, also download and merge the upstream catalog (deduplicating by issue number and reporting statistics). If only the upstream catalog is available, return the upstream catalog.

## Verification

After changes:
- All Python files must have valid syntax and all existing imports must continue to work
- No references to `HTML_S3_PATH` should remain in non-comment code
- The `Settings` class and all praktika modules must be importable without errors