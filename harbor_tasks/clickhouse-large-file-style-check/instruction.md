# Add a CI style check that flags large files committed to git

The repository's style-check script does not currently detect when binary
blobs or other oversized files have been committed to git. Once a large
file is committed it is cloned by every contributor forever and cannot be
fully removed without history rewriting, so we want CI to surface this as
a violation.

## What you need to do

Extend `ci/jobs/scripts/check_style/various_checks.sh` with a new check
that walks every git-tracked file in the working tree and emits one
warning line per file whose size exceeds **5 MB** (5 × 1024 × 1024 bytes
— use **MiB**, not decimal MB).

The check must satisfy the following requirements:

### 1. Threshold

A file is "too large" iff its on-disk size is **strictly greater than
5 × 1024 × 1024 bytes**. A 5 MB file is fine; a 5 MB + 1 byte file is
not. Files of any size below this threshold must not produce a warning.

### 2. Warning format

For each oversized non-whitelisted file `<path>`, the script must print
the following sentence, verbatim, on its own line:

```
File <path> is larger than 5 MB. Large files should not be committed to git — download them at test time or build from source instead.
```

That exact substring `is larger than 5 MB. Large files should not be committed to git`
must appear in the output for each violating file. The path is
substituted in place of `<path>`.

### 3. Whitelist

Some legitimate test/data files are too hard to generate at runtime and
must be allowed through. Implement a path-substring whitelist (the
filename appearing anywhere in the tracked path is enough). The
whitelist must include at least these patterns:

- `multi_column_bf.gz.parquet`
- `ghdata_sample.json`
- `libcatboostmodel.so_aarch64`
- `libcatboostmodel.so_x86_64`
- `test_01946.zstd`
- `e60db19f11f94175ac682c5898cce0f77cc508ea.tar.gz`
- `npy_big.npy`
- `string_int_list_inconsistent_offset_multiple_batches.parquet`
- `known_failures.txt`
- `keeper-java-client-test.jar`
- `amazon_model.bin`
- `nbagames_sample.json`
- `02731.arrow`
- `aes-gcm-avx512.s`
- `paimon-rest-catalog/chunk_`

If a tracked path contains any of these substrings, the file must NOT be
reported, even if its size exceeds the threshold.

### 4. Discovery and portability

- Use `git ls-files` (with `$ROOT_PATH` already defined at the top of the
  script) to enumerate tracked files. Untracked files in the working
  tree must not be considered.
- The check must work both on Linux (GNU `stat`, `-c '%s %n'`) and on
  macOS (BSD `stat`, `-f '%z %N'`). Detect once which flavour is
  available and use it for the whole pass; do not fork a `stat` process
  per file.
- The check must run in reasonable time on a repository with hundreds of
  thousands of tracked files — bulk-stat via `xargs -0`, do not use a
  per-file shell loop for the `stat` call.
- It is safe to swallow `stat` errors for paths that no longer exist on
  disk (e.g. files deleted from the working tree but not yet from the
  index) — those paths simply produce no output.

### 5. Surfacing existing violations

After your check is in place, run it against the repository as it
currently is. If it reports any file that is not in the whitelist, that
file represents the kind of bloat the check is meant to prevent. Where
the file is genuinely unused (its only references are in dead/commented
code), remove it from git so the check passes cleanly. Do not edit the
whitelist to suppress a real violation.

## Constraints

- Do not modify the threshold (5 MB), the warning sentence, or any of the
  whitelist patterns above. Tests assert on these literals.
- Do not remove or weaken any of the existing checks already present in
  `various_checks.sh`. Your change is purely additive within that file.
- The script must remain valid bash (`bash -n` must succeed).

## Code style requirements

This task does not require running any linter or formatter — the only
"style" requirement is the warning-string format above.
