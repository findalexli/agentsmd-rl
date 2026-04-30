# Fix CDP Domain Lifecycle in Selenium .NET Bindings

## Problem

The Chrome DevTools Protocol (CDP) domain adapter classes in the Selenium .NET bindings have a lifecycle bug. The `Network`, `JavaScript`, `Target`, and `Log` properties in the domain classes return new instances on every access instead of returning the same cached instance.

This causes the following issues:
- Event handlers registered on a domain instance are lost on subsequent property access
- State set on domain objects does not persist across accesses
- Multiple references to the same property compare as different objects (`ReferenceEquals(domains.Network, domains.Network)` returns `false`)

## Required Fix

The following three files must be modified:
- `dotnet/src/webdriver/DevTools/v143/V143Domains.cs`
- `dotnet/src/webdriver/DevTools/v144/V144Domains.cs`
- `dotnet/src/webdriver/DevTools/v145/V145Domains.cs`

Each file contains four properties that return new instances and must be modified to return the same instance on every access:
- `Network` property returning `DevTools.Network`
- `JavaScript` property returning `JavaScript`
- `Target` property returning `DevTools.Target`
- `Log` property returning `DevTools.Log`

The implementation requirements are:
1. Each property must return the same instance on every access (verified by `Is.SameAs` assertions in tests)
2. Instances must be initialized lazily on first access (not eagerly in the constructor)
3. The implementation must use `System.Lazy<T>` for thread-safe lazy initialization

The specific implementation patterns required in each file are:

**Fields (4 per file):**
- `private readonly Lazy<V143Network> network` (use `V144Network`, `V145Network` for respective versions)
- `private readonly Lazy<V143JavaScript> javaScript` (use `V144JavaScript`, `V145JavaScript` for respective versions)
- `private readonly Lazy<V143Target> target` (use `V144Target`, `V145Target` for respective versions)
- `private readonly Lazy<V143Log> log` (use `V144Log`, `V145Log` for respective versions)

**Constructor initialization (4 lines per file):**
- `this.network = new Lazy<V143Network>(() => new V143Network(domains.Network, domains.Fetch))`
- `this.javaScript = new Lazy<V143JavaScript>(() => new V143JavaScript(domains.Runtime, domains.Page))`
- `this.target = new Lazy<V143Target>(() => new V143Target(domains.Target))`
- `this.log = new Lazy<V143Log>(() => new V143Log(domains.Log))`

**Property implementations (4 per file):**
- `public override DevTools.Network Network => this.network.Value`
- `public override JavaScript JavaScript => this.javaScript.Value`
- `public override DevTools.Target Target => this.target.Value`
- `public override DevTools.Log Log => this.log.Value`

## Test File

Create `dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs` with test assertions that verify:
- `domains.Log` returns the same instance on multiple accesses using `Is.SameAs(domains.Log)`
- `domains.Network` returns the same instance on multiple accesses using `Is.SameAs(domains.Network)`
- `domains.Target` returns the same instance on multiple accesses using `Is.SameAs(domains.Target)`
- `domains.JavaScript` returns the same instance on multiple accesses using `Is.SameAs(domains.JavaScript)`

## Repository Guidelines

- Follow existing code style and XML documentation patterns
- Build with: `dotnet build dotnet/src/webdriver/WebDriver.csproj`
