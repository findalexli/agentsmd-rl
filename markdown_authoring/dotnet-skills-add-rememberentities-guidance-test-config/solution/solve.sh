#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "When using `WithShardRegion<T>`, the generic parameter `T` serves as a marker ty" "skills/akka/hosting-actor-patterns/SKILL.md" && grep -qF "When your production code uses custom `AkkaConfigurationBuilder` extension metho" "skills/akka/testing-patterns/SKILL.md" && grep -qF "Design your AppHost to support different configurations for interactive developm" "skills/aspire/integration-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/akka/hosting-actor-patterns/SKILL.md b/skills/akka/hosting-actor-patterns/SKILL.md
@@ -508,6 +508,98 @@ For more on DI lifetimes and scope management, see `microsoft-extensions/depende
 
 ---
 
+## Cluster Sharding Configuration
+
+### RememberEntities: Almost Always False
+
+`RememberEntities` controls whether the shard region remembers and automatically restarts all entities that were ever created. **This should almost always be `false`.**
+
+```csharp
+builder.WithShardRegion<OrderActor>(
+    "orders",
+    (system, registry, resolver) => entityId => resolver.Props<OrderActor>(entityId),
+    new OrderMessageExtractor(),
+    new ShardOptions
+    {
+        StateStoreMode = StateStoreMode.DData,
+        RememberEntities = false,  // DEFAULT - almost always correct
+        Role = clusterRole
+    });
+```
+
+**When `RememberEntities = true` causes problems:**
+
+| Problem | Explanation |
+|---------|-------------|
+| **Unbounded memory growth** | Every entity ever created gets remembered and restarted forever |
+| **Slow cluster startup** | Cluster must restart thousands/millions of entities on boot |
+| **Stale entity resurrection** | Expired sessions, sent emails, old orders all get restarted |
+| **No passivation** | Idle entities consume memory indefinitely (passivation is disabled) |
+
+### When to Use Each Setting
+
+| Entity Type | RememberEntities | Reason |
+|-------------|------------------|--------|
+| `UserSessionActor` | **false** | Sessions expire, created on login |
+| `DraftActor` | **false** | Drafts are sent/discarded, ephemeral |
+| `EmailSenderActor` | **false** | Fire-and-forget operations |
+| `OrderActor` | **false** | Orders complete, new ones created constantly |
+| `ShoppingCartActor` | **false** | Carts expire, abandoned carts common |
+| `TenantActor` | *maybe true* | Fixed set of tenants, always needed |
+| `AccountActor` | *maybe true* | Bounded set of accounts, long-lived |
+
+**Rule of thumb:** Use `RememberEntities = true` only for:
+1. **Bounded** entity sets (known upper limit)
+2. **Long-lived** domain entities that should always be available
+3. Entities where the **cost of remembering < cost of lazy creation**
+
+### Marker Types with WithShardRegion<T>
+
+When using `WithShardRegion<T>`, the generic parameter `T` serves as a marker type for the `ActorRegistry`. Use a dedicated marker type (not the actor class itself) for consistent registry access:
+
+```csharp
+/// <summary>
+/// Marker type for ActorRegistry. Use this to retrieve the OrderActor shard region.
+/// </summary>
+public sealed class OrderActorRegion;
+
+// Registration - use marker type as generic parameter
+builder.WithShardRegion<OrderActorRegion>(
+    "orders",
+    (system, registry, resolver) => entityId => resolver.Props<OrderActor>(entityId),
+    new OrderMessageExtractor(),
+    new ShardOptions { StateStoreMode = StateStoreMode.DData });
+
+// Retrieval - same marker type
+var orderRegion = ActorRegistry.Get<OrderActorRegion>();
+orderRegion.Tell(new CreateOrder(orderId, amount));
+```
+
+**Why marker types?**
+- `WithShardRegion<T>` auto-registers the shard region under type `T`
+- Using the actor class directly can cause confusion (registry returns region, not actor)
+- Marker types make the intent explicit and work consistently in both LocalTest and Clustered modes
+
+### Avoiding Redundant Registry Calls
+
+`WithShardRegion<T>` automatically registers the shard region in the `ActorRegistry`. Don't call `registry.Register<T>()` again:
+
+```csharp
+// BAD - redundant registration
+builder.WithShardRegion<OrderActorRegion>("orders", ...)
+    .WithActors((system, registry, resolver) =>
+    {
+        var region = registry.Get<OrderActorRegion>();
+        registry.Register<OrderActorRegion>(region);  // UNNECESSARY!
+    });
+
+// GOOD - WithShardRegion already registers
+builder.WithShardRegion<OrderActorRegion>("orders", ...);
+// That's it - OrderActorRegion is now in the registry
+```
+
+---
+
 ## Best Practices
 
 1. **Always support both execution modes** - Makes testing easy without code changes
@@ -518,3 +610,4 @@ For more on DI lifetimes and scope management, see `microsoft-extensions/depende
 6. **Composition over inheritance** - Chain extension methods, don't create deep hierarchies
 7. **ITimeProvider for scheduling** - Never use `DateTime.Now` directly in actors
 8. **akka-reminders for durability** - Use for scheduled tasks that must survive restarts
+9. **RememberEntities = false by default** - Only set to true for bounded, long-lived entities
diff --git a/skills/akka/testing-patterns/SKILL.md b/skills/akka/testing-patterns/SKILL.md
@@ -519,7 +519,119 @@ public class OrderPersistentActorTests : TestKit
 
 ---
 
-## Pattern 5: Testing Cluster Sharding Locally
+## Pattern 5: Reuse Production Configuration Extension Methods
+
+When your production code uses custom `AkkaConfigurationBuilder` extension methods (for serializers, actors, persistence), your tests should use those same extension methods rather than duplicating HOCON configuration.
+
+### Anti-Pattern: Duplicated Configuration
+
+```csharp
+// BAD: Duplicating HOCON config that already exists in an extension method
+public class DraftSerializerTests : Akka.TestKit.Xunit2.TestKit
+{
+    public DraftSerializerTests() : base(ConfigurationFactory.ParseString(@"
+        akka.actor {
+            serializers {
+                proto = ""MyApp.Serialization.DraftSerializer, MyApp""
+            }
+            serialization-bindings {
+                ""MyApp.Messages.IDraftEvent, MyApp"" = proto
+                ""MyApp.Actors.DraftState, MyApp"" = proto
+            }
+        }
+    "))
+    { }
+}
+```
+
+**Problems with duplicated config:**
+- Two places to update when bindings change
+- Tests can pass while production fails (or vice versa)
+- Easy to forget to add new bindings to tests
+- Doesn't actually test the extension method itself
+
+### Correct Pattern: Reuse Extension Methods
+
+```csharp
+// Production extension method (in your main project)
+public static class AkkaSerializerExtensions
+{
+    public static AkkaConfigurationBuilder AddDraftSerializer(
+        this AkkaConfigurationBuilder builder)
+    {
+        return builder.WithCustomSerializer(
+            serializerIdentifier: "draft-proto",
+            boundTypes: [typeof(IDraftEvent), typeof(DraftState)],
+            serializerFactory: system => new DraftSerializer(system));
+    }
+}
+
+// GOOD: Test reuses the same extension method
+public class DraftSerializerTests : Akka.Hosting.TestKit.TestKit
+{
+    public DraftSerializerTests(ITestOutputHelper output) : base(output: output) { }
+
+    protected override void ConfigureAkka(AkkaConfigurationBuilder builder, IServiceProvider provider)
+    {
+        // Use the SAME extension method as production
+        builder.AddDraftSerializer();
+
+        // Add test-specific config (in-memory persistence, etc.)
+        builder.WithInMemoryJournal()
+            .WithInMemorySnapshotStore();
+    }
+
+    [Fact]
+    public async Task DraftSerializer_RoundTrips_DraftCreatedEvent()
+    {
+        // Arrange
+        var original = new DraftCreated(DraftId.New(), "Test Draft", DateTime.UtcNow);
+
+        // Act - serialize and deserialize through the actor system
+        var serializer = Sys.Serialization.FindSerializerFor(original);
+        var bytes = serializer.ToBinary(original);
+        var deserialized = serializer.FromBinary(bytes, typeof(DraftCreated));
+
+        // Assert
+        deserialized.Should().BeEquivalentTo(original);
+    }
+}
+```
+
+### Benefits
+
+| Benefit | Explanation |
+|---------|-------------|
+| **DRY** | Single source of truth for configuration |
+| **No Drift** | Tests always use the exact same config as production |
+| **Easier Maintenance** | Add a new binding in one place, tests automatically pick it up |
+| **Better Coverage** | Actually tests the extension method itself |
+| **Catches Real Bugs** | If the extension method is broken, tests fail |
+
+### Applying to Other Configurations
+
+This pattern applies to any `AkkaConfigurationBuilder` extension method:
+
+```csharp
+protected override void ConfigureAkka(AkkaConfigurationBuilder builder, IServiceProvider provider)
+{
+    // Reuse production extension methods
+    builder
+        .AddDraftSerializer()           // Custom serializer
+        .AddOrderDomainActors(AkkaExecutionMode.LocalTest)  // Domain actors
+        .AddCustomPersistence()         // Persistence config
+        .AddReminders();                // Reminder system
+
+    // Override only what's test-specific
+    builder
+        .WithInMemoryJournal()          // Replace real DB with in-memory
+        .WithInMemorySnapshotStore();
+}
+```
+
+---
+
+## Pattern 6: Testing Cluster Sharding Locally
 
 Use `AkkaExecutionMode.LocalTest` to test cluster sharding behavior without an actual cluster.
 
diff --git a/skills/aspire/integration-testing/SKILL.md b/skills/aspire/integration-testing/SKILL.md
@@ -324,60 +324,161 @@ public class UIIntegrationTests
 }
 ```
 
-## Pattern 6: Conditional Volume Configuration in AppHost
+## Pattern 6: Conditional Resource Configuration for Tests
 
-Design your AppHost to support test scenarios by making volumes optional:
+Design your AppHost to support different configurations for interactive development (F5/CLI) vs automated test fixtures. The pattern goes beyond just volumes - it covers execution modes, authentication, external services, and more.
+
+### Core Principle
+
+> **Default to production-like behavior in AppHost.** Tests explicitly override what they need to be different. This catches configuration gaps early (e.g., missing DI registrations that only surface in clustered mode).
+
+### Configuration Class in AppHost
 
 ```csharp
-// In your AppHost Program.cs
-public class AppConfiguration
+// In your AppHost project
+public class AppHostConfiguration
 {
-    /// <summary>
-    /// Whether to use persistent volumes for databases.
-    /// Defaults to false - tests get a clean database each run.
-    /// </summary>
-    public bool UseVolumes { get; set; } = false;
+    // Infrastructure settings
+    public bool UseVolumes { get; set; } = true;  // Persist data in dev, clean slate in tests
+
+    // Execution mode settings (for Akka.NET or similar)
+    public string ExecutionMode { get; set; } = "Clustered";  // Full cluster in dev, LocalTest optional
 
-    public string Environment { get; set; } = "Development";
+    // Feature toggles
+    public bool EnableTestAuth { get; set; } = false;  // /dev-login endpoint for tests
+    public bool UseFakeExternalServices { get; set; } = false;  // Fake Gmail, Stripe, etc.
+
+    // Scale settings
     public int Replicas { get; set; } = 1;
 }
+```
+
+### AppHost Conditional Logic
 
+```csharp
 var builder = DistributedApplication.CreateBuilder(args);
 
 // Bind configuration from command-line args or appsettings
-var config = builder.Configuration.GetSection("YourApp")
-    .Get<AppConfiguration>() ?? new AppConfiguration();
+var config = builder.Configuration.GetSection("App")
+    .Get<AppHostConfiguration>() ?? new AppHostConfiguration();
 
+// Database with conditional volume
 var postgres = builder.AddPostgres("postgres").WithPgAdmin();
-
-// Only persist data when explicitly enabled (not during tests)
 if (config.UseVolumes)
 {
     postgres.WithDataVolume();
 }
-
 var db = postgres.AddDatabase("appdb");
 
-// Migrations run first
+// Migrations
 var migrations = builder.AddProject<Projects.YourApp_Migrations>("migrations")
     .WaitFor(db)
     .WithReference(db);
 
-// API waits for migrations to complete
+// API with environment-based configuration
 var api = builder.AddProject<Projects.YourApp_Api>("api")
     .WaitForCompletion(migrations)
-    .WithReference(db);
+    .WithReference(db)
+    .WithEnvironment("AkkaSettings__ExecutionMode", config.ExecutionMode)
+    .WithEnvironment("Testing__EnableTestAuth", config.EnableTestAuth.ToString())
+    .WithEnvironment("ExternalServices__UseFakes", config.UseFakeExternalServices.ToString());
+
+// Conditional replicas
+if (config.Replicas > 1)
+{
+    api.WithReplicas(config.Replicas);
+}
+
+builder.Build().Run();
 ```
 
-**Then in tests, pass `UseVolumes=false`:**
+### Test Fixture Overrides
 
 ```csharp
 var builder = await DistributedApplicationTestingBuilder
     .CreateAsync<Projects.YourApp_AppHost>([
-        "YourApp:UseVolumes=false"  // Clean database each test run
+        "App:UseVolumes=false",           // Clean database each test
+        "App:ExecutionMode=LocalTest",    // Faster, no cluster overhead (optional)
+        "App:EnableTestAuth=true",        // Enable /dev-login endpoint
+        "App:UseFakeExternalServices=true" // No real OAuth, email, payments
     ]);
 ```
 
+### Common Conditional Settings
+
+| Setting | F5/Development | Test Fixture | Purpose |
+|---------|----------------|--------------|---------|
+| `UseVolumes` | `true` (persist data) | `false` (clean slate) | Database isolation |
+| `ExecutionMode` | `Clustered` (realistic) | `LocalTest` or `Clustered` | Actor system mode |
+| `EnableTestAuth` | `false` (use real OAuth) | `true` (/dev-login) | Bypass OAuth in tests |
+| `UseFakeServices` | `false` (real integrations) | `true` (no external calls) | External API isolation |
+| `Replicas` | `1` or more | `1` (simplicity) | Scale configuration |
+| `SeedData` | `false` | `true` | Pre-populate test data |
+
+### Test Authentication Pattern
+
+When `EnableTestAuth=true`, your API can expose a test-only authentication endpoint:
+
+```csharp
+// In API startup, conditionally add test auth
+if (builder.Configuration.GetValue<bool>("Testing:EnableTestAuth"))
+{
+    app.MapPost("/dev-login", async (DevLoginRequest request, IAuthService auth) =>
+    {
+        // Generate a real auth token for the specified user
+        var token = await auth.GenerateTokenAsync(request.UserId, request.Roles);
+        return Results.Ok(new { token });
+    });
+}
+
+// In tests
+public async Task<string> LoginAsTestUser(string userId, string[] roles)
+{
+    var response = await _httpClient.PostAsJsonAsync("/dev-login",
+        new { UserId = userId, Roles = roles });
+    var result = await response.Content.ReadFromJsonAsync<DevLoginResponse>();
+    return result!.Token;
+}
+```
+
+### Fake External Services Pattern
+
+```csharp
+// In your service registration
+public static IServiceCollection AddExternalServices(
+    this IServiceCollection services,
+    IConfiguration config)
+{
+    if (config.GetValue<bool>("ExternalServices:UseFakes"))
+    {
+        // Test fakes - no external calls
+        services.AddSingleton<IEmailSender, FakeEmailSender>();
+        services.AddSingleton<IPaymentProcessor, FakePaymentProcessor>();
+        services.AddSingleton<IOAuthProvider, FakeOAuthProvider>();
+    }
+    else
+    {
+        // Real implementations
+        services.AddSingleton<IEmailSender, SendGridEmailSender>();
+        services.AddSingleton<IPaymentProcessor, StripePaymentProcessor>();
+        services.AddSingleton<IOAuthProvider, Auth0Provider>();
+    }
+
+    return services;
+}
+```
+
+### Why Default to Production-Like Behavior
+
+Starting with production-like defaults and overriding in tests catches issues that only appear under real conditions:
+
+- **DI registration gaps** - Services that are only registered in clustered mode
+- **Configuration errors** - Settings that are required in production but missing
+- **Integration issues** - Problems with real database connections, auth flows, etc.
+- **Performance characteristics** - Tests run closer to production behavior
+
+Tests explicitly opt-out of specific production behaviors rather than opting-in to a test mode that might miss real issues.
+
 ## Pattern 7: Database Reset with Respawn
 
 For tests that modify data, use [Respawn](https://github.com/jbogard/Respawn) to reset between tests:
PATCH

echo "Gold patch applied."
