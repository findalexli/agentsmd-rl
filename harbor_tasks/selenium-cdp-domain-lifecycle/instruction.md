# Fix CDP Domain Lifecycle in Selenium .NET Bindings

## Problem

The Chrome DevTools Protocol (CDP) domain adapter classes (`V143Domains`, `V144Domains`, `V145Domains`) have a lifecycle bug. Each time you access the `Network`, `JavaScript`, `Target`, or `Log` properties, a **new instance** is created instead of returning a cached instance.

This causes issues because:
- Event handlers registered on one instance are lost when a new instance is created
- State set on the domain object doesn't persist across property accesses
- Multiple references to the same property compare as different objects

## Affected Files

- `dotnet/src/webdriver/DevTools/v143/V143Domains.cs`
- `dotnet/src/webdriver/DevTools/v144/V144Domains.cs`
- `dotnet/src/webdriver/DevTools/v145/V145Domains.cs`

## What You Need to Do

Modify the three `V*Domains.cs` files to ensure that accessing `Network`, `JavaScript`, `Target`, or `Log` properties always returns the **same instance** (reference equality).

### Implementation Guidance

The standard C# pattern for lazy-initialized properties is:

1. Add private `readonly Lazy<T>` fields for each domain object
2. Initialize these fields in the constructor with factory lambdas
3. Change property getters to return `this.field.Value` instead of `new DomainType(...)`

Example pattern:
```csharp
public class V143Domains : DevToolsDomains
{
    private readonly Lazy<V143Network> network;

    public V143Domains(DevToolsSession session)
    {
        this.network = new Lazy<V143Network>(() => new V143Network(...));
    }

    public override DevTools.Network Network => this.network.Value;
}
```

## Expected Behavior

After your fix:
- `domains.Network == domains.Network` should return `true` (same reference)
- `domains.Log == domains.Log` should return `true`
- `domains.Target == domains.Target` should return `true`
- `domains.JavaScript == domains.JavaScript` should return `true`

## Testing

You should also create a test file at `dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs` that verifies the domain accessors return the same instance on multiple accesses.

## Repository Guidelines

- Follow existing code style and XML documentation patterns
- The codebase uses `Lazy<T>` for deferred initialization - use this approach
- Build with: `dotnet build dotnet/src/webdriver/WebDriver.csproj`
