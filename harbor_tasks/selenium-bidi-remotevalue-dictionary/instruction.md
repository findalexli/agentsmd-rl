# BiDi RemoteValue Dictionary Conversion

The `RemoteValue` class in the Selenium .NET WebDriver BiDi Script module cannot convert `MapRemoteValue` and `ObjectRemoteValue` instances to dictionary types.

## Problem

When working with BiDi (Browser Interface for DevTools) script results, users need to convert `MapRemoteValue` (JavaScript Map) and `ObjectRemoteValue` (JavaScript Object) to .NET dictionary types like `Dictionary<TKey, TValue>` or `IDictionary<TKey, TValue>`.

Currently, attempting to convert these types to dictionaries throws an `InvalidCastException`:

```csharp
var mapValue = new MapRemoteValue { Value = /* key-value pairs */ };
var dict = mapValue.ConvertTo<Dictionary<string, int>>();  // Throws!
```

The `ConvertTo<TResult>()` method in `RemoteValue.cs` handles arrays and lists but does not handle dictionaries.

## Expected Behavior

Add dictionary conversion support by extending the `ConvertTo<TResult>()` method to handle dictionary types when the result type is `Dictionary<,>` or `IDictionary<,>`:

- `MapRemoteValue.ConvertTo<Dictionary<TKey, TValue>>()` should return a dictionary with converted key-value pairs
- `ObjectRemoteValue.ConvertTo<Dictionary<TKey, TValue>>()` should also work (objects have a similar key-value structure)
- Both should support interface types like `IDictionary<TKey, TValue>`
- Empty or null remote values should convert to empty dictionaries
- The existing array and list conversion functionality must remain intact

## File

- `dotnet/src/webdriver/BiDi/Script/RemoteValue.cs` - Contains the `ConvertTo<TResult>()` method and helper methods for array and list conversions
