# Selenium Java HttpClient: tighten interface conventions

You are working in the Selenium monorepo. The Java bindings have an
interface that leaks JDK-internal types and lacks the deprecation marker
the project's own conventions require.

## Repository layout

The Java sources live under `java/src/`. The two source files involved
here are part of the HTTP transport package; their conventions are
governed by `java/AGENTS.md`.

## What is wrong

The public interface
`org.openqa.selenium.remote.http.HttpClient` declares two methods that
expose JDK transport types directly to anyone implementing or consuming
the interface:

- `sendAsyncNative(java.net.http.HttpRequest, java.net.http.HttpResponse.BodyHandler<T>)`
- `sendNative(java.net.http.HttpRequest, java.net.http.HttpResponse.BodyHandler<T>)`

This is wrong on two counts:

1. **Interfaces in this codebase must not expose the native classes of
   their implementations.** The contract of an interface should be
   independent of which concrete client is wired up underneath it. A
   contributor reading the existing `java/AGENTS.md` conventions and
   thinking carefully about interface design should arrive at this rule
   on their own; this PR also encodes it explicitly so future agents do
   not have to re-derive it.
2. **The project's deprecation policy** (root `AGENTS.md` and the
   "Deprecation" example block in `java/AGENTS.md`) says public
   functionality must be marked deprecated *before* removal, with a
   pointer to the replacement.

Concretely, the JDK-typed methods should remain present (so we do not
break ABI on this release) but be marked for removal, and a clean
escape hatch must exist on the implementation class for callers who
genuinely need the underlying `java.net.http.HttpClient`.

## What you must do

1. **Mark both `sendAsyncNative` and `sendNative` for removal.** Use the
   project's standard deprecation mechanism (see the existing
   "Deprecation" code block in `java/AGENTS.md` for the exact form).
   The Javadoc on each method should also gain a `@deprecated` tag
   pointing readers to the replacement.

2. **Provide an accessor for the underlying native client on the JDK
   implementation.** The implementation class
   `org.openqa.selenium.remote.http.jdk.JdkHttpClient` already holds the
   underlying `java.net.http.HttpClient` in a private field named
   `client`. Expose it via a public no-argument method on
   `JdkHttpClient` whose return type is `java.net.http.HttpClient` and
   whose body simply returns that field. This is the recommended path
   forward for callers who previously relied on `sendAsyncNative` /
   `sendNative`.

3. **Update `java/AGENTS.md` to encode the new conventions.** Add a new
   sub-section under `## Code conventions` titled `### Interfaces` with
   two bullet points:

   - New methods added to existing interfaces must provide a default
     implementation, if possible.
   - Interfaces must not expose the native classes of their
     implementations.

   These rules belong in `java/AGENTS.md` (not the root `AGENTS.md`)
   because they are Java-binding-specific — Selenium ships in five
   languages and only Java has interfaces with this exact failure mode.

## Constraints

- Do not delete `sendAsyncNative` or `sendNative`; they must stay
  declared on the interface so this change is ABI-preserving for the
  current release. They simply become deprecated-for-removal.
- Do not change the signatures of those two methods.
- Do not introduce new third-party dependencies.
- Keep the diff small: only the three files listed below should be
  touched.

## Files in scope

- `java/AGENTS.md` (add the new `### Interfaces` sub-section)
- `java/src/org/openqa/selenium/remote/http/HttpClient.java` (deprecate
  the two `*Native` methods)
- `java/src/org/openqa/selenium/remote/http/jdk/JdkHttpClient.java`
  (expose the underlying native client)

## Verification

The Selenium repo is built with Bazel, but you do **not** need to run
the full Bazel build. The grader compiles
`HttpClient.java` in isolation against a stub copy of its package and
inspects the resulting bytecode (annotations, method signatures), so
make sure the source remains compilable as a self-contained interface.
The `JdkHttpClient` change is checked at the source level.
