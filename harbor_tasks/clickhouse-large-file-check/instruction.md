# Task: Add Large File Check to ClickHouse Style Script

## Problem

ClickHouse is a large monorepo where every byte committed to git is cloned by every contributor forever. Binary blobs (JARs, archives, `.so` files, datasets) should not be committed directly - they permanently bloat the repository and can never be fully removed without history rewriting.

## Goal

Add a style check to `ci/jobs/scripts/check_style/various_checks.sh` that flags any git-tracked file larger than 5 MB unless it is explicitly whitelisted. This prevents accidentally committing large binary files.

## Requirements

1. **Define a size limit**: Set `MAX_FILE_SIZE` to 5 MB (5 * 1024 * 1024 bytes)

2. **Create a whitelist**: Define `LARGE_FILE_WHITELIST` array that includes patterns for legitimate test data that is hard to generate at runtime (e.g., `multi_column_bf.gz.parquet`, `ghdata_sample.json`, `libcatboostmodel.so`, `test_01946.zstd`, etc.)

3. **Handle stat compatibility**: Detect whether the system uses GNU stat (Linux: `-c '%s %n'`) or BSD stat (macOS: `-f '%z %N'`) and set `STAT_FMT_FLAG` and `STAT_FMT` accordingly

4. **Check all tracked files**: Use `git ls-files -z` piped through `xargs -0 stat` to efficiently get file sizes

5. **Filter by size**: Use `awk` to filter files larger than the limit: `awk -v limit="$MAX_FILE_SIZE" '$1 > limit { print substr($0, index($0, $2)) }'`

6. **Apply whitelist**: Use `grep -v` with the whitelist patterns to exclude legitimate files

7. **Output warnings**: For each large non-whitelisted file, print: `"File $file is larger than 5 MB. Large files should not be committed to git — download them at test time or build from source instead."`

## Key Implementation Notes

- The check should be cross-platform (Linux/macOS compatible stat usage)
- Use bulk operations via `xargs` to avoid fork-per-file overhead on large repos
- The whitelist is an array of `grep -v` patterns, one per line with `-e` prefix
- Test dependencies should be downloaded at test time, built from source inside the test container, or pulled from Docker images

## References

- The file `tests/stress/keeper/workloads/zookeeper_log.parquet` (14 MB) was removed in the PR as it was unused
- The only reference to it was a commented-out line in a scenario file pointing to a different filename
