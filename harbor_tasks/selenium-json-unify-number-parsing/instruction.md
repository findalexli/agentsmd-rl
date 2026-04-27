# Unify JSON number parsing in Selenium's Java bindings

The Selenium Java JSON layer currently has three different code paths that
parse numeric values, and they disagree on edge cases. The repository is
already cloned at `/workspace/selenium`; only the
`java/src/org/openqa/selenium/json/` package should need to change.

Make all three paths funnel through a single number reader so that the
behaviors below all hold.

## Behaviors to fix

### 1. Coercing a `Number` whose magnitude exceeds `Long` range

When the JSON value parses to a magnitude larger than `Long.MAX_VALUE` or
smaller than `Long.MIN_VALUE` (e.g. `-1e20`), deserializing as `Number` must
return the floating-point value, not silently clamp to `Long.MIN_VALUE`.
The current code only guards against the positive-overflow direction.

After the fix:

```java
Number n = (Number) new Json().toType("-1e20", Number.class);
assert Math.abs(n.doubleValue() - (-1e20)) < 1e10;    // currently fails — returns Long.MIN_VALUE
```

### 2. Parsing a numeric `Instant` regardless of whether it was JSON-quoted

Today, when an `Instant` field receives a JSON **string** that holds a numeric
timestamp, the coercer rejects anything that isn't a digits-only run of
characters (no leading sign). A bare JSON number containing the same value
parses fine. The two paths should agree.

After the fix:

```java
Instant i = (Instant) new Json().toType("\"-1234\"", Instant.class);
assert i.toEpochMilli() == -1234L;                    // currently throws JsonException
```

In addition, `InstantCoercer` should first attempt to parse the string with
`DateTimeFormatter.ISO_INSTANT`; only if that fails should it fall back to
the numeric path.

## Required API additions / changes on `JsonInput`

To support the unified number path, two API edits to
`org.openqa.selenium.json.JsonInput` are required:

- **Add a public method `void nextEnd()`** that asserts the current token is
  the end of the input stream (delegating to `expect(JsonType.END)`).  It
  should throw a `JsonException` if any unread tokens remain. The unified
  number path uses this to make sure a string like `"3.14"` was fully
  consumed and didn't have trailing junk.
- **Mark `Instant nextInstant()` as `@Deprecated(forRemoval = true)`.**  The
  method is unused, has no unit tests, and differs from every other
  `next…` method in being `@Nullable`. Add a `@deprecated` Javadoc tag
  pointing to `InstantCoercer` as the replacement; do not delete the
  method.

## Constraints

- Maintain API/ABI compatibility for everything that is already public or
  package-private — users upgrade by changing only the version number.
- The fix should be confined to the `java/src/org/openqa/selenium/json/`
  package. Do not touch other packages, BUILD.bazel files, or tests.
- Prefer reusing the existing `JsonInput.nextNumber()` reader over hand-rolled
  string-to-number parsing (`BigDecimal`, `BigInteger`, regex `\d+`, …).
- Follow the project's deprecation idiom from `java/AGENTS.md`:
  ```java
  @Deprecated(forRemoval = true)
  public void legacyMethod() { }
  ```
- Keep diffs small and reversible (root `AGENTS.md`: "avoid repo-wide
  refactors/formatting; prefer small, reversible diffs").

## How your changes are verified

The grader compiles only the `java/src/org/openqa/selenium/json/` package
against the published `selenium-api` jar and runs targeted Java assertions
against your modifications. The package must compile cleanly. Existing
behaviors (boolean / integer / double parsing, ISO-8601 instant strings,
`Map` round-trips) must continue to hold.
