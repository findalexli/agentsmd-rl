# Docker Container Log Files Contain Garbage Characters

When saving Docker container logs to a file in Selenium Grid, the resulting `selenium-server.log` file contains garbage binary characters at the start of each log line.

## Symptom

Log lines in the saved file look like this:
```
??????g2026-03-13 09:30:55,398 INFO Included extra file
```

Instead of the expected clean format:
```
2026-03-13 09:30:55,398 INFO Included extra file
```

## Root Cause

The Docker Engine API `/containers/{id}/logs` endpoint returns log data in a multiplexed stream format when the container is created with `tty: false`. This format prefixes each chunk of output with an 8-byte header (stream type byte + 3 padding bytes + 4-byte big-endian payload size), followed by the actual payload bytes. When these raw bytes are written directly to a log file, the header bytes appear as garbage characters.

To produce clean logs, the header must be stripped from each frame before writing. The parsing algorithm reads and discards: 1 stream-type byte, 3 padding bytes, then reads a 4-byte big-endian integer for the payload size, then reads exactly that many payload bytes into the output. This repeats until end-of-stream.

## Required Method Addition

The `DockerSession.java` file at `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java` must implement a `parseMultiplexedStream` method that:
- Reads bytes from an `InputStream` wrapped in a `DataInputStream` buffered stream
- For each frame: skips 1 stream-type byte and 3 padding bytes using `readFully()`
- Reads the 4-byte big-endian payload size using `readInt()`
- Reads exactly `payloadSize` bytes of payload using `readFully()` and writes them to the output stream
- Continues until `EOFException` is thrown (end of stream)

The method signature should accept an `InputStream` and return a `byte[]` or written output.

## Required Helper Methods

For the log saving to work correctly, additional methods are needed:

**In `Container.java`** (`java/src/org/openqa/selenium/docker/Container.java`):
- `public boolean isRunning()` — returns the current running state of the container

**In `ContainerLogs.java`** (`java/src/org/openqa/selenium/docker/ContainerLogs.java`):
- `public InputStream getLogs()` — returns a streaming input stream for container logs (use `Contents.Supplier` for lazy loading)
- The existing `getLogLines()` method should be marked `@Deprecated`

**In `JdkHttpMessages.java`** (`java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java`):
- A helper method `isBinaryStream` that recognizes Docker binary stream content types:
  - `application/vnd.docker.multiplexed-stream`
  - `application/vnd.docker.raw-stream`

## Additional Safety Check

In `DockerSessionFactory.java` (`java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java`), the code that reads the `TZ` environment variable must check for `null` before using the value (use `Optional.ofNullable` pattern with null guard).

## Expected Behavior After Fix

After the fix:
1. Container logs fetched via Docker API should have their multiplexed stream headers correctly stripped
2. Log files should contain only clean, readable text without any leading garbage bytes
3. `Container.isRunning()` should accurately reflect the container's running state
4. `ContainerLogs.getLogs()` should return an `InputStream` for streaming log access
5. `JdkHttpMessages` should treat Docker binary streams as binary (not text)
6. No `NullPointerException` should occur when the `TZ` environment variable is unset