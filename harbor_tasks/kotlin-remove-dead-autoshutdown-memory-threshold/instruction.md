# Remove Dead Code from Kotlin Compiler Daemon

The Kotlin compiler daemon contains unused code related to memory threshold monitoring that was never implemented. This dead code should be removed to reduce maintenance burden and improve code clarity.

## Task

Remove the unused `autoShutdownMemoryThreshold` functionality from the compiler daemon configuration. This involves:

1. **Remove the unused constant** related to memory threshold configuration
2. **Remove the unused field** from the `DaemonOptions` data class
3. **Remove the unused PropMapper** that was configured for this field

## Location

The relevant code is in:
- `compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt`

Look for:
- The `DaemonOptions` data class definition
- Constants related to memory thresholds
- `PropMapper` configurations in the `mappers` list

## Requirements

- The `DaemonOptions` class should continue to function correctly for all other options
- All remaining timeout and shutdown-related options must stay intact
- The `PropMapper` list should be updated to remove only the unused entry
- Code should remain syntactically valid Kotlin

## Guidelines

This is a code cleanup task. Focus on removing only the unused code while preserving all existing functionality. The compiler daemon should continue to work exactly as before for all implemented features.

When making changes:
- Review the `DaemonOptions` data class structure carefully
- Ensure no references to the removed functionality remain
- Verify the remaining `PropMapper` instances are properly configured
