# Fix: RuntimeException handling in Lazy.java

## Problem

The `Lazy.java` class in Selenium's concurrent utilities has a bug in its exception handling. When a `RuntimeException` is thrown by the supplier during lazy initialization, it gets incorrectly wrapped in an `InitializationException`, losing the original exception type and making it harder for callers to handle specific runtime errors.

## File to Modify

`java/src/org/openqa/selenium/concurrent/Lazy.java`

## Current Behavior

In the `get()` method of `Lazy.java`, the code catches `Exception` and wraps it in `InitializationException`. Since `RuntimeException` extends `Exception`, runtime exceptions are being wrapped when they should be re-thrown directly.

## Expected Behavior

1. `RuntimeException` (and its subclasses like `IllegalStateException`, `IllegalArgumentException`, etc.) should be re-thrown as-is without wrapping
2. Checked exceptions (non-RuntimeException) should continue to be wrapped in `InitializationException`

## Example

```java
Lazy<String> lazy = new Lazy<>(() -> {
    throw new IllegalStateException("connection failed");
});

// Currently: Throws InitializationException with IllegalStateException as cause
// Expected: Throws IllegalStateException directly
String result = lazy.get();
```

## Testing

You can test your fix by writing a small Java program that:
1. Creates a `Lazy` with a supplier that throws `IllegalStateException`
2. Calls `get()` and verifies that `IllegalStateException` is thrown (not `InitializationException`)
3. Tests with other RuntimeException subclasses to ensure they are all preserved

## Notes

- The repository uses Bazel for building. You can compile the concurrent package with: `bazel build //java/src/org/openqa/selenium/concurrent:concurrent`
- See `java/AGENTS.md` for Java-specific coding conventions
- The fix should be minimal - only a few lines of code need to change
