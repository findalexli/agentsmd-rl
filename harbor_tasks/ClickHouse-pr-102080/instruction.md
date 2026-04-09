# Task: Add Large File Check to ClickHouse Style Checks

## Problem

The ClickHouse repository is a large monorepo where every byte committed is cloned by every contributor forever. Binary blobs (JARs, archives, compiled artifacts, datasets) should never be committed directly to git. The repository needs a CI style check that detects and flags any git-tracked file larger than 5 MB, unless it is explicitly whitelisted as legitimate test data.

## Task

Add a large file detection check to `ci/jobs/scripts/check_style/various_checks.sh` that:

1. Scans all git-tracked files for files larger than 5 MB
2. Prints a warning message for any oversized file found
3. Respects a whitelist of known legitimate large test files
4. Works on both GNU (Linux) and BSD (macOS) stat formats
5. Uses efficient bulk operations (avoiding fork-per-file which takes minutes on large repos)

## Files to Modify

- `ci/jobs/scripts/check_style/various_checks.sh` - Add the large file check logic at the end of the file

## Hints

- The whitelist should include entries like `multi_column_bf.gz.parquet`, `libcatboostmodel.so_aarch64`, and other known large test data files
- Use `git ls-files` to get tracked files and `stat` to get file sizes
- The warning message should guide users to download files at test time or build from source instead
- Consider how to handle different stat command formats between Linux and macOS

## Expected Behavior

When run, the script should output warnings like:
```
File path/to/file is larger than 5 MB. Large files should not be committed to git — download them at test time or build from source instead.
```

But should NOT flag files matching the whitelist patterns.
