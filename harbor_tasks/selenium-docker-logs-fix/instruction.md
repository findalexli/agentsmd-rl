# Fix Docker Logs Parsing in Selenium Grid

## Problem

When saving Docker container logs to a file in Selenium Grid, the resulting log files contain garbage characters at the start of each line. For example:

- **Before (broken)**: `^A??????g2026-03-13 09:30:55,398 INFO Included extra file`
- **After (fixed)**: `2026-03-13 09:54:06,477 INFO Included extra file `

The issue is that Docker's `/logs` endpoint returns a **multiplexed stream format** with binary framing headers, and the current code is writing these raw bytes directly to the log file instead of parsing and extracting the actual log content.

## Docker Multiplexed Stream Format

Each log frame from Docker has an 8-byte header:
1. **1 byte**: Stream type (1 = stdout, 2 = stderr)
2. **3 bytes**: Padding (empty/zero)
3. **4 bytes**: Payload size (big-endian integer)
4. **N bytes**: Actual log content (where N = payload size)

The fix needs to parse this format and write only the payload to the file.

## Affected Files

The relevant code is in the Selenium Grid Docker integration:

1. **`java/src/org/openqa/selenium/grid/node/docker/DockerSession.java`**
   - The `saveLogs()` method currently writes raw log data without parsing
   - Should parse the multiplexed stream format before writing

2. **`java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java`**
   - The `isBinaryStream` check needs to recognize Docker stream content types
   - Content types: `application/vnd.docker.multiplexed-stream` and `application/vnd.docker.raw-stream`

3. **`java/src/org/openqa/selenium/docker/ContainerLogs.java`**
   - Currently stores logs as `List<String>`, forcing all content into memory
   - Should support streaming access via `InputStream` to avoid memory issues with large logs

4. **`java/src/org/openqa/selenium/docker/Container.java`**
   - Needs `isRunning()` method to check container state before saving logs
   - Should return empty content when container is not running

5. **`java/src/org/openqa/selenium/docker/client/GetContainerLogs.java`**
   - Currently converts response to string and splits by newlines (breaks binary data)
   - Should pass raw response content through

## Expected Behavior

After the fix:
- Log files contain clean text without binary headers
- Large logs can be streamed without loading into memory
- Non-running containers are skipped when saving logs
- Docker-specific content types are properly handled as binary streams

## Implementation Notes

- Use `DataInputStream` for parsing the binary frame headers (readInt, skipBytes)
- Use buffered I/O streams for efficiency
- Handle `EOFException` to detect end of stream
- Consider marking `getLogLines()` as deprecated since it loads all content to memory
- Add proper null checks where needed (e.g., TZ environment variable)

## References

- Docker API docs for container logs: https://docs.docker.com/engine/api/v1.45/#operation/ContainerLogs
- Related issue: #17209 (Docker logs contain binary garbage)
