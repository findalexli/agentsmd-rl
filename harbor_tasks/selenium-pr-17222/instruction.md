# Selenium Grid Docker Container Stop Issues

There are several issues with how Selenium Grid's `DockerSession` handles container shutdown:

## Problem 1: Hardcoded Timeouts

The browser container and video container use hardcoded timeout values (60 seconds and 10 seconds respectively) when stopping. Grid operators have no way to configure these values, which can be problematic:

- In environments with slow container shutdown, 60 seconds may not be enough
- For video containers, 10 seconds might be too short to properly finalize recordings

Look at `DockerSession.stop()` to see the hardcoded `Duration.ofMinutes(1)` and `Duration.ofSeconds(10)` values.

## Problem 2: Missing Exception Safety

If stopping the video container fails with an exception, or if saving logs throws an error, the browser container cleanup and `super.stop()` may never execute. This can leave orphaned containers running.

The `stop()` method needs proper try-finally handling to ensure container cleanup always happens.

## Problem 3: Stream Parsing Bug

In `DockerSession.parseMultiplexedStream()`, the code uses `skipBytes()` to skip header bytes. However, `DataInputStream.skipBytes()` may skip fewer bytes than requested without throwing an exception, which can corrupt the stream parsing.

## Your Task

Fix these issues by:

1. Adding a configurable `--docker-stop-grace-period` command-line flag that allows operators to set the container stop timeout (default: 60 seconds)

2. Implementing proper exception safety in `DockerSession.stop()` so that container cleanup always executes

3. Fixing the stream parsing to properly consume header bytes

Files to examine:
- `java/src/org/openqa/selenium/grid/node/docker/DockerSession.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java`
- `java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java`
