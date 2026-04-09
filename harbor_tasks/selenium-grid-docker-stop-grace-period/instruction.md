# Fix DockerSession.stop() Container Leak and Add Configurable Stop Grace Period

## Problem

The `DockerSession.stop()` method in `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java` has two critical issues:

### Issue 1: Resource Leak on Exception
The method lacks proper exception handling. If an exception is thrown during `videoContainer.stop()` or `saveLogs()`, the subsequent calls to `container.stop()` and `super.stop()` are **skipped**, causing the browser container to leak.

```java
// Current problematic code:
@Override
public void stop() {
  if (videoContainer != null) {
    videoContainer.stop(Duration.ofSeconds(10));  // Exception here skips rest
  }
  saveLogs();  // Exception here skips rest
  container.stop(Duration.ofMinutes(1));
  super.stop();
}
```

### Issue 2: Hardcoded Timeouts
The stop timeouts are hardcoded (60s for browser, 10s for video) with no way for operators to tune them.

## Required Fix

1. **Add try-finally protection** to guarantee `container.stop()` and `super.stop()` always execute, regardless of failures during video container stop or log saving.

2. **Add configurable stop grace period**:
   - Add `--docker-stop-grace-period` CLI flag
   - Add `stop-grace-period` TOML config key
   - Default: 60 seconds (preserves previous browser container timeout)
   - Apply to both browser and video containers
   - Validate that the value is non-negative (throw `ConfigException` for negative values)

3. **Refactor DockerSession** to:
   - Store `Duration containerStopTimeout` and `Duration videoContainerStopTimeout` fields
   - Accept these in the constructor
   - Use them in `stop()` instead of hardcoded values

4. **Update related classes**:
   - `DockerOptions`: Add `getStopGracePeriod()` method and pass to factory
   - `DockerFlags`: Add `--docker-stop-grace-period` parameter
   - `DockerSessionFactory`: Accept `stopGracePeriod` and pass to `DockerSession`

5. **Bonus fix included in PR**: The `parseMultiplexedStream()` method should use `readFully()` instead of `skipBytes()` for more reliable log parsing, and `Debug.configureLogger()` should use a static `SELENIUM_LOGGER` for thread safety.

## Key Files to Modify

- `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java`
- `java/src/org/openqa/selenium/internal/Debug.java` (thread safety fix)
- `java/test/org/openqa/selenium/grid/node/docker/DockerSessionTest.java` (new test file)
- `java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel` (new deps)

## Testing

The PR includes comprehensive unit tests in `DockerSessionTest.java` that verify:
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
