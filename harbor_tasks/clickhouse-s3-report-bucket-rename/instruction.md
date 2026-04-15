# Rename HTML_S3_PATH Setting and Add Upstream Catalog Merge

## Problem

The CI system uses a setting called `HTML_S3_PATH` to specify the S3 location for CI reports. This name is misleading — it refers to an S3 bucket path for reports, not just HTML files. It should be renamed to `S3_REPORT_BUCKET` throughout the codebase.

Additionally, repository forks need to merge local issue catalogs with upstream catalogs for better flaky test detection. This requires a new optional setting and merge logic in the `TestCaseIssueCatalog` class.

## Requirements

### 1. Setting Rename: `HTML_S3_PATH` → `S3_REPORT_BUCKET`

The setting must be renamed everywhere it is used. After the rename, the following must hold:

- The `Settings` class (in `ci/praktika/settings.py`) must declare: `S3_REPORT_BUCKET: str = ""`
- The `_USER_DEFINED_SETTINGS` list must contain the string `"S3_REPORT_BUCKET"` (replacing the old entry)
- All code that previously referenced `Settings.HTML_S3_PATH` must instead use `Settings.S3_REPORT_BUCKET` — use grep to find every occurrence across the codebase
- The validator must produce the error message: `"S3_REPORT_BUCKET Setting must be defined"`
- No non-comment references to `HTML_S3_PATH` may remain in any source file
- The legacy compatibility module `ci/settings/settings.py` must export `S3_REPORT_BUCKET = S3_REPORT_BUCKET_NAME` (replacing the old `HTML_S3_PATH` alias)

The file `ci/jobs/collect_statistics.py` currently imports `S3_REPORT_BUCKET_NAME` from `ci.settings.settings` and uses it to build S3 paths. It must be updated to import `Settings` via `from ci.praktika.settings import Settings` and use `Settings.S3_REPORT_BUCKET` for S3 path construction. The `S3_REPORT_BUCKET_NAME` import must be removed entirely.

### 2. New Setting: `S3_UPSTREAM_REPORT_BUCKET`

A new optional setting must be added to the `Settings` class:

- Attribute declaration: `S3_UPSTREAM_REPORT_BUCKET: str = ""`
- Listed in `_USER_DEFINED_SETTINGS` as `"S3_UPSTREAM_REPORT_BUCKET"`

When non-empty, this setting specifies an upstream S3 bucket from which to pull and merge issue catalogs.

### 3. Upstream Catalog Merge in `TestCaseIssueCatalog`

The `TestCaseIssueCatalog` class must support downloading and merging catalogs from an upstream bucket:

- The module must import `Settings` via: `from praktika.settings import Settings`
- A new classmethod with signature `def _download_catalog(cls, bucket, suffix="")` must handle downloading and decompressing a single catalog from a given S3 bucket
- The `to_s3()` method currently uploads to a hardcoded `"clickhouse-test-reports/statistics"` path — it must use `{Settings.S3_REPORT_BUCKET}/statistics` instead
- The `from_s3()` method must download the main catalog from `Settings.S3_REPORT_BUCKET`, then check `if Settings.S3_UPSTREAM_REPORT_BUCKET:` — if set, also download the upstream catalog using `"_upstream"` as a local file suffix, merge upstream issues into the main catalog (deduplicating by issue number), and print merge statistics. If only the upstream catalog is available (main is None), return the upstream catalog.

## Verification

After changes:
- All Python files must have valid syntax and all existing imports must continue to work
- No references to `HTML_S3_PATH` should remain in non-comment code
- The `Settings` class and all praktika modules must be importable without errors
