# Fix CDP Domain Lifecycle in Selenium .NET Bindings

## Problem

The Chrome DevTools Protocol (CDP) domain adapter classes (`V143Domains`, `V144Domains`, `V145Domains`) have a lifecycle bug. Each time you access the `Network`, `JavaScript`, `Target`, or `Log` properties, a **new instance** is created instead of returning a cached instance.

This causes issues because:
- Event handlers registered on one instance are lost when a new instance is created
- State set on the domain object doesn't persist across property accesses
- Multiple references to the same property compare as different objects (`domains.Network != domains.Network`)

## Affected Files

- `dotnet/src/webdriver/DevTools/v143/V143Domains.cs`
- `dotnet/src/webdriver/DevTools/v144/V144Domains.cs`
- `dotnet/src/webdriver/DevTools/v145/V145Domains.cs`

## Required Changes

Modify the three `V*Domains.cs` files to ensure that accessing `Network`, `JavaScript`, `Target`, or `Log` properties always returns the **same instance** on subsequent accesses (reference equality).

### Specific Requirements

**For V143Domains:**
- The `Network` property currently creates `new V143Network(domains.Network, domains.Fetch)` - this must be cached
- The `JavaScript` property currently creates `new V143JavaScript(domains.Runtime, domains.Page)` - this must be cached
- The `Target` property currently creates `new V143Target(domains.Target)` - this must be cached
- The `Log` property currently creates `new V143Log(domains.Log)` - this must be cached

**For V144Domains:**
- The `Network` property currently creates `new V144Network(domains.Network, domains.Fetch)` - this must be cached
- The `JavaScript` property currently creates `new V144JavaScript(domains.Runtime, domains.Page)` - this must be cached
- The `Target` property currently creates `new V144Target(domains.Target)` - this must be cached
- The `Log` property currently creates `new V144Log(domains.Log)` - this must be cached

**For V145Domains:**
- The `Network` property currently creates `new V145Network(domains.Network, domains.Fetch)` - this must be cached
- The `JavaScript` property currently creates `new V145JavaScript(domains.Runtime, domains.Page)` - this must be cached
- The `Target` property currently creates `new V145Target(domains.Target)` - this must be cached
- The `Log` property currently creates `new V145Log(domains.Log)` - this must be cached

## Expected Behavior

After your fix:
- `domains.Network == domains.Network` should return `true` (same reference)
- `domains.Log == domains.Log` should return `true`
- `domains.Target == domains.Target` should return `true`
- `domains.JavaScript == domains.JavaScript` should return `true`

## Testing

Create a test file at `dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs` that verifies the domain accessors return the same instance on multiple accesses using `Is.SameAs()` assertions for `domains.Log`, `domains.Network`, `domains.Target`, and `domains.JavaScript`.

## Repository Guidelines

- Follow existing code style and XML documentation patterns
- Build with: `dotnet build dotnet/src/webdriver/WebDriver.csproj`
