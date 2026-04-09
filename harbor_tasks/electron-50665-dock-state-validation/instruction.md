# Fix Dock State Validation in DevTools

## Problem

The `InspectableWebContents` class in Electron's DevTools implementation has a security vulnerability where user-controlled `dock_state` values are used without validation. This can lead to unexpected behavior when invalid or malicious values are passed to the DevTools docking system.

## Affected Code

The issue exists in `shell/browser/ui/inspectable_web_contents.cc` in two locations:

1. **`SetDockState()` method** - Directly assigns user-provided state without validation
2. **`LoadCompleted()` method** - Reads persisted dock state from preferences without validation

## Expected Fix

You need to implement input validation for the `dock_state` parameter:

1. **Create an allowlist** of valid dock states: `"bottom"`, `"left"`, `"right"`, `"undocked"`
2. **Add a validation function** that checks if a state is in the allowlist
3. **Update `SetDockState()`** to validate input and default to `"right"` if invalid
4. **Update `LoadCompleted()`** to:
   - Check if `current_dock_state` exists before using it
   - Sanitize the value by removing quotes
   - Validate the sanitized value and default to `"right"` if invalid
5. **Include the required header** for the container type used in the allowlist

## Implementation Hints

- Use Chromium's `base::MakeFixedFlatSet` for the allowlist (efficient constant-time lookup)
- Handle the case where `current_dock_state` might be null/undefined
- Use `base::RemoveChars()` to sanitize quote characters from persisted values
- The default fallback for invalid states should be `"right"`

## Testing

Your fix will be verified by checking that:
- The security allowlist constant exists and contains the correct values
- The validation function is properly defined
- Both `SetDockState()` and `LoadCompleted()` use validation
- Invalid states are rejected and replaced with the default
- No direct assignment of unvalidated state values remains

## References

- See `.github/copilot-instructions.md` for Electron coding conventions
- The file uses Chromium's `base::` abstractions and follows Chromium style
