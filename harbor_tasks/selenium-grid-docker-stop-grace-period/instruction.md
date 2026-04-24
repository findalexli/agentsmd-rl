# Fix DockerSession.stop() Container Leak and Add Configurable Stop Grace Period

## Problem

The `DockerSession.stop()` method in `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java` has two critical issues:

### Issue 1: Resource Leak on Exception
If an exception is thrown during `videoContainer.stop()` or `saveLogs()`, the subsequent calls to `container.stop()` and `super.stop()` are **skipped**, causing the browser container to leak.

### Issue 2: Hardcoded Timeouts
The stop timeouts are hardcoded with no way for operators to tune them.

## Required Fix

1. **Add try-finally protection** to guarantee `container.stop()` and `super.stop()` always execute, regardless of failures during video container stop or log saving.

2. **Add configurable stop grace period**:
   - Add a CLI flag for the stop grace period
   - Add a TOML config key for the stop grace period
   - Default: 60 seconds (preserves previous browser container timeout)
   - Apply to both browser and video containers
   - Validate that the value is non-negative

3. **Use Duration fields instead of hardcoded values** in `DockerSession.stop()`

4. **Update related classes** to pass the configurable grace period through the construction chain.

5. **Bonus fixes**: The `parseMultiplexedStream()` method should use a more reliable approach for reading stream bytes, and `Debug.configureLogger()` should use a static logger field for thread safety.

## Key Files to Modify

- `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java`
- `java/src/org/openqa/selenium/internal/Debug.java`
- `java/test/org/openqa/selenium/grid/node/docker/DockerSessionTest.java`
- `java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel`

## Testing

The PR should include comprehensive unit tests in `DockerSessionTest.java` that verify:
- Video container is stopped before logs are fetched
- Browser container is stopped even if video container stop fails
- Browser container is stopped even if log fetch throws
- Configured stop grace period is passed to both containers

Build commands:
```bash
bazel build //java/src/org/openqa/selenium/grid/node/docker/...
bazel build grid
```

See `java/AGENTS.md` for code conventions (logging, deprecation patterns, Javadoc).