# Fix File Discovery Test Flakiness

## Problem

The file service discovery tests in `discovery/file/file_test.go` are flaky. Tests occasionally fail with empty target groups when valid targets were expected.

The root cause is a race condition between the test helpers and the fsnotify watcher. When `copyFileTo` and `writeString` write to files, the fsnotify watcher may observe the file between the truncate and write steps, reading an empty or partial file instead of the complete content.

## Affected Code

File: `discovery/file/file_test.go`
Functions: `copyFileTo` and `writeString` on the `testRunner` struct

## Symptom

After a test helper writes a file (e.g., after calling `os.WriteFile`), the fsnotify watcher may read the file before the write completes, seeing an empty or truncated file. This causes the watcher to process stale or empty content instead of the newly written data, leading to intermittent test failures where valid targets are not detected.

## Requirements

1. File writes performed by the test helpers must not be observable in an intermediate state by a concurrent reader — the write must complete atomically from the perspective of the watcher.
2. The fix must work correctly on Linux, macOS, and Windows.
3. The code must compile and pass: `go test ./discovery/file/ -run "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate"`
4. The code must pass `go vet ./discovery/file/...` and `go fmt ./discovery/file/...`

## What the Tests Check

The tests verify that the following patterns exist in `discovery/file/file_test.go`:

- A helper function with receiver `*testRunner` named `func (t *testRunner) atomicWrite`
- The function uses `os.CreateTemp` and `os.Rename`
- `copyFileTo` calls `t.atomicWrite(dst, content)`
- `writeString` calls `t.atomicWrite(file, []byte(data))`
- The function has a retry loop using `for retries := 0; ; retries++`
- The retry limit is `retries >= 5`
- The sleep between retries is `time.Sleep(50 * time.Millisecond)`
- Temp files are created in a directory from `os.CreateTemp(t.TempDir()`

## Verification

After making your changes:
```bash
cd /workspace/prometheus
go test -v ./discovery/file/ -run "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate"
go vet ./discovery/file/...
go fmt ./discovery/file/...
```