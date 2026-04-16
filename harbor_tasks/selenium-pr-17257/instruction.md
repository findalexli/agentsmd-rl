# OSGi Resource Loading Failure in Selenium Java

## Problem

When running Selenium in an OSGi environment (such as Eclipse plugins or Karaf containers), the `Read.resourceAsString()` method fails to load JavaScript resources like `isDisplayed.js` and `mutation-listener.js`.

The error manifests as:
```
IllegalArgumentException: Resource not found: /org/openqa/selenium/remote/isDisplayed.js
```

This happens even though the resource exists in the correct location in the JAR file.

## Root Cause

In OSGi, each bundle has its own classloader that can only see resources within its own bundle. The current implementation in `java/src/org/openqa/selenium/io/Read.java` uses `Read.class.getResourceAsStream(resource)` which uses the classloader of the `Read` class.

When code from another bundle (like `CdpEventTypes` or `RemoteScript`) calls this method to load resources that are packaged in *their* bundle (not the bundle containing `Read`), the resource cannot be found because the wrong classloader is being used.

## Files Involved

- `java/src/org/openqa/selenium/io/Read.java` - The utility class with the resource loading method
- `java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java` - Loads `mutation-listener.js`
- `java/src/org/openqa/selenium/remote/RemoteScript.java` - Loads `bidi-mutation-listener.js`
- `java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java` - Loads various atom JS files
- `java/test/org/openqa/selenium/io/ReadTest.java` - Test file that exercises resource loading

## Required Changes

The solution must resolve the classloader issue while maintaining backward compatibility. Specifically:

1. **A new overloaded method must be added** with the signature:
   `public static String resourceAsString(Class<?> resourceOwner, String resource)`

2. **The existing single-argument method** `resourceAsString(String resource)` must be marked with the `@Deprecated` annotation.

3. **The deprecated single-argument method** must delegate to the new two-argument method, passing the defining class (`Read.class`) as the first argument.

4. **All caller classes** must be updated to use the new two-argument method with the appropriate class reference:
   - `CdpEventTypes.java` must call `Read.resourceAsString(CdpEventTypes.class, ...)`
   - `RemoteScript.java` must call `Read.resourceAsString(getClass(), ...)`
   - `W3CHttpCommandCodec.java` must call `resourceAsString(getClass(), ...)`
   - `ReadTest.java` must call `Read.resourceAsString(Read.class, ...)`

5. **The new method** must use `resourceOwner.getResourceAsStream(resource)` to load resources using the caller's classloader instead of `Read`'s classloader.

## Expected Behavior

After the fix, resource loading should work correctly regardless of the classloader hierarchy, allowing OSGi bundles to load resources from their own bundle.

## Constraints

- The fix must maintain backward compatibility with non-OSGi environments
- Follow the project's deprecation policy for any API changes
- The old single-argument method must continue to work for existing non-OSGi callers