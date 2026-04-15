# Task: Add Large File Check to ClickHouse Style Checks

## Problem

The ClickHouse monorepo's CI needs a style check that detects git-tracked files larger than 5 MB. Such files should be flagged as violations unless they match a whitelist of known legitimate test data.

## Task

Append a large file detection section to the end of `ci/jobs/scripts/check_style/various_checks.sh`.

## Requirements

### Functionality

The check must:

1. Enumerate all git-tracked files and determine their sizes
2. Flag any file exceeding 5 MB as a violation
3. Exclude files matching a whitelist of known large test data (see below)
4. Print a warning for each violation
5. Work correctly on both GNU (Linux) and BSD (macOS) systems

The `stat` command syntax differs between GNU and BSD platforms, so the check must detect which variant is available at runtime.

### Whitelist Patterns

These file patterns must be exempt from violation reporting:

- `multi_column_bf.gz.parquet`
- `libcatboostmodel.so_aarch64`
- `libcatboostmodel.so_x86_64`
- `keeper-java-client-test.jar`
- `paimon-rest-catalog/chunk_`
- `ghdata_sample.json`

### Warning Message

Each violation warning must contain the text:

```
is larger than 5 MB. Large files should not be committed to git
```

along with the suggestion `download them at test time or build from source`.

### CI Test Suite Identifiers

The CI test suite validates this check by searching the script for specific identifiers. To pass validation, the script must contain all of the following:

- A comment containing the text `Large files checked into git`
- The threshold expression `MAX_FILE_SIZE=$((5 * 1024 * 1024))`
- An array named `LARGE_FILE_WHITELIST` holding the exclusion patterns
- Variables named `STAT_FMT_FLAG` and `STAT_FMT` for the detected stat configuration
- The `git ls-files` command for enumerating tracked files
- A GNU stat probe using `stat -c '%s %n' /dev/null` (the detection logic must reference both `-c` and `-f` flag variants)
