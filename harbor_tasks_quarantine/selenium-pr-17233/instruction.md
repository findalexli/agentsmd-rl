# RuntimeException Wrapping Bug in Lazy Class

The `Lazy<T>` class in `java/src/org/openqa/selenium/concurrent/Lazy.java` is a thread-safe lazy initialization utility.

## Problem

When a supplier passed to `Lazy.lazy()` throws a `RuntimeException`, the exception is incorrectly wrapped in an `InitializationException`. This is problematic because:

1. **RuntimeExceptions are unchecked** - they should propagate naturally without wrapping
2. **Callers expect specific exception types** - wrapping changes the exception hierarchy
3. **Stack traces become harder to read** - unnecessary nesting obscures the real error

For example:
```java
Lazy<String> lazy = Lazy.lazy(() -> {
    throw new IllegalStateException("config missing");
});

// Expected: IllegalStateException is thrown directly
// Actual: InitializationException wrapping IllegalStateException is thrown
lazy.get();
```

## Expected Behavior

- `RuntimeException` and its subclasses should be re-thrown directly without wrapping
- Checked exceptions (like `IOException`) should still be wrapped in `InitializationException`
- Normal operation (successful supplier calls) should not be affected

## Files to Examine

- `java/src/org/openqa/selenium/concurrent/Lazy.java` - the lazy initialization utility class
