# Selenium Java: OSGi-safe resource loading from `Read.resourceAsString`

You are working in the Selenium monorepo. The Java bindings ship a small
helper class `Read` under `java/src/org/openqa/selenium/io/Read.java` that
wraps `Class.getResourceAsStream(...)` to return a resource's contents as a
UTF-8 string.

## The bug

`Read.resourceAsString(String)` resolves the resource by calling
`Read.class.getResourceAsStream(...)`. That always uses the classloader of
the *Read* class.

In a standard application classpath this is fine — every class shares one
classloader, so any resource shipped with Selenium is visible. **In an OSGi
container it is not**: each bundle gets its own isolated classloader, and
`Read.class.getResourceAsStream(...)` only sees resources packaged in the
bundle that ships `Read` itself. Resources that live in other Selenium
bundles (for example `isDisplayed.js`, `mutation-listener.js`,
`bidi-mutation-listener.js`, the W3C atom files, …) are not found, and
`Read.resourceAsString(...)` fails with `IllegalArgumentException: Resource
not found: …`.

This regression is tracked at upstream issue #17251.

## What you need to do

Make `org.openqa.selenium.io.Read` resolve resources through a
caller-supplied class so that, in OSGi, callers can pass a class from
*their own* bundle and reach their bundle's resources.

Concretely:

1. **Add a new public static method** on `Read`:

   ```java
   public static String resourceAsString(Class<?> resourceOwner, String resource)
   ```

   It must read the resource by calling `getResourceAsStream(...)` on the
   classloader associated with `resourceOwner`, decode the bytes as UTF-8,
   and return the result. If the resource is not found, throw the same
   `IllegalArgumentException("Resource not found: " + resource)` the
   existing method throws.

2. **Validate the new parameter.** A null `resourceOwner` must raise a
   `NullPointerException` whose message contains the literal text
   `Class owning the resource` (so callers see which argument was bad).

3. **Keep backward compatibility.** The existing
   `Read.resourceAsString(String)` method must continue to work
   (downstream users on classic classpath setups should not have to touch
   their call sites). Mark it `@Deprecated` and have its javadoc point
   readers at the new overload as the OSGi-safe replacement; internally,
   delegate to the new method passing `Read.class`.

4. **Migrate the in-repo callers** that load resources packaged in a
   *different* selenium module from `Read`, so production code paths get
   the OSGi-correct behaviour. The callers that load JS atom resources
   from outside the `org.openqa.selenium.io` package should pass a class
   from the calling bundle (typically `getClass()` for instance methods,
   or the enclosing class for static contexts) to the new overload.

The repo-level [`AGENTS.md`](https://github.com/SeleniumHQ/selenium/blob/36fc8f9b7bdedeba3884fadc232aec76fcd044c1/AGENTS.md)
makes API/ABI compatibility a hard invariant ("users upgrade by changing
only version number") and asks for small, reversible diffs — no
package-wide refactor.
The Java-specific [`java/AGENTS.md`](https://github.com/SeleniumHQ/selenium/blob/36fc8f9b7bdedeba3884fadc232aec76fcd044c1/java/AGENTS.md)
requires Javadoc on public APIs and that deprecated methods point at
their replacement.

## How you'll be graded

The harness compiles `Read.java` standalone and exercises it from small
inline Java helpers. Among the things it checks:

- The new 2-arg overload exists with the exact signature
  `static String resourceAsString(Class<?>, String)` and is callable.
- Calling the overload with a class loaded by a *separate* `URLClassLoader`
  (which has the requested resource on its URL list, but is **not** on
  Read's classpath) successfully returns the resource — i.e. the
  implementation really does dispatch through the supplied class's
  classloader, not Read's.
- A null first argument throws `NullPointerException` containing
  `Class owning the resource`.
- The original `resourceAsString(String)` is retained and carries the
  `@Deprecated` annotation.
- The original `resourceAsString(String)` still loads a resource from
  Read's own classloader.

The grader does not run a full Bazel build, so you do not need to worry
about `BUILD.bazel` files; just keep the Java source compilable.
