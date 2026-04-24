# Fix File Discovery Test Flakiness

## Problem

The file service discovery tests in `discovery/file/file_test.go` are flaky. Tests occasionally fail with empty target groups when valid targets were expected.

The root cause is a race condition between the test helpers and the fsnotify watcher. When `copyFileTo` and `writeString` write to files, the fsnotify watcher may observe the file between the truncate and write steps, reading an empty or partial file instead of the complete content.

## Affected Code

File: `discovery/file/file_test.go`
Functions: `copyFileTo` and `writeString` on the `testRunner` struct

## Symptom

After a test helper writes a file using `os.WriteFile`, the fsnotify watcher may read the file before the write completes, seeing an empty or truncated file. This causes the watcher to process stale or empty content instead of the newly written data, leading to intermittent test failures where valid targets are not detected.

## Requirements

The solution must satisfy the following, which are verified by automated tests:

1. A helper function named `atomicWrite` must exist on the `testRunner` type, accepting a destination path and data
2. The helper must use `os.CreateTemp` and `os.Rename` for atomic file replacement
3. The helper must create temporary files in the directory returned by `t.TempDir()` (not in `t.dir`)
4. The helper must implement retry logic with at least 5 retries and use `time.Sleep` with `Millisecond` duration for cross-platform Windows compatibility
5. `copyFileTo` and `writeString` must call `t.atomicWrite` instead of `os.WriteFile`
6. File writes performed by the test helpers must not be observable in an intermediate state by a concurrent reader
7. The code must compile and pass: `go test ./discovery/file/ -run "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate"`
8. The code must pass `go vet ./discovery/file/...` and `go fmt ./discovery/file/...`

## Hints

- Atomic file replacement using a temporary file and rename avoids the race condition where a concurrent reader sees partial content
- Creating temp files outside the watched directory avoids triggering spurious fsnotify events that could cause file handle conflicts on Windows
- Windows file systems may hold file handles open longer than expected after read operations, causing rename to fail until the handle is released
- The fsnotify watcher must always see a complete, intact file when reading after a write completes

## Verification

After making your changes:
```bash
cd /workspace/prometheus
go test -v ./discovery/file/ -run "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate"
go vet ./discovery/file/...
go fmt ./discovery/file/...
```
