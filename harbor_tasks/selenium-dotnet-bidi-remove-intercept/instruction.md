# Task: Remove High-Level BiDi Network Interception API

## Problem

The Selenium .NET BiDi bindings currently expose high-level network interception convenience methods (`InterceptRequestAsync`, `InterceptResponseAsync`, `InterceptAuthAsync`) that combine intercept registration with event handler setup. These high-level methods need to be removed in favor of the lower-level `AddInterceptAsync` API combined with explicit event subscriptions.

## What You Need To Do

1. **Remove the high-level interception API** from:
   - `dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs` (delete entire file)
   - `dotnet/src/webdriver/BiDi/Network/NetworkModule.cs` (remove any partial class methods)
   - `dotnet/src/webdriver/BiDi/Network/INetworkModule.cs` (remove interface methods)
   - `dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs` (remove methods)
   - `dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs` (remove interface methods)

2. **Remove associated types** that were defined in the deleted file:
   - `InterceptedRequest`, `InterceptedResponse`, `InterceptedAuth` records
   - `Interception` record with `IAsyncDisposable`
   - `InterceptRequestOptions`, `InterceptResponseOptions`, `InterceptAuthOptions` records

3. **Update tests** in `dotnet/test/webdriver/BiDi/Network/NetworkTests.cs` to use the lower-level API:
   - Replace calls to `InterceptRequestAsync(handler, options)` with:
     1. `AddInterceptAsync([InterceptPhase.BeforeRequestSent], options)`
     2. `OnBeforeRequestSentAsync(handler)` with appropriate filtering
   - Replace calls to `InterceptResponseAsync(handler, options)` with similar pattern using `InterceptPhase.ResponseStarted`
   - Replace calls to `InterceptAuthAsync(handler, options)` with `InterceptPhase.AuthRequired`
   - Event handlers should check `e.IsBlocked && e.Intercepts?.Contains(result.Intercept)` before processing

## Important Notes

- The lower-level `AddInterceptAsync` API already exists and should be used
- All interception is now done through explicit event subscriptions with filtering
- The tests should continue to work with the new lower-level API pattern
- Make sure the code compiles after all changes (`dotnet build`)

## Expected Outcome

After your changes:
- The file `NetworkModule.HighLevel.cs` should not exist
- `InterceptRequestAsync`, `InterceptResponseAsync`, `InterceptAuthAsync` should not exist in any module or interface
- Tests should use `AddInterceptAsync` + `OnBeforeRequestSentAsync`/`OnResponseStartedAsync`/`OnAuthRequiredAsync` pattern
- Code compiles successfully

## Key Files

- `dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs`
- `dotnet/src/webdriver/BiDi/Network/NetworkModule.cs`
- `dotnet/src/webdriver/BiDi/Network/INetworkModule.cs`
- `dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs`
- `dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs`
- `dotnet/test/webdriver/BiDi/Network/NetworkTests.cs`

## Relevant Repository Guidelines

Before making changes, review:
- `dotnet/AGENTS.md` for .NET-specific conventions (async patterns, deprecation, logging, XML docs)
- Root `AGENTS.md` for monorepo-wide guidelines (testing, bazel, etc.)
