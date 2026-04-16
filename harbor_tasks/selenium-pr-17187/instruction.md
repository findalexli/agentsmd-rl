# Fix JSON Deserialization Error for Duplicate Field Names

## Problem

When deserializing JSON into a Java class where both a parent class and child class declare a field with the same name, the JSON library throws an unclear `IllegalStateException` from an internal Java collector. The error does not explain that duplicate field names caused the failure.

For example, given these classes:

```java
class Parent {
    String value;
}

class Child extends Parent {
    String value;  // Same name as parent field
}
```

Attempting to deserialize `{"value": "test"}` into `Child.class` using field-based setting (`BY_FIELD`) produces an `IllegalStateException` with a message like "Key already exists" — unhelpful and misleading.

## Expected Behavior

When duplicate field names are detected in a class hierarchy during JSON deserialization, the library should throw a `JsonException` with a descriptive message. The error message must include the exact phrase:

```
Duplicate JSON field name detected while collecting field writers
```

Additionally, the code that detects this condition must use a merge function with parameters named exactly `(existing, replacement) ->` as the third argument to the `Collectors.toMap` call in the relevant collection method.

## Where to Look

The issue occurs in the JSON library's instance coercion code, in a class named `InstanceCoercer` located in the `java/src/org/openqa/selenium/json/` directory. Look for the method that collects field writers using `Collectors.toMap` — it currently takes two arguments but needs a third merge-function argument to handle duplicate keys gracefully.

## Verification

After the fix:
1. The JSON library must build successfully with `bazel build //java/src/org/openqa/selenium/json:json`
2. The existing JSON test suite must still pass: `bazel test //java/test/org/openqa/selenium/json:SmallTests --test_output=errors`
3. Core and remote tests must continue to pass to ensure no regressions