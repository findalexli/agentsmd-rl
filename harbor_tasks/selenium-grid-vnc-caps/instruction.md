# Fix VNC Capabilities Propagation

Fix the Selenium Grid SessionCapabilitiesMutator to propagate VNC capabilities (SE_VNC_ENABLED and SE_NO_VNC_PORT) even for session requests that don't include a browserName (e.g., proxy-only capability requests).

## Problem

When a session request without browserName was processed, the code had an early return that prevented VNC capabilities from being propagated from the slot stereotype to the session capabilities. This meant that proxy-only sessions couldn't access VNC even when the slot had VNC enabled.

## Solution

Reorder the code in SessionCapabilitiesMutator.apply() so that VNC capability handling happens BEFORE the browserName check and early return.

## Files to Modify

- `java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java`

## Testing

Run the SessionCapabilitiesMutatorTest to verify the fix:
```bash
bazel test //java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest
```

## References

- PR #17235: [grid] Fix VNC caps not propagated for sessions without browserName
- Base commit: b1a7b8de7bf8c9889627914888adee44c01f925a
