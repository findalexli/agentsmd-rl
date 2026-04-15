# Improve JSON Duplicate Field Error Messages

## Problem

When deserializing JSON in Selenium's Java bindings, if a class inherits a field with the same name as a field in its parent class, a `JsonException` is thrown. The current error message is unhelpful:

```
Duplicate JSON field name detected while collecting field writers
```

This message doesn't tell the user *which* fields are conflicting, making debugging difficult.

## Expected Behavior

The error message should identify the conflicting fields with their full class and field names. The new error message format should be:

```
Duplicate JSON field name detected while collecting field writers:
    FieldWriter(org.openqa.selenium.json.JsonTest$ChildFieldBean.value) vs
    FieldWriter(org.openqa.selenium.json.JsonTest$ParentFieldBean.value)
```

Note: The exact field names and class names will vary depending on the beans involved in the conflict.

## Files to Modify

The error is thrown when merging duplicate field writers during JSON deserialization. Two source files in the Selenium JSON package need updates:

1. `java/src/org/openqa/selenium/json/InstanceCoercer.java` - the main coercer class
2. `java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java` - the property descriptor class

## Required Changes

### InstanceCoercer.java

Add `toString()` methods to these inner classes:

- **FieldWriter** - toString() should include the declaring class name and field name (e.g., `ClassName.fieldName`)
- **SimplePropertyWriter** - toString() should include the property descriptor info
- **TypeAndWriter** - toString() should delegate to `writer.toString()`

Also update the duplicate field merge function to include field comparison information in the error message using a format like `FieldWriter(X) vs FieldWriter(Y)`.

### SimplePropertyDescriptor.java

Add `toString()` method that returns the class simple name and field name (e.g., `ClassName.fieldName`).

## Expected Error Message Format

```
Duplicate JSON field name detected while collecting field writers:
    FieldWriter(org.openqa.selenium.json.JsonTest$ChildFieldBean.value) vs
    FieldWriter(org.openqa.selenium.json.JsonTest$ParentFieldBean.value)
```

The error message should include the full class path and field name for each conflicting field writer.

## Testing

Run the JSON test suite to verify the fix:
```bash
bazel test //java/test/org/openqa/selenium/json:JsonTest
```

The relevant test method is `shouldThrowWhenDuplicateFieldNamesExistWithFieldSetting()`.

## Constraints

- Maintain API compatibility - this is a refactoring that changes internal error messages only
- Follow the existing code style in the Selenium Java codebase
- See `java/AGENTS.md` for code conventions (logging, deprecation, javadoc)
