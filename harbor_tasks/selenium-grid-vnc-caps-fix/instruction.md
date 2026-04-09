# Selenium Grid: Fix VNC Caps Not Propagated for Sessions Without browserName

## Problem

When a session request arrives at the Selenium Grid without a `browserName` capability (for example, a request with only proxy configuration like `{proxy: {proxyType: direct}}`), the session is routed to a matching slot but the resulting session capabilities are missing `se:vnc` and `se:vncLocalAddress`.

This causes the live preview icon to not appear on the Grid UI, even though VNC is actually enabled on the node.

## Files to Modify

The core issue is in:
- `java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java`

The `SessionCapabilitiesMutator` class takes a `slotStereotype` and merges its capabilities into session request capabilities. Look at the `apply()` method which handles capability propagation.

## Expected Behavior

When a session request (without browserName) is matched to a slot that has VNC enabled:
- The `se:vncEnabled` capability should be present in the session capabilities
- The `se:noVncPort` capability should be present in the session capabilities

This should happen regardless of whether the session request has a browserName or not.

## Repository Guidelines

Before making changes, read the repository guidance:
- `AGENTS.md` (root level) - Overall project conventions
- `java/AGENTS.md` - Java-specific guidance

Key points:
- Maintain API/ABI compatibility
- Prefer small, reversible diffs
- Use Bazel for building and testing
- Write tests for your fix

## Testing

The repository uses Bazel for builds and tests. The relevant test class is:
- `//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest`

You can run tests with:
```bash
bazel test //java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest
```
