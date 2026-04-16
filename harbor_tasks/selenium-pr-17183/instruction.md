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

- A method that takes a command name, parameters, and a default value — returning the default when `execute` returns null. This method must use `Objects.requireNonNullElse` from the standard library.
- A method that takes just a command name and parameters — returning a non-null value by casting the result and enforcing non-null via `Objects.requireNonNull`. This method replaces a method that should be removed from the interface.
- A single-argument method that takes only a command name — calling the two-argument form with null parameters and casting the result.

### 3. Remove the old method

An existing method that enforces non-null return values must be removed entirely from the interface. Call sites currently using this method must be updated to use one of the new convenience methods.

### 4. Add required import

The interface must import `java.util.Objects.requireNonNullElse` (static import) for the default value fallback method.

### 5. Suppress unchecked cast warnings

Methods that perform unchecked casts from `Object` to `T` must have `@SuppressWarnings("unchecked")` annotations. At least three such annotations are required in the interface.

### 6. Document new methods

New public methods must have Javadoc documentation. The interface should contain at least three Javadoc blocks.

### 7. Update call sites

All call sites using the old method must be updated:
- `java/src/org/openqa/selenium/chromium/AddHasCasting.java` — update to use the new default-value method
- `java/src/org/openqa/selenium/chromium/AddHasCdp.java` — update to use the new non-null casting method
- `java/src/org/openqa/selenium/firefox/AddHasExtensions.java` — update to use the new non-null casting method
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
