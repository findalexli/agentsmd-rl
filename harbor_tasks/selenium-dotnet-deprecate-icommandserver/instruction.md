# Deprecate `ICommandServer` and detach it from `DriverService`

You are working in the Selenium .NET bindings (`dotnet/src/webdriver/`) of the
Selenium monorepo. The class hierarchy currently routes the `Start()` /
`Dispose()` contract of every browser-driver service through a public
interface called `ICommandServer`, defined in
`dotnet/src/webdriver/Remote/ICommandServer.cs`:

```csharp
namespace OpenQA.Selenium.Remote;

public interface ICommandServer : IDisposable
{
    void Start();
}
```

`ICommandServer` is consumed in exactly one place: the abstract
`DriverService` base class declares it as a base type:

```csharp
public abstract class DriverService : ICommandServer
```

No external code ever holds a `DriverService` as an `ICommandServer`. The
interface adds nothing the abstract class doesn't already provide, and it
forces every consumer of `DriverService` to drag in
`OpenQA.Selenium.Remote`. Your job is to retire `ICommandServer` from the
public surface of `DriverService` while honouring the project's deprecation
policy.

## What to change

### `DriverService`

`DriverService` must continue to satisfy the `IDisposable` contract its
existing callers depend on, but it must no longer name `ICommandServer` in
its base/inheritance list. Replacing the inherited interface with a direct
`IDisposable` declaration is the minimal change that preserves callers.

When `ICommandServer` is removed from the inheritance list, `DriverService`
no longer transitively pulls types out of the `OpenQA.Selenium.Remote`
namespace, so any `using OpenQA.Selenium.Remote;` directive in this file
that was added solely for the interface should be removed if it is no
longer needed.

If, after the inheritance change, `DriverService` no longer references any
type from a particular `using` directive, that `using` should be removed
too — the file's `using` list should not contain imports that the file no
longer uses.

### `ICommandServer`

`ICommandServer` itself must remain in the codebase (we cannot delete it
outright; downstream projects such as Appium reference it). It must,
however, be marked as deprecated so that consumers receive a compiler
warning when they reference it.

The deprecation must follow the project's policy in
[`dotnet/AGENTS.md`](https://raw.githubusercontent.com/SeleniumHQ/selenium/77f325f198b2d660b8bba483623fe9770a08f77a/dotnet/AGENTS.md):

> ```csharp
> [Obsolete("Use NewMethod instead")]
> public void OldMethod() { }
> ```

and the root [`AGENTS.md`](https://raw.githubusercontent.com/SeleniumHQ/selenium/77f325f198b2d660b8bba483623fe9770a08f77a/AGENTS.md):

> Deprecation policy: This project does not follow semantic versioning
> (semver); before removing public functionality, mark it as deprecated
> with a message pointing to the alternative.

The deprecation message you attach to `ICommandServer` must:

* be a non-empty string passed as the first positional argument to
  `[Obsolete(...)]`, and
* clearly tell consumers that the interface is on its way out — either by
  using the word "remove" / "removal", by mentioning a "future release",
  or by stating that the interface "no longer" supports them. A message
  that simply says "deprecated" without explaining what comes next is not
  sufficient.

## What stays the same

* The behaviour of `DriverService` (process management, port handling,
  `Dispose()` semantics, etc.) does not change.
* The shape of `ICommandServer` (its `Start()` member and `IDisposable`
  inheritance) does not change.
* The file `ICommandServer.cs` should not be deleted, renamed, or moved.

## Files in scope

The change is limited to two files:

* `dotnet/src/webdriver/DriverService.cs`
* `dotnet/src/webdriver/Remote/ICommandServer.cs`

You should not need to modify any other source files, project files, or
build configuration to complete this task.
