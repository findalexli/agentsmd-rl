# Fix RuntimeException handling in Lazy.java

## Problem

The `Lazy.java` class in the Selenium concurrent utilities has a bug in its exception handling. Currently, when a `RuntimeException` is thrown by the supplier during lazy initialization, it gets caught by the generic `catch (Exception e)` block and wrapped in an `InitializationException`. This loses the original exception type and prevents proper exception propagation.

## Expected Behavior

- `RuntimeException` (and its subclasses like `IllegalStateException`, `NullPointerException`, etc.) should propagate directly without being wrapped
- Checked exceptions should continue to be wrapped in `InitializationException` as they cannot be thrown directly from the `get()` method

## File to Modify

`java/src/org/openqa/selenium/concurrent/Lazy.java`

## What You Need to Do

1. Look at the exception handling in the `get()` method
2. Add a specific `catch (RuntimeException e)` block that re-throws the exception as-is
3. Ensure this new catch block comes BEFORE the generic `catch (Exception e)` block (order matters for exception handling)
4. The fix should be minimal - just 2 lines added (the catch clause and the throw statement)

## Verification

The fix should allow code like this to catch the original exception type:

```java
Lazy<String> lazy = new Lazy<>(() -> {
    throw new IllegalStateException("error");
});

try {
    lazy.get();
} catch (IllegalStateException e) {
    // This should work - RTE propagates directly
}
```

## References

- The `InitializationException` class is in the same package
- This is a concurrent utility using double-checked locking pattern
- Related test files show the expected behavior
