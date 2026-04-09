# Task: Refactor BiDi Network Interception API

## Problem Description

The Selenium .NET BiDi (Bidirectional) implementation currently has two different ways to handle network interception:

1. **High-level convenience methods** like `InterceptRequestAsync`, `InterceptResponseAsync`, and `InterceptAuthAsync` that combine intercept creation and event handling
2. **Lower-level primitives** like `AddInterceptAsync` with explicit event subscriptions via `OnBeforeRequestSentAsync`, `OnResponseStartedAsync`, and `OnAuthRequiredAsync`

The high-level API provides a simplified interface but adds complexity and maintenance overhead. The goal is to simplify the API surface by removing the high-level interception methods and consolidating on the lower-level, more flexible primitives.

## Your Task

Remove the high-level network interception API from the BiDi implementation. This includes:

1. **Remove from `INetworkModule` interface** (`dotnet/src/webdriver/BiDi/Network/INetworkModule.cs`):
   - `InterceptRequestAsync`
   - `InterceptResponseAsync`
   - `InterceptAuthAsync`

2. **Remove from `IBrowsingContextNetworkModule` interface** (`dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs`):
   - `InterceptRequestAsync`
   - `InterceptResponseAsync`
   - `InterceptAuthAsync`

3. **Remove from `BrowsingContextNetworkModule` class** (`dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs`):
   - The three method implementations
   - Associated option types: `InterceptRequestOptions`, `InterceptResponseOptions`, `InterceptAuthOptions`

4. **Delete the entire file** `dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs` which contains:
   - The high-level implementations in `NetworkModule`
   - Option types: `InterceptRequestOptions`, `InterceptResponseOptions`, `InterceptAuthOptions`
   - Event argument types: `InterceptedRequest`, `InterceptedResponse`, `InterceptedAuth`
   - The `Interception` helper class

## What to Preserve

The following should remain intact as they form the replacement API:

- `AddInterceptAsync` method (creates intercepts)
- `OnBeforeRequestSentAsync`, `OnResponseStartedAsync`, `OnAuthRequiredAsync` (event subscriptions)
- `ContinueRequestAsync`, `ContinueResponseAsync`, `ContinueWithAuthAsync`, `FailRequestAsync`, `ProvideResponseAsync` (request/response handling)
- `RemoveInterceptAsync` (intercept cleanup)

## Files to Modify

1. `dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs` - **DELETE entire file**
2. `dotnet/src/webdriver/BiDi/Network/INetworkModule.cs` - Remove method declarations
3. `dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs` - Remove methods and types
4. `dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs` - Remove method declarations

## Success Criteria

After your changes:
- The solution should compile successfully
- The high-level interception methods should no longer exist on the interfaces or classes
- The associated types (options, event args, Interception class) should be removed
- The lower-level API (`AddInterceptAsync`, event subscription methods) should remain functional

## Notes

- This is a breaking API change that removes public surface area
- The replacement pattern uses `AddInterceptAsync` to create intercepts, then subscribes to events explicitly
- Refer to the existing tests to understand the new usage pattern
