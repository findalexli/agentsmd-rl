# ExecuteMethod Interface Breaking External Implementations

## Problem

The `ExecuteMethod` interface in `java/src/org/openqa/selenium/remote/ExecuteMethod.java` has a signature that breaks backward compatibility with external implementations.

The current interface defines `execute()` with a generic return type `<T> T`, which causes problems for projects like Appium that have their own implementations of this interface (e.g., `AppiumExecutionMethod`). When these external classes try to override the method, they encounter type inference issues with the generic return type.

## Impact

External projects that extend Selenium's `ExecuteMethod` interface cannot upgrade to newer Selenium versions without code changes, violating the principle that users should be able to upgrade by changing only the version number.

## Requirements

### 1. Change `execute()` return type

The `execute(String commandName, Map<String, ?> parameters)` method needs a return type that works with external implementations — it cannot use a generic type parameter `T`. The return type must be a concrete type (such as `Object`) that external implementations can override without type inference conflicts.

### 2. Add convenient overload methods

The interface must provide the following default methods (exact signatures and names matter):

- `execute(String commandName, @Nullable Map<String, ?> parameters, T defaultValue)` — a default method that returns `defaultValue` when `execute` returns null. This method must use `Objects.requireNonNullElse` from the standard library.
- `executeAs(String commandName, @Nullable Map<String, ?> parameters)` — a default method that casts the result to `T` and enforces non-null via `Objects.requireNonNull`. This method replaces the existing `executeRequired` method which should be removed from the interface.
- `execute(String commandName)` — a single-argument default method that calls `execute(commandName, null)` and casts the result to `T`.

### 3. Remove the old `executeRequired` method

The existing `executeRequired` method that enforces non-null return values must be removed entirely from the interface. Call sites currently using `executeRequired` must be updated to use `executeAs` or one of the new convenience methods.

### 4. Add required import

The interface must import `java.util.Objects.requireNonNullElse` (static import) for the default value fallback method.

### 5. Suppress unchecked cast warnings

Methods that perform unchecked casts from `Object` to `T` must have `@SuppressWarnings("unchecked")` annotations. At least three such annotations are required in the interface.

### 6. Document new methods

New public methods must have Javadoc documentation. The interface should contain at least three Javadoc blocks.

### 7. Update call sites

All call sites using `executeRequired` must be updated:
- `java/src/org/openqa/selenium/chromium/AddHasCasting.java` — update to use the `execute(cmd, params, defaultValue)` overload for default-value cases and `execute(cmd)` for non-null cases
- `java/src/org/openqa/selenium/chromium/AddHasCdp.java` — update to use `executeAs`
- `java/src/org/openqa/selenium/firefox/AddHasExtensions.java` — update to use `executeAs`
- Other files as needed

### 8. Maintain existing code quality

All modified files must use spaces (not tabs) for indentation, have no trailing whitespace, and include the Apache License copyright header.

## Files to Examine

- `java/src/org/openqa/selenium/remote/ExecuteMethod.java` — the interface to modify
- `java/src/org/openqa/selenium/remote/RemoteExecuteMethod.java` — implementation
- `java/src/org/openqa/selenium/remote/LocalExecuteMethod.java` — implementation
- `java/src/org/openqa/selenium/chromium/AddHasCasting.java` — call site
- `java/src/org/openqa/selenium/chromium/AddHasCdp.java` — call site
- `java/src/org/openqa/selenium/firefox/AddHasExtensions.java` — call site
- Various other call sites in `java/src/org/openqa/selenium/chromium/`, `java/src/org/openqa/selenium/firefox/`, `java/src/org/openqa/selenium/safari/`
