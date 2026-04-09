#!/bin/bash
set -e

cd /workspace/selenium

# Apply the patch to remove high-level network interception methods
patch -p1 <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs b/dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs
index 324b0729336c8..420cc6e6892b8 100644
--- a/dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs
+++ b/dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs
@@ -23,60 +23,6 @@ namespace OpenQA.Selenium.BiDi.BrowsingContext;

 public sealed class BrowsingContextNetworkModule(BrowsingContext context, INetworkModule networkModule) : IBrowsingContextNetworkModule
 {
-    public async Task<Interception> InterceptRequestAsync(Func<InterceptedRequest, Task> handler, InterceptRequestOptions? options = null, CancellationToken cancellationToken = default)
-    {
-        AddInterceptOptions addInterceptOptions = new(options)
-        {
-            Contexts = [context]
-        };
-
-        var interceptResult = await networkModule.AddInterceptAsync([InterceptPhase.BeforeRequestSent], addInterceptOptions, cancellationToken).ConfigureAwait(false);
-
-        Interception interception = new(networkModule, interceptResult.Intercept);
-
-        await interception.OnBeforeRequestSentAsync(
-            async req => await handler(new(req.BiDi, req.Context, req.IsBlocked, req.Navigation, req.RedirectCount, req.Request, req.Timestamp, req.Initiator, req.Intercepts)),
-            new() { Contexts = [context] }).ConfigureAwait(false);
-
-        return interception;
-    }
-
-    public async Task<Interception> InterceptResponseAsync(Func<InterceptedResponse, Task> handler, InterceptResponseOptions? options = null, CancellationToken cancellationToken = default)
-    {
-        AddInterceptOptions addInterceptOptions = new(options)
-        {
-            Contexts = [context]
-        };
-
-        var interceptResult = await networkModule.AddInterceptAsync([InterceptPhase.ResponseStarted], addInterceptOptions, cancellationToken).ConfigureAwait(false);
-
-        Interception interception = new(networkModule, interceptResult.Intercept);
-
-        await interception.OnResponseStartedAsync(
-            async res => await handler(new(res.BiDi, res.Context, res.IsBlocked, res.Navigation, res.RedirectCount, res.Request, res.Timestamp, res.Response, res.Intercepts)),
-            new() { Contexts = [context] }).ConfigureAwait(false);
-
-        return interception;
-    }
-
-    public async Task<Interception> InterceptAuthAsync(Func<InterceptedAuth, Task> handler, InterceptAuthOptions? options = null, CancellationToken cancellationToken = default)
-    {
-        AddInterceptOptions addInterceptOptions = new(options)
-        {
-            Contexts = [context]
-        };
-
-        var interceptResult = await networkModule.AddInterceptAsync([InterceptPhase.AuthRequired], addInterceptOptions, cancellationToken).ConfigureAwait(false);
-
-        Interception interception = new(networkModule, interceptResult.Intercept);
-
-        await interception.OnAuthRequiredAsync(
-            async auth => await handler(new(auth.BiDi, auth.Context, auth.IsBlocked, auth.Navigation, auth.RedirectCount, auth.Request, auth.Timestamp, auth.Response, auth.Intercepts)),
-            new() { Contexts = [context] }).ConfigureAwait(false);
-
-        return interception;
-    }
-
     public Task<AddDataCollectorResult> AddDataCollectorAsync(IEnumerable<DataType> dataTypes, int maxEncodedDataSize, ContextAddDataCollectorOptions? options = null, CancellationToken cancellationToken = default)
     {
         return networkModule.AddDataCollectorAsync(dataTypes, maxEncodedDataSize, ContextAddDataCollectorOptions.WithContext(options, context), cancellationToken);
@@ -267,9 +213,3 @@ private void HandleAuthRequired(AuthRequiredEventArgs e, Action<AuthRequiredEven
         }
     }
 }
-
-public sealed record InterceptRequestOptions : ContextAddInterceptOptions;
-
-public sealed record InterceptResponseOptions : ContextAddInterceptOptions;
-
-public sealed record InterceptAuthOptions : ContextAddInterceptOptions;
diff --git a/dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs b/dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs
index 11be308511e66..b5e2e676d97e7 100644
--- a/dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs
+++ b/dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs
@@ -24,9 +24,6 @@ namespace OpenQA.Selenium.BiDi.BrowsingContext;
 public interface IBrowsingContextNetworkModule
 {
     Task<AddDataCollectorResult> AddDataCollectorAsync(IEnumerable<DataType> dataTypes, int maxEncodedDataSize, ContextAddDataCollectorOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptAuthAsync(Func<InterceptedAuth, Task> handler, InterceptAuthOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptRequestAsync(Func<InterceptedRequest, Task> handler, InterceptRequestOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptResponseAsync(Func<InterceptedResponse, Task> handler, InterceptResponseOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnAuthRequiredAsync(Func<AuthRequiredEventArgs, Task> handler, ContextSubscriptionOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnAuthRequiredAsync(Action<AuthRequiredEventArgs> handler, ContextSubscriptionOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnBeforeRequestSentAsync(Func<BeforeRequestSentEventArgs, Task> handler, ContextSubscriptionOptions? options = null, CancellationToken cancellationToken = default);
diff --git a/dotnet/src/webdriver/BiDi/Network/INetworkModule.cs b/dotnet/src/webdriver/BiDi/Network/INetworkModule.cs
index cddfadeed3101..ec8b45fb947ee 100644
--- a/dotnet/src/webdriver/BiDi/Network/INetworkModule.cs
+++ b/dotnet/src/webdriver/BiDi/Network/INetworkModule.cs
@@ -30,9 +30,6 @@ public interface INetworkModule
     Task<ContinueWithAuthResult> ContinueWithAuthAsync(Request request, ContinueWithAuthCancelCredentialsOptions? options = null, CancellationToken cancellationToken = default);
     Task<FailRequestResult> FailRequestAsync(Request request, FailRequestOptions? options = null, CancellationToken cancellationToken = default);
     Task<BytesValue> GetDataAsync(DataType dataType, Request request, GetDataOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptAuthAsync(Func<InterceptedAuth, Task> handler, InterceptAuthOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptRequestAsync(Func<InterceptedRequest, Task> handler, InterceptRequestOptions? options = null, CancellationToken cancellationToken = default);
-    Task<Interception> InterceptResponseAsync(Func<InterceptedResponse, Task> handler, InterceptResponseOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnAuthRequiredAsync(Func<AuthRequiredEventArgs, Task> handler, SubscriptionOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnAuthRequiredAsync(Action<AuthRequiredEventArgs> handler, SubscriptionOptions? options = null, CancellationToken cancellationToken = default);
     Task<Subscription> OnBeforeRequestSentAsync(Func<BeforeRequestSentEventArgs, Task> handler, SubscriptionOptions? options = null, CancellationToken cancellationToken = default);
PATCH

# Delete the NetworkModule.HighLevel.cs file
rm -f dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs

echo "Patch applied successfully"
