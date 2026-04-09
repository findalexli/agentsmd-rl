# Task: Add Trace ID Injection to Logrus Fields

## Problem

The containerd logging system currently lacks the ability to correlate logs with OpenTelemetry traces. When debugging distributed issues, it's difficult to connect log entries with their corresponding trace IDs.

## Goal

Implement a feature that allows optionally injecting OpenTelemetry Trace IDs directly into logrus log entry fields. This feature should:

1. Be configurable via a `log_trace_id` toggle in the `[debug]` section of containerd's configuration
2. Only inject trace IDs when the option is enabled AND a valid trace context exists
3. Preserve backward compatibility - existing behavior should remain unchanged when disabled

## Files to Modify

The key files involved in this change are:

- `pkg/tracing/log.go` - Core hook implementation for adding trace IDs to log entries
- `cmd/containerd/server/config/config.go` - Debug configuration struct
- `cmd/containerd/command/main.go` - Hook registration (needs to happen after config is loaded)
- `pkg/tracing/plugin/otlp.go` - Currently registers hook in `init()`, needs to be moved

## Requirements

When enabled, the `LogrusHook.Fire()` method should:
1. Extract the trace ID from the active span context
2. Add it to the log entry's Data fields under the key `"trace_id"`
3. Only do this if the span context is valid

The hook registration should be moved from `init()` in `otlp.go` to the main application startup in `main.go`, where the configuration is already parsed and available.

## Testing

You can test your implementation by running the tests in the `pkg/tracing/` package:

```bash
cd /workspace/containerd/pkg/tracing
go test -v -run TestLogrusHookTraceID
```

The test file `log_test.go` should be created with comprehensive test cases covering:
- Trace ID injection when enabled (with valid span context)
- No injection when option is disabled
- No injection when no span context exists

## Notes

- The feature must be opt-in via configuration
- Maintain API stability - use functional options pattern for new configuration
- The trace ID should only be injected for valid span contexts
- Hook registration must happen AFTER config is parsed (not in `init()`)
