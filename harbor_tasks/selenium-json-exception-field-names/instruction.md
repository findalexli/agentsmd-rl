# Task: Improve JSON Duplicate Field Error Messages

## Problem

When deserializing JSON in Selenium's Java bindings, if a class inherits a field with the same name as a field in its parent class, a `JsonException` is thrown. However, the current error message is unhelpful:

```
Duplicate JSON field name detected while collecting field writers
```

This message doesn't tell the user *which* fields are conflicting, making debugging difficult.

## Expected Behavior

The error message should identify the conflicting fields with their full class and field names:

```
Duplicate JSON field name detected while collecting field writers:
    FieldWriter(org.openqa.selenium.json.JsonTest$ChildFieldBean.value) vs
    FieldWriter(org.openqa.selenium.json.JsonTest$ParentFieldBean.value)
```

## Files to Modify

1. **`java/src/org/openqa/selenium/json/InstanceCoercer.java`**
   - The `getFieldWriters()` and `getBeanWriters()` methods collect field writers
   - Currently uses anonymous lambdas for field/property writers
   - The merge function throws a generic exception without field information

2. **`java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java`**
   - Needs a `toString()` method to identify the property

## Key Implementation Points

- The field writers are currently anonymous lambdas that don't have useful `toString()` implementations
- When the merge conflict function is called, it receives `existing` and `replacement` TypeAndWriter objects
- TypeAndWriter should delegate its `toString()` to the underlying writer's `toString()`
- FieldWriter and SimplePropertyWriter classes should be created with proper `toString()` methods

## Testing

The relevant test is in `java/test/org/openqa/selenium/json/JsonTest.java`:
- Test method: `shouldThrowWhenDuplicateFieldNamesExistWithFieldSetting()`
- Run with: `bazel test //java/test/org/openqa/selenium/json:JsonTest`

## Constraints

- Maintain API compatibility - this is a refactoring that changes internal error messages only
- Follow the existing code style in the Selenium Java codebase
- See `java/AGENTS.md` for code conventions (logging, deprecation, javadoc)
