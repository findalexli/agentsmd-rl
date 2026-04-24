# Improve JSON Duplicate Field Error Messages

## Problem

When deserializing JSON in Selenium's Java bindings, if a class inherits a field with the same name as a field in its parent class, a `JsonException` is thrown. The current error message is unhelpful:

```
Duplicate JSON field name detected while collecting field writers
```

This message doesn't tell the user *which* fields are conflicting, making debugging difficult.

## Expected Behavior

The error message should identify the conflicting fields with their full class and field names. When a duplicate field is detected, the message should show something like:

```
Duplicate JSON field name detected while collecting field writers:
    FieldWriter(org.openqa.selenium.json.JsonTest$ChildFieldBean.value) vs
    FieldWriter(org.openqa.selenium.json.JsonTest$ParentFieldBean.value)
```

The agent should look at the existing test (`shouldThrowWhenDuplicateFieldNamesExistWithFieldSetting` in `JsonTest.java`) to understand the exact expected format.

## Files to Modify

The error is thrown when merging duplicate field writers during JSON deserialization. Two source files in the Selenium JSON package likely need updates:

1. `java/src/org/openqa/selenium/json/InstanceCoercer.java` - handles field writer creation and merging
2. `java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java` - property descriptor class

## Constraints

- The existing test `shouldThrowWhenDuplicateFieldNamesExistWithFieldSetting` in `//java/test/org/openqa/selenium/json:JsonTest` must pass after the fix
- Maintain API compatibility - this changes internal error messages only
- Follow the existing code style in the Selenium Java codebase
- See `java/AGENTS.md` for code conventions (logging, deprecation, javadoc)

## Testing

Run the JSON test suite to verify the fix:
```bash
bazel test //java/test/org/openqa/selenium/json:JsonTest
```

The relevant test method is `shouldThrowWhenDuplicateFieldNamesExistWithFieldSetting()`.