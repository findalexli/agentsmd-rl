# Refactor BiDi Input Actions Serialization

The .NET WebDriver's BiDi Input Actions model currently uses a custom JSON converter (`InputSourceActionsConverter`) for serializing action types. This approach is outdated and should be modernized to use native .NET polymorphic serialization features.

## Problem

The current implementation in `dotnet/src/webdriver/BiDi/Input/SourceActions.cs` relies on:
1. A custom `JsonConverter` attribute pointing to `InputSourceActionsConverter`
2. Mutable collection patterns (`IList<ISourceAction>` with `Add()` method)
3. Interface-based inheritance hierarchies with abstract base classes
4. Type names that don't clearly indicate they are BiDi source actions

Additionally, `dotnet/src/webdriver/BiDi/Input/SequentialSourceActions.cs` contains commented-out experimental code that should be removed.

The custom converter in `dotnet/src/webdriver/BiDi/Json/Converters/Enumerable/InputSourceActionsConverter.cs` manually handles serialization logic that can now be handled natively by `System.Text.Json`.

## Required Changes

1. **Remove custom serialization**: Delete `InputSourceActionsConverter.cs` and remove its usage from `SourceActions.cs`

2. **Adopt polymorphic serialization**: Use `[JsonPolymorphic]` and `[JsonDerivedType]` attributes on `SourceActions` base class for native type discrimination

3. **Modernize action types**:
   - Rename `KeyActions` → `KeySourceActions`
   - Rename `PointerActions` → `PointerSourceActions` (rename `Options` property to `Parameters`)
   - Rename `WheelActions` → `WheelSourceActions`
   - Rename `NoneActions` → `NoneSourceActions`
   - Change from mutable collection pattern (`IList<ISourceAction>` with `Add()`) to immutable (`IEnumerable<T>` in constructor)
   - Remove abstract base classes (`KeySourceAction`, `PointerSourceAction`, `WheelSourceAction`, `NoneSourceAction`) - have action records implement interfaces directly

4. **Update numeric types**: Change `int` to `long` for properties like `Button`, `Width`, `Height`, `Twist`, `Duration`, `X`, `Y`, `DeltaX`, `DeltaY` for consistency with WebDriver BiDi spec

5. **Update InputModule.cs**: Remove the `[JsonSerializable]` attributes for `IEnumerable<I*SourceAction>` types from the serializer context (no longer needed with polymorphic serialization)

6. **Delete SequentialSourceActions.cs**: Remove the file containing commented experimental code

7. **Update test file**: Modify `dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs` to use the new API with immutable collection initializers (`new Type(id, [actions])` instead of `new Type(id) { actions }`)

## Files to Modify

- `dotnet/src/webdriver/BiDi/Input/SourceActions.cs` - Modernize type hierarchy
- `dotnet/src/webdriver/BiDi/Input/InputModule.cs` - Remove obsolete serialization attributes
- `dotnet/src/webdriver/BiDi/Input/SequentialSourceActions.cs` - Delete
- `dotnet/src/webdriver/BiDi/Json/Converters/Enumerable/InputSourceActionsConverter.cs` - Delete
- `dotnet/test/webdriver/BiDi/Input/CombinedInputActionsTests.cs` - Update API usage

## References

See the .NET `System.Text.Json` polymorphic serialization documentation for proper usage of `JsonPolymorphic` and `JsonDerivedType` attributes.
