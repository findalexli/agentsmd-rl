# VNC Capabilities Missing in Session Response

## Problem

When creating a Selenium Grid session with a request that doesn't include a `browserName` capability (for example, a proxy-only configuration like `{proxy: {proxyType: direct}}`), the session response is missing the VNC-related capabilities (`se:vncEnabled` and `se:noVncPort`).

This causes the live preview icon to disappear from the Grid UI, even though the session was successfully routed to a slot that has VNC enabled.

## Expected Behavior

The VNC capabilities from the slot stereotype must be propagated to the session response regardless of whether the request included a `browserName`. When a session is routed to a VNC-enabled slot, the response must include the VNC address information. The `apply()` method must include a comment with the text `Always propagate VNC capabilities from the stereotype` to document this behavior.

## Files to Investigate

- `java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java` — handles capability mutation for sessions
- `java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java` — unit tests for the mutator

## Testing Requirements

Write a new `@Test` method named `shouldPropagateVncCapsWhenRequestHasNoBrowserName` in `SessionCapabilitiesMutatorTest.java` that verifies VNC capabilities (`se:vncEnabled` and `se:noVncPort`) are present in the session response when the request capabilities have no `browserName`.

## Reproduction

Create a session request without `browserName`:
```java
Capabilities capabilities = new ImmutableCapabilities("proxy", Map.of("proxyType", "direct"));
```

When this request is processed by `SessionCapabilitiesMutator.apply()` against a VNC-enabled stereotype (e.g., one with `"se:vncEnabled", true, "se:noVncPort", 7900`), the resulting capabilities should include `se:vncEnabled` and `se:noVncPort`, but they don't.
