# OSGi Resource Loading Failure in Selenium Java

## Problem

When running Selenium in an OSGi environment (such as Eclipse plugins or Apache Karaf containers), loading JavaScript resources via `Read.resourceAsString()` fails. The error message is:

```
IllegalArgumentException: Resource not found: /org/openqa/selenium/remote/isDisplayed.js
```

Other resources affected include `mutation-listener.js` and `bidi-mutation-listener.js`.

## Root Cause

In OSGi, each bundle has its own classloader that can only see resources within its own bundle. The utility method `Read.resourceAsString()` in `org.openqa.selenium.io.Read` currently resolves resources using the classloader of the `Read` class itself (`Read.class.getResourceAsStream(resource)`). When code from another bundle calls this method to load resources packaged in *their* bundle (not the bundle containing `Read`), the resource cannot be found because the wrong classloader is used.

## Affected Code

The following callers load JavaScript resources through `Read.resourceAsString()` and are affected by this issue:

- `CdpEventTypes` — loads `mutation-listener.js` from the devtools package
- `RemoteScript` — loads `bidi-mutation-listener.js` from the remote package
- `W3CHttpCommandCodec` — loads atom JavaScript files from the remote package
- `ReadTest` — the unit test for the `Read` utility class, which tests resource loading from the classpath

Each of these classes needs to load resources using its own classloader rather than `Read`'s classloader.

## Requirements

1. Resource loading must work correctly when called from any bundle, using the caller's classloader instead of hardcoding `Read.class`.
2. Backward compatibility must be maintained — existing callers that do not specify a classloader must continue to work unchanged.
3. All affected callers (`CdpEventTypes`, `RemoteScript`, `W3CHttpCommandCodec`, `ReadTest`) must be updated to use the correct classloader for their resources.
4. The `ReadTest` unit test must verify that resources can be loaded from the classpath.

## Code Style Requirements

- Follow the project's deprecation policy: when an API is superseded by a new one, the old API must be annotated with `@Deprecated`.
- Follow the project's Javadoc conventions for any new public methods.

## Expected Behavior

After the fix, JavaScript resources such as `isDisplayed.js` should be loadable via `Read.resourceAsString()` regardless of which bundle's code makes the call, and all existing tests should continue to pass.

## Constraints

- The fix must work in both OSGi and non-OSGi environments
- Changes must be minimal and reversible
- Do not refactor unrelated code or reformat files
