# Task: Add Large File Check to ClickHouse Style Checks

## Problem

The ClickHouse CI needs a style check that detects git-tracked files larger than 5 MB. Large files permanently bloat the repository for every contributor and cannot be removed without rewriting git history. Binary blobs (JARs, archives, .so files, datasets) should be downloaded at test time or built from source instead of being committed.

## Task

Add a large file detection check to the shell script in `ci/jobs/scripts/check_style/various_checks.sh` that:

1. Enumerates all git-tracked files using `git ls-files`
2. Identifies any file exceeding 5 MB (5,242,880 bytes)
3. Excludes files matching a whitelist of known legitimate test data (see below)
4. Prints a warning for each violation containing:
   - The filename
   - The phrase "is larger than 5 MB"
   - The phrase "download them at test time or build from source"
5. Works correctly on both GNU/Linux and BSD/macOS systems

## Whitelist Patterns

The following files are legitimate large test data and should not be flagged:

- `multi_column_bf.gz.parquet`
- `libcatboostmodel.so_aarch64`
- `libcatboostmodel.so_x86_64`
- `keeper-java-client-test.jar`
- `paimon-rest-catalog/chunk_`
- `ghdata_sample.json`

## Requirements

- The check should use feature detection to handle platform differences (GNU stat vs BSD stat have different flag formats)
- Consider using efficient bulk processing for large repositories (the ClickHouse repo has thousands of files)
- Add comments explaining the check's purpose and any non-obvious logic
- The check runs with `ROOT_PATH` available as an environment variable

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
