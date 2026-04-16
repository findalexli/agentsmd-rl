# Improve JSON Exception Error Messages

When parsing JSON into Java objects using the Selenium JSON library, the `Json.toType()` method throws a `JsonException` if a class has duplicate field names (e.g., a child class redefines a field from its parent).

Currently, the error message is unhelpful:

```
Duplicate JSON field name detected while collecting field writers
```

This doesn't tell the user which fields are conflicting or which classes they belong to.

## The Problem

When using `PropertySetting.BY_FIELD` to deserialize JSON into a class that has inherited fields with the same name, the exception message doesn't include the conflicting field information. Users have to manually inspect their class hierarchy to find the duplicate.

For example, if `ChildBean` extends `ParentBean` and both have a `value` field, the error message should identify both conflicting fields.

## Files to Investigate

- `java/src/org/openqa/selenium/json/InstanceCoercer.java` - Contains the field writer collection logic
- `java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java` - Property descriptor class

## Implementation Requirements

The exception message must include the conflicting field names in a format like:

```
Duplicate JSON field name detected while collecting field writers:
  FieldWriter(ChildBean.value) vs FieldWriter(ParentBean.value)
```

To enable this format:

1. **FieldWriter class**: Create a class that implements `BiConsumer<Object, Object>` (in InstanceCoercer.java). This class must have a `toString()` method that returns a string in the format `ClassName.fieldName` (e.g., `FieldWriter(ChildBean.value)`).

2. **SimplePropertyDescriptor changes**: Add a `toString()` method annotated with `@Override` that returns `ClassName.propertyName` format using `clazz.getSimpleName()`. The constructor must accept a `Class<?>` parameter as the first argument to enable this.

The error message merge conflict format must be: `FieldWriter(ClassName.fieldName) vs FieldWriter(ClassName.fieldName)` - specifically including the literal strings "FieldWriter", the class and field names in format `ClassName.fieldName` for each conflicting field, and " vs " between the two field descriptions.
