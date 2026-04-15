# Task: Add Large File Check to ClickHouse Style Checks

## Problem

The ClickHouse repository is a large monorepo where every byte committed is cloned by every contributor forever. Binary blobs (JARs, archives, compiled artifacts, datasets) should never be committed directly to git. The repository needs a CI style check that detects and flags any git-tracked file larger than 5 MB, unless it is explicitly whitelisted as legitimate test data.

## Task

Add a large file detection check to `ci/jobs/scripts/check_style/various_checks.sh` that:

1. Scans all git-tracked files using `git ls-files` for files larger than 5 MB
2. Prints a warning message for any oversized file found
3. Respects a whitelist of known legitimate large test files
4. Works on both GNU (Linux) and BSD (macOS) stat formats
5. Uses efficient bulk operations (avoiding fork-per-file which takes minutes on large repos)

## Detailed Requirements

### Size Threshold

Define the size limit as a variable named `MAX_FILE_SIZE` with the value `$((5 * 1024 * 1024))` (5 MB in bytes).

### Whitelist

Define a whitelist array variable named `LARGE_FILE_WHITELIST` that includes entries for these known legitimate large test data files (the whitelist entries are used as `grep -e` patterns):

- `multi_column_bf.gz.parquet`
- `libcatboostmodel.so_aarch64`
- `libcatboostmodel.so_x86_64`
- `keeper-java-client-test.jar`
- `paimon-rest-catalog/chunk_`
- `ghdata_sample.json`

### Cross-Platform Stat Format Detection

The script must detect whether the system has GNU or BSD `stat` and store the results in two variables:

- `STAT_FMT_FLAG` — the flag character: `-c` for GNU stat, `-f` for BSD stat
- `STAT_FMT` — the format string: `%s %n` for GNU, `%z %N` for BSD

To detect GNU stat, test whether the command `stat -c '%s %n' /dev/null` succeeds.

### Section Comment

Include a comment containing the text "Large files checked into git" to label this check section.

### Warning Message

When an oversized, non-whitelisted file is detected, print a warning that includes the exact text:

```
is larger than 5 MB. Large files should not be committed to git
```

The warning must also contain the suggestion: `download them at test time or build from source`.

## File to Modify

- `ci/jobs/scripts/check_style/various_checks.sh` — Add the large file check logic at the end of the file
