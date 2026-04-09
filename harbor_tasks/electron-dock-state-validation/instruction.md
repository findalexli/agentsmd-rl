# Task: Add Input Validation for DevTools Dock State

## Problem

The `dock_state_` variable in Electron's `InspectableWebContents` class comes from DevTools preferences and can be manipulated by users or malicious actors. Currently, this value is passed directly to JavaScript contexts without validation, which could lead to security issues.

## Your Task

Add allowlist validation for the `dock_state_` variable before it is used in JavaScript execution contexts.

## Target File

`shel/browser/ui/inspectable_web_contents.cc`

## What You Need To Do

1. **Define an allowlist** of valid dock states:
   - The valid states are: `"bottom"`, `"left"`, `"right"`, `"undocked"`
   - Use Chromium's `base::MakeFixedFlatSet` to create an efficient compile-time set
   - Include the necessary header: `base/containers/fixed_flat_set.h`

2. **Create a validation function** `IsValidDockState`:
   - Takes a `std::string` parameter
   - Returns `true` if the state is in the allowlist
   - Use `kValidDockStates.contains()` for the check

3. **Update `SetDockState` method**:
   - Currently assigns `dock_state_ = state` directly
   - Change to validate the state first, falling back to `"right"` if invalid

4. **Update `LoadCompleted` method**:
   - Currently reads `current_dock_state` from preferences and removes quotes directly
   - First check if `current_dock_state` is not null
   - Remove quotes to create a `sanitized` value
   - Validate the sanitized value, falling back to `"right"` if invalid
   - Handle the null case by setting `dock_state_ = "right"`

## Example

```cpp
// Before (in SetDockState):
dock_state_ = state;

// After:
dock_state_ = IsValidDockState(state) ? state : "right";

// Before (in LoadCompleted):
base::RemoveChars(*current_dock_state, "\"", &dock_state_);

// After:
if (current_dock_state) {
  std::string sanitized;
  base::RemoveChars(*current_dock_state, "\"", &sanitized);
  dock_state_ = IsValidDockState(sanitized) ? sanitized : "right";
} else {
  dock_state_ = "right";
}
```

## Notes

- Follow Chromium's C++ coding style
- The fix should be minimal and focused
- Ensure all edge cases (null, invalid values) are handled
- The fallback state should always be `"right"`
