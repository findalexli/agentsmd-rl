# Fix Domain Lifecycle in CDP Adapters

## Problem

The DevTools Protocol (CDP) domain adapters in the .NET WebDriver have a lifecycle bug. When accessing domain properties like `Network`, `JavaScript`, `Target`, or `Log` on a `DevToolsDomains` instance, a **new wrapper object is created on every access**.

This causes problems:
1. Event subscriptions are lost because each access returns a different object
2. Unnecessary memory allocations on repeated property access
3. State is not preserved between accesses to the same property

## Files Affected

The issue exists in the version-specific domain classes:
- `dotnet/src/webdriver/DevTools/v143/V143Domains.cs`
- `dotnet/src/webdriver/DevTools/v144/V144Domains.cs`
- `dotnet/src/webdriver/DevTools/v145/V145Domains.cs`

## Expected Behavior

Each domain property should return the **same instance** on repeated accesses. For example:
```csharp
var domains = session.Domains;
var network1 = domains.Network;
var network2 = domains.Network;
// network1 and network2 should be the SAME object reference
```

## Required Implementation Details

The fix must use lazy initialization with the following structure:

**1. Private readonly backing fields** (camelCase names):
   - `private readonly Lazy<V143Network> network;` (and similar for V144, V145)
   - `private readonly Lazy<V143JavaScript> javaScript;`
   - `private readonly Lazy<V143Target> target;`
   - `private readonly Lazy<V143Log> log;`

**2. Constructor initialization** using factory lambdas:
   ```csharp
   this.network = new Lazy<V143Network>(() => new V143Network(domains.Network, domains.Fetch));
   this.javaScript = new Lazy<V143JavaScript>(() => new V143JavaScript(domains.Runtime, domains.Page));
   this.target = new Lazy<V143Target>(() => new V143Target(domains.Target));
   this.log = new Lazy<V143Log>(() => new V143Log(domains.Log));
   ```

**3. Property accessors** return the lazy value:
   ```csharp
   public override DevTools.Network Network => this.network.Value;
   public override JavaScript JavaScript => this.javaScript.Value;
   public override DevTools.Target Target => this.target.Value;
   public override DevTools.Log Log => this.log.Value;
   ```

## Requirements

1. Add private readonly backing fields for all four domain properties (Network, JavaScript, Target, Log) using `Lazy<T>` with camelCase names
2. Initialize the lazy fields in the constructor with appropriate factory lambdas
3. Update all four property accessors to return `this.<fieldName>.Value` instead of creating new instances
4. Apply this pattern consistently across all three version files (V143, V144, V145)
5. Maintain API compatibility - the property signatures must not change
6. The `Lazy<T>` type is from `System.Threading` namespace