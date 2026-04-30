# Selenium Grid Docker Container Stop Issues

The Selenium Grid's Docker integration has several issues with container lifecycle management that need to be fixed across the Docker node module.

## Problem 1: Unconfigurable Container Stop Timeouts

When Selenium Grid stops a Docker browser session, it terminates the browser container and any associated video recording container. However, these stop timeout values are hardcoded — operators cannot adjust how long the system waits before forcibly terminating containers.

In environments with slow container shutdown, the current timeout values may not be sufficient. In other environments, shorter timeouts may be desirable to reclaim resources faster.

A new `--docker-stop-grace-period` command-line flag is needed, defaulting to 60 seconds. This flag should be backed by a TOML configuration option under the `[docker]` section with the key `stop-grace-period`. The flag description should mention "grace period" so operators understand its purpose.

The configuration value must be validated: supplying a negative value should produce an error message containing "stop-grace-period must be a non-negative" explaining the validation failure.

The options class needs a new constant named `DEFAULT_STOP_GRACE_PERIOD` set to 60, and a new `getStopGracePeriod` method that reads the configuration and returns a `Duration`. Follow the same patterns used by the existing `DEFAULT_SERVER_START_TIMEOUT` constant and `getServerStartTimeout()` method for naming and structure. Add `import java.time.Duration` in any file that uses `Duration`.

The session class that manages Docker container lifecycles needs two new `Duration` fields: `containerStopTimeout` and `videoContainerStopTimeout`. These must be initialized in the constructor using `Require.nonNull` for validation, with descriptive parameter names like "Container stop timeout" and "Video container stop timeout". The configured values must flow from the session factory to each session instance. The factory class needs a `stopGracePeriod` field that it receives in its constructor and passes when creating sessions.

When the session's stop method executes, it must use the stored timeout fields instead of any hardcoded Duration literals.

## Problem 2: Missing Exception Safety

When stopping a Docker session, the system performs several steps in sequence: stop the video container (if present), save container logs, stop the browser container, and invoke the parent stop. If stopping the video container throws an unchecked exception, or if saving logs fails, the call to stop the browser container (`container.stop`) and the call to `super.stop()` may never execute. This can leave orphaned containers consuming resources.

The stop method needs proper exception handling using a try-finally pattern so that `container.stop` and `super.stop()` are always invoked regardless of earlier failures.

## Problem 3: Stream Parsing Bug

The Docker multiplexed stream parser reads container log output from Docker's multiplexed stream format. The format consists of a stream type byte, three padding bytes, a 4-byte payload size, and the payload data.

The current implementation consumes header bytes using a skip method that may skip fewer bytes than requested without throwing an exception, which can silently corrupt the stream. The fix should use `readFully` to guarantee all requested bytes are consumed.

## Code Style Requirements

- Use `java.time.Duration` for timeout values — add the necessary `import java.time.Duration` statement in files that use it
- Use `Require.nonNull` for parameter validation, following the existing pattern in the codebase
- Preserve all existing fields in modified classes: `container`, `videoContainer`, and `assetsPath`
- Follow the naming conventions already established in the Docker options and session classes — look at how `DEFAULT_SERVER_START_TIMEOUT` and `getServerStartTimeout()` are structured for guidance
