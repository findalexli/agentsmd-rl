#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-instructions

# Idempotency guard
if grep -qF "description: Use when building Model Context Protocol (MCP) servers in .NET, con" ".github/skills/creating-dotnet-mcp-servers/SKILL.md" && grep -qF "public PackageTools(IQueryHandler<SearchPackagesQuery, IEnumerable<PackageMetada" ".github/skills/creating-dotnet-mcp-servers/references/advanced.md" && grep -qF "**Never throw unhandled exceptions** - MCP tools should return structured error " ".github/skills/creating-dotnet-mcp-servers/references/error-handling.md" && grep -qF "| No `WebApplicationFactory` in integration tests | Can't test real transport \u2192 " ".github/skills/creating-dotnet-mcp-servers/references/testing.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/creating-dotnet-mcp-servers/SKILL.md b/.github/skills/creating-dotnet-mcp-servers/SKILL.md
@@ -0,0 +1,144 @@
+---
+name: creating-dotnet-mcp-servers
+description: Use when building Model Context Protocol (MCP) servers in .NET, configuring tools, transports (SSE/stdio), JSON serialization for AOT, or testing MCP endpoints
+---
+
+# Creating .NET MCP Servers
+
+Build production-ready Model Context Protocol (MCP) servers in .NET with AOT compatibility.
+
+**Core principle:** MCP servers expose tools via standardized protocol using attribute-based registration and explicit JSON serialization contexts for AOT.
+
+## When to Use
+
+```mermaid
+graph TD
+    A[Need to build server?] -->|Yes| B[Using .NET?]
+    B -->|Yes| C[MCP Protocol?]
+    C -->|Yes| D[✅ Use this skill]
+    C -->|No| E[❌ Use REST/gRPC guide]
+    B -->|No| F[❌ See Python/TS MCP docs]
+    A -->|No| G[❌ Skip]
+```
+
+Use this skill when:
+- Building new MCP server in .NET
+- Configuring SSE or stdio transport
+- Enabling AOT compilation
+- Need testing or error handling patterns
+
+**Not for:** Non-.NET MCP, client-side integration, generic APIs
+
+## Quick Reference
+
+| Task | Implementation |
+|------|----------------|
+| Install packages | `dotnet add package ModelContextProtocol` + `ModelContextProtocol.AspNetCore` |
+| Mark tool class | `[McpServerToolType]` |
+| Mark tool method | `[McpServerTool(Name = "ToolName"), Description("...")]` |
+| Parameter description | `[Description("param description")] string param` |
+| Register server | `services.AddMcpServer().WithHttpTransport().WithTools<T>()` |
+| Map endpoints | `app.MapMcp()` (exposes `/sse`) |
+| AOT serialization | Create `JsonSerializerContext` with `[JsonSerializable]` |
+| Test transport | Use `SseClientTransport` + `McpClientFactory` |
+
+## Basic Setup
+
+### 1. Install Packages
+
+```bash
+dotnet add package ModelContextProtocol --version 0.3.0-preview.1
+dotnet add package ModelContextProtocol.AspNetCore --version 0.3.0-preview.1
+# For testing (optional)
+dotnet add package ModelContextProtocol.Client --version 0.3.0-preview.1
+```
+
+### 2. Enable AOT
+
+**Project configuration:**
+```xml
+<PropertyGroup>
+  <PublishAot>true</PublishAot>
+  <JsonSerializerIsReflectionEnabledByDefault>false</JsonSerializerIsReflectionEnabledByDefault>
+</PropertyGroup>
+```
+
+**JSON serialization context:**
+```csharp
+[JsonSerializable(typeof(PackageMetadata))]
+[JsonSerializable(typeof(IEnumerable<PackageMetadata>))]
+public partial class McpJsonContext : JsonSerializerContext { }
+```
+
+**Register in Program.cs:**
+```csharp
+builder.Services.AddMcpServer()
+    .WithTools<PackageTools>(serializerOptions: McpJsonContext.Default.Options);
+```
+
+**Critical:** Add ALL tool return types to `[JsonSerializable]` attributes.
+
+## Tool Implementation
+
+Minimal example:
+
+```csharp
+[McpServerToolType]
+public sealed class PackageTools
+{
+    public const string SearchPackages = "SearchPackages";
+    
+    [McpServerTool(Name = SearchPackages)]
+    [Description("Search for NuGet packages by name or keyword")]
+    public async Task<IEnumerable<PackageMetadata>> SearchAsync(
+        [Description("The package name or search keyword")] string query,
+        [Description("Maximum number of results (default: 10)")] int limit = 10,
+        CancellationToken cancellationToken = default)
+    {
+        // Implementation
+    }
+}
+```
+
+**Key patterns:** Sealed classes, const tool names, `[Description]` on method and parameters, always accept `CancellationToken`.
+
+## Transport Configuration
+
+**SSE (HTTP):**
+```csharp
+builder.Logging.AddConsole(options => options.LogToStandardErrorThreshold = LogLevel.Trace);
+builder.Services.AddMcpServer().WithHttpTransport().WithTools<PackageTools>(...);
+app.MapMcp();  // Exposes /sse
+```
+
+**Stdio (CLI):**
+```csharp
+builder.Services.AddMcpServer().WithStdioTransport().WithTools<PackageTools>(...);
+// No MapMcp() needed
+```
+
+## Testing and Error Handling
+
+**📖 See references:**
+- [Testing MCP servers](references/testing.md) - Integration tests, fixtures, Testcontainers
+- [Error handling patterns](references/error-handling.md) - Structured errors, error codes, logging
+
+## Common Mistakes
+
+| Mistake | Fix |
+|---------|-----|
+| Forgot `[JsonSerializable]` for return type | Add all tool return types to `JsonSerializerContext` |
+| Not logging to stderr | Set `LogToStandardErrorThreshold = LogLevel.Trace` |
+| Missing `CancellationToken` | Always add `CancellationToken` parameter |
+| Throwing exceptions in tools | Return `ToolResult<T>` with structured errors |
+| Magic strings for tool names | Use `const string` in tool class |
+| No `[Description]` on parameters | Add `[Description]` to all parameters |
+| Forgetting `MapMcp()` | Required for HTTP/SSE transport |
+
+## References
+
+- **📖 [Testing](references/testing.md)** - WebApplicationFactory, fixtures, Testcontainers
+- **📖 [Error Handling](references/error-handling.md)** - Structured errors, error codes
+- **📖 [Advanced Topics](references/advanced.md)** - Clean Architecture, deployment, monitoring
+- [MCP Specification](https://modelcontextprotocol.io/docs)
+- [ModelContextProtocol NuGet](https://www.nuget.org/packages/ModelContextProtocol)
diff --git a/.github/skills/creating-dotnet-mcp-servers/references/advanced.md b/.github/skills/creating-dotnet-mcp-servers/references/advanced.md
@@ -0,0 +1,586 @@
+# Advanced Topics
+
+Clean Architecture integration, configuration patterns, and production deployment for MCP servers.
+
+## Clean Architecture Integration
+
+Project structure example with Clean Architecture layering:
+
+```
+src/
+  YourProject.Domain/         # Entities, value objects, interfaces
+    PackageAggregate/
+      IPackageService.cs      # Domain interface
+      PackageMetadata.cs      # Domain model
+      PackageVersion.cs       # Value object
+      
+  YourProject.Application/    # Use cases
+    SearchPackages/
+      SearchPackagesUseCase.cs # Application logic
+      
+  YourProject.Infrastructure/ # External service implementations
+    NuGet/
+      NuGetService.cs         # Implements IPackageService
+      NuGetServiceOptions.cs  # Configuration
+      
+  YourProject.Api/           # MCP server
+    PackageTools.cs          # MCP tool class
+    Program.cs               # Server setup
+    McpJsonContext.cs        # AOT serialization
+```
+
+### Tool Class Integration Patterns
+
+Example with direct Use Case injection:
+
+```csharp
+[McpServerToolType]
+public sealed class PackageTools
+{
+    private readonly SearchPackagesUseCase _searchUseCase;
+    private readonly GetPackageInfoUseCase _getInfoUseCase;
+    
+    public PackageTools(
+        SearchPackagesUseCase searchUseCase,
+        GetPackageInfoUseCase getInfoUseCase)
+    {
+        _searchUseCase = searchUseCase;
+        _getInfoUseCase = getInfoUseCase;
+    }
+    
+    [McpServerTool(Name = "SearchPackages")]
+    [Description("Search for packages by name or keyword")]
+    public async Task<IEnumerable<PackageMetadata>> SearchAsync(
+        [Description("Search query")] string query,
+        [Description("Maximum results")] int limit = 10)
+    {
+        return await _searchUseCase.ExecuteAsync(query, limit);
+    }
+    
+    [McpServerTool(Name = "GetPackageInfo")]
+    [Description("Get detailed information about a specific package")]
+    public async Task<PackageMetadata> GetInfoAsync(
+        [Description("Package ID")] string packageId)
+    {
+        return await _getInfoUseCase.ExecuteAsync(packageId);
+    }
+}
+```
+
+#### Available Injection Patterns
+
+**Direct injection:**
+```csharp
+// Simple, explicit, AOT-friendly
+public PackageTools(SearchPackagesUseCase searchUseCase) { }
+```
+
+**Pros:**
+- Explicit dependencies (easy to understand)
+- AOT compatible (no reflection)
+- Simpler DI registration
+- Better IDE support
+- Each tool method maps 1:1 to use case
+
+**Cons:**
+- Tools with many use cases get many constructor params
+- Less flexible (can't swap implementations easily)
+
+**CQRS pattern (alternative for tools with many operations):**
+```csharp
+// Alternative: Basic CQRS when tools have 10+ operations
+public PackageTools(IQueryHandler<SearchPackagesQuery, IEnumerable<PackageMetadata>> searchHandler) { }
+public Task<IEnumerable<PackageMetadata>> SearchAsync(string query)
+    => searchHandler.HandleAsync(new SearchPackagesQuery(query));
+```
+
+**Pros:**
+- Single dependency per query/command type
+- Clear separation of concerns (queries vs commands)
+- Easier to add cross-cutting concerns
+
+**Cons:**
+- More boilerplate (query/command classes, handlers)
+- Less obvious what dependencies tool has
+
+### Dependency Injection Setup
+
+```csharp
+// Infrastructure layer extension
+public static class ServiceCollectionExtensions
+{
+    public static IServiceCollection AddInfrastructure(
+        this IServiceCollection services, 
+        IConfiguration configuration)
+    {
+        // Register domain services
+        services.AddTransient<IPackageService, NuGetService>();
+        
+        // Configure options
+        services.Configure<NuGetServiceOptions>(
+            configuration.GetSection("NuGetService"));
+        
+        // Add post-configuration validation
+        services.AddSingleton<IPostConfigureOptions<NuGetServiceOptions>, 
+            PostConfigureNuGetServiceOptions>();
+        
+        // Add HTTP clients
+        services.AddHttpClient<IPackageService, NuGetService>();
+        
+        return services;
+    }
+}
+
+// Application layer extension
+public static class ServiceCollectionExtensions
+{
+    public static IServiceCollection AddApplication(
+        this IServiceCollection services)
+    {
+        // Register use cases
+        services.AddTransient<SearchPackagesUseCase>();
+        services.AddTransient<GetPackageInfoUseCase>();
+        
+        return services;
+    }
+}
+
+// Program.cs
+builder.Services.AddInfrastructure(builder.Configuration);
+builder.Services.AddApplication();
+
+builder.Services
+    .AddMcpServer()
+    .WithHttpTransport()
+    .WithTools<PackageTools>(serializerOptions: McpJsonContext.Default.Options);
+```
+
+## Configuration Patterns
+
+### Environment-Specific Configuration
+
+**appsettings.json:**
+```json
+{
+  "Logging": {
+    "LogLevel": {
+      "Default": "Information",
+      "Microsoft.AspNetCore": "Warning"
+    },
+    "Console": {
+      "LogToStandardErrorThreshold": "Trace"
+    }
+  },
+  "NuGetService": {
+    "FeedUrl": "https://api.nuget.org/v3/index.json",
+    "Timeout": "00:00:30",
+    "MaxRetries": 3
+  }
+}
+```
+
+**appsettings.Development.json:**
+```json
+{
+  "Logging": {
+    "LogLevel": {
+      "Default": "Debug"
+    }
+  },
+  "NuGetService": {
+    "FeedUrl": "http://localhost:5555/v3/index.json"
+  }
+}
+```
+
+### Options Pattern with Validation
+
+```csharp
+public sealed class NuGetServiceOptions
+{
+    public const string SectionName = "NuGetService";
+    
+    public string FeedUrl { get; set; } = string.Empty;
+    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
+    public int MaxRetries { get; set; } = 3;
+}
+
+// Post-configure validation
+public sealed class PostConfigureNuGetServiceOptions 
+    : IPostConfigureOptions<NuGetServiceOptions>
+{
+    public void PostConfigure(string? name, NuGetServiceOptions options)
+    {
+        if (string.IsNullOrWhiteSpace(options.FeedUrl))
+        {
+            throw new InvalidOperationException(
+                "NuGetService:FeedUrl is required");
+        }
+        
+        if (!Uri.TryCreate(options.FeedUrl, UriKind.Absolute, out _))
+        {
+            throw new InvalidOperationException(
+                "NuGetService:FeedUrl must be a valid URL");
+        }
+        
+        if (options.Timeout <= TimeSpan.Zero)
+        {
+            throw new InvalidOperationException(
+                "NuGetService:Timeout must be positive");
+        }
+    }
+}
+```
+
+### Multiple Tool Classes
+
+```csharp
+builder.Services
+    .AddMcpServer()
+    .WithHttpTransport()
+    .WithTools<PackageTools>(serializerOptions: McpJsonContext.Default.Options)
+    .WithTools<DocumentationTools>(serializerOptions: McpJsonContext.Default.Options)
+    .WithTools<AnalyticsTools>(serializerOptions: McpJsonContext.Default.Options);
+```
+
+## Production Deployment
+
+### Dockerfile for AOT
+
+```dockerfile
+FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
+WORKDIR /src
+
+# Copy solution and project files
+COPY *.sln .
+COPY src/**/*.csproj ./
+RUN for file in $(ls *.csproj); do mkdir -p src/${file%.*}/ && mv $file src/${file%.*}/; done
+
+# Restore dependencies
+RUN dotnet restore
+
+# Copy source code
+COPY . .
+
+# Publish with AOT
+WORKDIR /src/src/YourProject.Api
+RUN dotnet publish -c Release -o /app --self-contained true
+
+# Runtime image - use runtime-deps for AOT
+FROM mcr.microsoft.com/dotnet/runtime-deps:9.0-alpine
+WORKDIR /app
+
+# Install required libraries for AOT
+RUN apk add --no-cache \
+    icu-libs \
+    libintl
+
+# Copy published app
+COPY --from=build /app .
+
+# Create non-root user
+RUN adduser -D -u 1000 mcpuser && \
+    chown -R mcpuser:mcpuser /app
+
+USER mcpuser
+
+EXPOSE 8080
+
+ENTRYPOINT ["./YourProject.Api"]
+```
+
+### Docker Compose
+
+```yaml
+version: '3.8'
+
+services:
+  mcp-server:
+    build:
+      context: .
+      dockerfile: Dockerfile
+    ports:
+      - "8080:8080"
+    environment:
+      - ASPNETCORE_ENVIRONMENT=Production
+      - ASPNETCORE_URLS=http://+:8080
+      - NuGetService__FeedUrl=https://api.nuget.org/v3/index.json
+    healthcheck:
+      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
+      interval: 30s
+      timeout: 10s
+      retries: 3
+      start_period: 40s
+    restart: unless-stopped
+    logging:
+      driver: "json-file"
+      options:
+        max-size: "10m"
+        max-file: "3"
+```
+
+### Health Checks
+
+```csharp
+builder.Services.AddHealthChecks()
+    .AddCheck("self", () => HealthCheckResult.Healthy())
+    .AddCheck<NuGetServiceHealthCheck>("nuget-service");
+
+var app = builder.Build();
+
+app.MapHealthChecks("/health");
+app.MapMcp();
+```
+
+```csharp
+public sealed class NuGetServiceHealthCheck : IHealthCheck
+{
+    private readonly IPackageService _packageService;
+    
+    public NuGetServiceHealthCheck(IPackageService packageService)
+    {
+        _packageService = packageService;
+    }
+    
+    public async Task<HealthCheckResult> CheckHealthAsync(
+        HealthCheckContext context,
+        CancellationToken cancellationToken = default)
+    {
+        try
+        {
+            // Simple connectivity check
+            await _packageService.PingAsync(cancellationToken);
+            return HealthCheckResult.Healthy("NuGet service is reachable");
+        }
+        catch (Exception ex)
+        {
+            return HealthCheckResult.Unhealthy(
+                "NuGet service is unreachable",
+                ex);
+        }
+    }
+}
+```
+
+### Performance Metrics
+
+**AOT Compilation Benefits:**
+
+| Metric | Without AOT | With AOT | Improvement |
+|--------|-------------|----------|-------------|
+| Startup Time | ~500ms | ~50ms | 10x faster |
+| Memory Usage | ~100MB | ~30MB | 70% reduction |
+| Binary Size | ~80MB | ~15MB | 80% smaller |
+| JIT Overhead | Present | None | Eliminated |
+
+### Production Configuration
+
+```csharp
+var builder = WebApplication.CreateSlimBuilder(args);
+
+// Production logging
+builder.Logging.ClearProviders();
+builder.Logging.AddConsole(options =>
+{
+    options.LogToStandardErrorThreshold = LogLevel.Information;
+    options.TimestampFormat = "[yyyy-MM-dd HH:mm:ss] ";
+});
+
+// Add structured logging (Serilog)
+builder.Host.UseSerilog((context, configuration) =>
+{
+    configuration
+        .ReadFrom.Configuration(context.Configuration)
+        .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
+        .WriteTo.File("logs/mcp-server-.log", 
+            rollingInterval: RollingInterval.Day,
+            retainedFileCountLimit: 7);
+});
+
+// Add metrics
+builder.Services.AddOpenTelemetry()
+    .WithMetrics(metrics =>
+    {
+        metrics
+            .AddAspNetCoreInstrumentation()
+            .AddPrometheusExporter();
+    });
+
+var app = builder.Build();
+
+// Metrics endpoint
+app.MapPrometheusScrapingEndpoint();
+
+// Health checks
+app.MapHealthChecks("/health");
+
+// MCP endpoints
+app.MapMcp();
+
+await app.RunAsync();
+```
+
+### Kubernetes Deployment
+
+```yaml
+apiVersion: apps/v1
+kind: Deployment
+metadata:
+  name: mcp-server
+spec:
+  replicas: 3
+  selector:
+    matchLabels:
+      app: mcp-server
+  template:
+    metadata:
+      labels:
+        app: mcp-server
+    spec:
+      containers:
+      - name: mcp-server
+        image: your-registry/mcp-server:latest
+        ports:
+        - containerPort: 8080
+        env:
+        - name: ASPNETCORE_ENVIRONMENT
+          value: "Production"
+        - name: NuGetService__FeedUrl
+          valueFrom:
+            configMapKeyRef:
+              name: mcp-config
+              key: nuget-feed-url
+        resources:
+          requests:
+            memory: "64Mi"
+            cpu: "100m"
+          limits:
+            memory: "128Mi"
+            cpu: "500m"
+        livenessProbe:
+          httpGet:
+            path: /health
+            port: 8080
+          initialDelaySeconds: 10
+          periodSeconds: 30
+        readinessProbe:
+          httpGet:
+            path: /health
+            port: 8080
+          initialDelaySeconds: 5
+          periodSeconds: 10
+---
+apiVersion: v1
+kind: Service
+metadata:
+  name: mcp-server
+spec:
+  selector:
+    app: mcp-server
+  ports:
+  - port: 80
+    targetPort: 8080
+  type: LoadBalancer
+```
+
+## Monitoring and Observability
+
+### Application Insights
+
+```csharp
+builder.Services.AddApplicationInsightsTelemetry(options =>
+{
+    options.ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"];
+    options.EnableAdaptiveSampling = true;
+});
+```
+
+### Custom Metrics
+
+```csharp
+public sealed class PackageTools
+{
+    private readonly SearchPackagesUseCase _searchUseCase;
+    private readonly ILogger<PackageTools> _logger;
+    private readonly IMeterFactory _meterFactory;
+    private readonly Counter<long> _searchCounter;
+    
+    public PackageTools(
+        SearchPackagesUseCase searchUseCase,
+        ILogger<PackageTools> logger,
+        IMeterFactory meterFactory)
+    {
+        _searchUseCase = searchUseCase;
+        _logger = logger;
+        _meterFactory = meterFactory;
+        
+        var meter = _meterFactory.Create("McpServer.PackageTools");
+        _searchCounter = meter.CreateCounter<long>("package_searches_total");
+    }
+    
+    [McpServerTool(Name = "SearchPackages")]
+    [Description("Search for packages")]
+    public async Task<IEnumerable<PackageMetadata>> SearchAsync(string query)
+    {
+        _searchCounter.Add(1, new TagList { { "query_length", query.Length } });
+        
+        var sw = Stopwatch.StartNew();
+        try
+        {
+            var results = await _searchUseCase.ExecuteAsync(query);
+            _logger.LogInformation(
+                "Search completed in {ElapsedMs}ms, found {Count} results",
+                sw.ElapsedMilliseconds, results.Count());
+            return results;
+        }
+        catch (Exception ex)
+        {
+            _logger.LogError(ex, "Search failed after {ElapsedMs}ms", sw.ElapsedMilliseconds);
+            throw;
+        }
+    }
+}
+```
+
+## Security Considerations
+
+### Authentication/Authorization
+
+MCP servers typically run in trusted environments. For public-facing deployments:
+
+```csharp
+builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
+    .AddJwtBearer(options =>
+    {
+        options.Authority = builder.Configuration["Auth:Authority"];
+        options.Audience = builder.Configuration["Auth:Audience"];
+    });
+
+builder.Services.AddAuthorization();
+
+var app = builder.Build();
+
+app.UseAuthentication();
+app.UseAuthorization();
+
+// Secure MCP endpoints
+app.MapMcp().RequireAuthorization();
+```
+
+### Rate Limiting
+
+```csharp
+builder.Services.AddRateLimiter(options =>
+{
+    options.AddFixedWindowLimiter("fixed", options =>
+    {
+        options.Window = TimeSpan.FromMinutes(1);
+        options.PermitLimit = 100;
+    });
+});
+
+var app = builder.Build();
+app.UseRateLimiter();
+
+app.MapMcp().RequireRateLimiting("fixed");
+```
diff --git a/.github/skills/creating-dotnet-mcp-servers/references/error-handling.md b/.github/skills/creating-dotnet-mcp-servers/references/error-handling.md
@@ -0,0 +1,442 @@
+# Error Handling in MCP Tools
+
+Best practices for handling errors gracefully in MCP tools and returning meaningful messages to clients.
+
+## Core Principle
+
+**Never throw unhandled exceptions** - MCP tools should return structured error responses instead of letting exceptions bubble up. This provides better UX for LLM clients and makes debugging easier.
+
+## Structured Error Response Pattern
+
+```csharp
+public record ToolResult<T>
+{
+    public bool Success { get; init; }
+    public T? Data { get; init; }
+    public string? Error { get; init; }
+    public string? ErrorCode { get; init; }
+}
+
+[McpServerTool(Name = "SearchPackages")]
+[Description("Search for packages")]
+public async Task<ToolResult<IEnumerable<PackageMetadata>>> SearchAsync(
+    [Description("Search query")] string query,
+    [Description("Maximum results (default: 10)")] int limit = 10,
+    CancellationToken cancellationToken = default)
+{
+    try
+    {
+        // Input validation
+        if (string.IsNullOrWhiteSpace(query))
+        {
+            return new ToolResult<IEnumerable<PackageMetadata>>
+            {
+                Success = false,
+                Data = null,
+                Error = "Search query cannot be empty",
+                ErrorCode = "INVALID_INPUT"
+            };
+        }
+        
+        if (limit < 1 || limit > 100)
+        {
+            return new ToolResult<IEnumerable<PackageMetadata>>
+            {
+                Success = false,
+                Data = null,
+                Error = "Limit must be between 1 and 100",
+                ErrorCode = "INVALID_INPUT"
+            };
+        }
+        
+        // Business logic
+        var results = await _packageService.SearchAsync(query, limit, cancellationToken);
+        
+        return new ToolResult<IEnumerable<PackageMetadata>>
+        {
+            Success = true,
+            Data = results,
+            Error = null,
+            ErrorCode = null
+        };
+    }
+    catch (ArgumentException ex)
+    {
+        return new ToolResult<IEnumerable<PackageMetadata>>
+        {
+            Success = false,
+            Data = null,
+            Error = ex.Message,
+            ErrorCode = "INVALID_ARGUMENT"
+        };
+    }
+    catch (HttpRequestException ex)
+    {
+        _logger.LogError(ex, "Network error during package search for query: {Query}", query);
+        
+        return new ToolResult<IEnumerable<PackageMetadata>>
+        {
+            Success = false,
+            Data = null,
+            Error = $"Network error: {ex.Message}",
+            ErrorCode = "NETWORK_ERROR"
+        };
+    }
+    catch (TimeoutException ex)
+    {
+        _logger.LogError(ex, "Timeout during package search for query: {Query}", query);
+        
+        return new ToolResult<IEnumerable<PackageMetadata>>
+        {
+            Success = false,
+            Data = null,
+            Error = "Request timed out. Please try again.",
+            ErrorCode = "TIMEOUT"
+        };
+    }
+    catch (Exception ex)
+    {
+        // Log unexpected errors with full details
+        _logger.LogError(ex, "Unexpected error during package search for query: {Query}", query);
+        
+        return new ToolResult<IEnumerable<PackageMetadata>>
+        {
+            Success = false,
+            Data = null,
+            Error = "An unexpected error occurred. Please try again.",
+            ErrorCode = "INTERNAL_ERROR"
+        };
+    }
+}
+```
+
+## Error Categories
+
+### 1. Validation Errors (User Input)
+
+**Pattern:** Return immediately without calling services
+
+```csharp
+if (string.IsNullOrWhiteSpace(packageId))
+{
+    return ToolResult.Failure<PackageInfo>(
+        "Package ID is required",
+        "VALIDATION_ERROR");
+}
+
+if (!Regex.IsMatch(packageId, @"^[a-zA-Z0-9\.\-_]+$"))
+{
+    return ToolResult.Failure<PackageInfo>(
+        "Package ID contains invalid characters",
+        "VALIDATION_ERROR");
+}
+```
+
+### 2. Business Logic Errors
+
+**Pattern:** Catch domain exceptions and translate to user-friendly messages
+
+```csharp
+try
+{
+    var package = await _service.GetPackageAsync(packageId);
+    return ToolResult.Success(package);
+}
+catch (PackageNotFoundException ex)
+{
+    return ToolResult.Failure<PackageInfo>(
+        $"Package '{packageId}' not found",
+        "NOT_FOUND");
+}
+catch (PackageDeprecatedException ex)
+{
+    return ToolResult.Failure<PackageInfo>(
+        $"Package '{packageId}' has been deprecated. Reason: {ex.Reason}",
+        "DEPRECATED");
+}
+```
+
+### 3. Infrastructure Errors
+
+**Pattern:** Log detailed error, return generic message
+
+```csharp
+catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.Unauthorized)
+{
+    _logger.LogError(ex, "Authentication failed for package service");
+    return ToolResult.Failure<PackageInfo>(
+        "Unable to authenticate with package service. Please check configuration.",
+        "AUTH_ERROR");
+}
+catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
+{
+    _logger.LogWarning("Rate limit exceeded for package service");
+    return ToolResult.Failure<PackageInfo>(
+        "Rate limit exceeded. Please try again in a few minutes.",
+        "RATE_LIMIT");
+}
+```
+
+### 4. Unexpected Errors
+
+**Pattern:** Always log, never expose internal details to client
+
+```csharp
+catch (Exception ex)
+{
+    _logger.LogError(ex, "Unexpected error in SearchAsync for query: {Query}", query);
+    
+    // Don't expose internal exception details to client
+    return ToolResult.Failure<IEnumerable<PackageMetadata>>(
+        "An internal error occurred. The issue has been logged.",
+        "INTERNAL_ERROR");
+}
+```
+
+## Cancellation Handling
+
+Always support cancellation tokens:
+
+```csharp
+[McpServerTool(Name = "AnalyzePackage")]
+[Description("Performs deep analysis of a package")]
+public async Task<ToolResult<PackageAnalysis>> AnalyzeAsync(
+    [Description("Package ID")] string packageId,
+    CancellationToken cancellationToken = default)
+{
+    try
+    {
+        cancellationToken.ThrowIfCancellationRequested();
+        
+        var package = await _service.GetPackageAsync(packageId, cancellationToken);
+        var analysis = await _analyzer.AnalyzeAsync(package, cancellationToken);
+        
+        return ToolResult.Success(analysis);
+    }
+    catch (OperationCanceledException)
+    {
+        _logger.LogInformation("Analysis cancelled for package: {PackageId}", packageId);
+        
+        return ToolResult.Failure<PackageAnalysis>(
+            "Analysis was cancelled",
+            "CANCELLED");
+    }
+    catch (Exception ex)
+    {
+        _logger.LogError(ex, "Error analyzing package: {PackageId}", packageId);
+        return ToolResult.Failure<PackageAnalysis>(
+            "Analysis failed. Please try again.",
+            "ANALYSIS_ERROR");
+    }
+}
+```
+
+## JSON Serialization for Error Types
+
+Don't forget to add error result types to your JSON context:
+
+```csharp
+[JsonSerializable(typeof(ToolResult<PackageMetadata>))]
+[JsonSerializable(typeof(ToolResult<IEnumerable<PackageMetadata>>))]
+[JsonSerializable(typeof(ToolResult<PackageAnalysis>))]
+[JsonSourceGenerationOptions(
+    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
+    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
+public partial class McpJsonContext : JsonSerializerContext
+{
+}
+```
+
+## Error Code Constants
+
+**Always use constants** instead of magic strings for error codes:
+
+```csharp
+public static class ErrorCodes
+{
+    // Validation errors (4xx equivalent)
+    public const string InvalidInput = "INVALID_INPUT";
+    public const string ValidationError = "VALIDATION_ERROR";
+    public const string InvalidArgument = "INVALID_ARGUMENT";
+    
+    // Business logic errors (4xx equivalent)
+    public const string NotFound = "NOT_FOUND";
+    public const string AlreadyExists = "ALREADY_EXISTS";
+    public const string Deprecated = "DEPRECATED";
+    public const string Forbidden = "FORBIDDEN";
+    
+    // Infrastructure errors (5xx equivalent)
+    public const string NetworkError = "NETWORK_ERROR";
+    public const string Timeout = "TIMEOUT";
+    public const string AuthError = "AUTH_ERROR";
+    public const string RateLimit = "RATE_LIMIT";
+    public const string ServiceUnavailable = "SERVICE_UNAVAILABLE";
+    
+    // Operation errors
+    public const string Cancelled = "CANCELLED";
+    public const string InternalError = "INTERNAL_ERROR";
+    public const string AnalysisError = "ANALYSIS_ERROR";
+}
+```
+
+**Usage:**
+
+```csharp
+if (string.IsNullOrWhiteSpace(query))
+{
+    return ToolResult.Failure<PackageInfo>(
+        "Search query cannot be empty",
+        ErrorCodes.InvalidInput);  // ✅ Type-safe constant
+}
+
+// Not this:
+return ToolResult.Failure<PackageInfo>(
+    "Search query cannot be empty",
+    "INVALID_INPUT");  // ❌ Magic string
+```
+
+**Benefits:**
+- Compile-time safety
+- Autocomplete support
+- Easy refactoring
+- Consistent error codes across tools
+- Easier to test (can reference constants in assertions)
+
+## Helper Extension Methods
+
+Create reusable helpers for common patterns:
+
+```csharp
+public static class ToolResult
+{
+    public static ToolResult<T> Success<T>(T data)
+    {
+        return new ToolResult<T>
+        {
+            Success = true,
+            Data = data,
+            Error = null,
+            ErrorCode = null
+        };
+    }
+    
+    public static ToolResult<T> Failure<T>(string error, string errorCode)
+    {
+        return new ToolResult<T>
+        {
+            Success = false,
+            Data = default,
+            Error = error,
+            ErrorCode = errorCode
+        };
+    }
+}
+```
+
+## Logging Best Practices
+
+```csharp
+// ✅ Good: Structured logging with context
+_logger.LogError(ex, 
+    "Failed to search packages. Query: {Query}, Limit: {Limit}, User: {UserId}",
+    query, limit, userId);
+
+// ❌ Bad: String concatenation
+_logger.LogError($"Failed to search packages: {ex.Message}");
+
+// ✅ Good: Different log levels for different scenarios
+_logger.LogWarning("Package {PackageId} not found", packageId);  // Expected scenario
+_logger.LogError(ex, "Unexpected error searching packages");      // Unexpected error
+
+// ✅ Good: Don't log sensitive data
+_logger.LogInformation("Authentication successful for user: {UserId}", userId);
+
+// ❌ Bad: Logging credentials
+_logger.LogInformation("Login attempt: {Username} / {Password}", user, pass);
+```
+
+## Error Response Examples
+
+LLM clients will see responses like:
+
+```json
+{
+  "success": true,
+  "data": [
+    { "id": "Newtonsoft.Json", "version": "13.0.3" }
+  ],
+  "error": null,
+  "errorCode": null
+}
+```
+
+```json
+{
+  "success": false,
+  "data": null,
+  "error": "Search query cannot be empty",
+  "errorCode": "INVALID_INPUT"
+}
+```
+
+```json
+{
+  "success": false,
+  "data": null,
+  "error": "Network error: Connection timed out",
+  "errorCode": "NETWORK_ERROR"
+}
+```
+
+## Common Error Codes
+
+Standardize error codes across your tools:
+
+| Code | Meaning | Usage |
+|------|---------|-------|
+| `INVALID_INPUT` | Input validation failed | Required fields missing, format errors |
+| `NOT_FOUND` | Resource not found | Package doesn't exist, ID not found |
+| `VALIDATION_ERROR` | Business rule violation | Invalid state, rule violation |
+| `AUTH_ERROR` | Authentication failed | Invalid credentials, unauthorized |
+| `RATE_LIMIT` | Too many requests | API rate limit exceeded |
+| `NETWORK_ERROR` | Network/connectivity issue | HTTP errors, timeouts |
+| `TIMEOUT` | Operation timed out | Long-running operation exceeded limit |
+| `CANCELLED` | Operation cancelled | User or system cancellation |
+| `INTERNAL_ERROR` | Unexpected error | Unhandled exceptions |
+
+## Testing Error Handling
+
+```csharp
+[Fact]
+public async Task SearchAsync_EmptyQuery_ReturnsValidationError()
+{
+    // Arrange
+    var tools = new PackageTools(_mockService);
+
+    // Act
+    var result = await tools.SearchAsync("");
+
+    // Assert
+    Assert.False(result.Success);
+    Assert.Equal("INVALID_INPUT", result.ErrorCode);
+    Assert.Contains("query", result.Error, StringComparison.OrdinalIgnoreCase);
+}
+
+[Fact]
+public async Task SearchAsync_NetworkError_ReturnsNetworkError()
+{
+    // Arrange
+    _mockService.SearchAsync(Arg.Any<string>(), Arg.Any<int>())
+        .ThrowsAsync(new HttpRequestException("Connection failed"));
+    
+    var tools = new PackageTools(_mockService);
+
+    // Act
+    var result = await tools.SearchAsync("test");
+
+    // Assert
+    Assert.False(result.Success);
+    Assert.Equal("NETWORK_ERROR", result.ErrorCode);
+    Assert.Contains("Network error", result.Error);
+}
+```
diff --git a/.github/skills/creating-dotnet-mcp-servers/references/testing.md b/.github/skills/creating-dotnet-mcp-servers/references/testing.md
@@ -0,0 +1,382 @@
+# Testing MCP Servers
+
+Complete guide for testing MCP tools with integration tests, unit tests, and test patterns.
+
+## Integration Test Setup
+
+Use `WebApplicationFactory` and `SseClientTransport` to test the actual MCP protocol:
+
+```csharp
+using Microsoft.AspNetCore.Mvc.Testing;
+using ModelContextProtocol.Client;
+using Xunit;
+
+public sealed class PackageToolsTests
+{
+    [Fact]
+    public async Task ListTools_ShouldReturnRegisteredTools()
+    {
+        // Arrange
+        var factory = new WebApplicationFactory<Program>()
+            .WithWebHostBuilder(builder => 
+            {
+                builder.UseUrls("http://localhost:5000");
+            });
+
+        var transport = new SseClientTransport(
+            new SseClientTransportOptions
+            {
+                Endpoint = new Uri("http://localhost:5000/sse"),
+            }, 
+            factory.CreateClient());
+        
+        var client = await McpClientFactory.CreateAsync(
+            transport, 
+            cancellationToken: TestContext.Current.CancellationToken);
+
+        // Act
+        var tools = await client.ListToolsAsync(
+            cancellationToken: TestContext.Current.CancellationToken);
+
+        // Assert
+        Assert.Single(tools);
+        Assert.Equal(PackageTools.SearchPackages, tools[0].Name);
+    }
+    
+    [Fact]
+    public async Task SearchPackages_ShouldReturnResults()
+    {
+        // Arrange
+        var factory = new WebApplicationFactory<Program>();
+        var transport = new SseClientTransport(
+            new SseClientTransportOptions { Endpoint = new Uri("http://localhost:5000/sse") },
+            factory.CreateClient());
+        
+        var client = await McpClientFactory.CreateAsync(transport);
+
+        // Act
+        var result = await client.CallToolAsync(
+            PackageTools.SearchPackages,
+            new { query = "Newtonsoft.Json", limit = 5 });
+
+        // Assert
+        Assert.NotNull(result);
+        Assert.NotEmpty(result.Content);
+    }
+}
+```
+
+### Integration Test Best Practices
+
+1. **Use WebApplicationFactory** - Tests real HTTP transport
+2. **Use unique ports** - Prevents port conflicts in parallel tests
+3. **Pass CancellationToken** - Enables test timeout handling
+4. **Test both ListTools and CallTool** - Verifies protocol compliance
+5. **Use tool name constants** - `PackageTools.SearchPackages` instead of magic strings
+
+## Unit Test (Tool Logic Only)
+
+Test business logic without MCP protocol overhead:
+
+```csharp
+using NSubstitute;
+using Xunit;
+
+public sealed class PackageToolsUnitTests
+{
+    [Fact]
+    public async Task SearchAsync_ValidQuery_ReturnsResults()
+    {
+        // Arrange
+        var mockService = Substitute.For<IPackageService>();
+        mockService.SearchAsync("test", 10)
+            .Returns(new[] { new PackageMetadata("Test.Package", "1.0.0") });
+        
+        var tools = new PackageTools(mockService);
+
+        // Act
+        var results = await tools.SearchAsync("test", 10);
+
+        // Assert
+        Assert.Single(results);
+        Assert.Equal("Test.Package", results.First().Id);
+    }
+    
+    [Theory]
+    [InlineData("")]
+    [InlineData(null)]
+    [InlineData("   ")]
+    public async Task SearchAsync_InvalidQuery_ReturnsError(string query)
+    {
+        // Arrange
+        var mockService = Substitute.For<IPackageService>();
+        var tools = new PackageTools(mockService);
+
+        // Act
+        var result = await tools.SearchAsync(query);
+
+        // Assert
+        Assert.False(result.Success);
+        Assert.Contains("query", result.Error, StringComparison.OrdinalIgnoreCase);
+    }
+}
+```
+
+## Test Organization
+
+Recommended structure:
+
+```
+tests/
+  YourProject.UnitTests/          # Fast, isolated tests
+    Tools/
+      PackageToolsTests.cs        # Tool business logic
+    Application/
+      UseCaseTests.cs             # Use case logic
+      
+  YourProject.IntegrationTests/   # Slower, MCP protocol tests
+    Features/
+      PackageToolsIntegrationTests.cs  # Full MCP stack
+```
+
+## Testing Multiple Tools
+
+```csharp
+[Theory]
+[InlineData(PackageTools.SearchPackages)]
+[InlineData(PackageTools.GetPackageInfo)]
+[InlineData(PackageTools.ListVersions)]
+public async Task AllTools_ShouldBeDiscoverable(string expectedToolName)
+{
+    // Arrange
+    var factory = new WebApplicationFactory<Program>();
+    var transport = new SseClientTransport(
+        new SseClientTransportOptions { Endpoint = new Uri("http://localhost:5000/sse") },
+        factory.CreateClient());
+    
+    var client = await McpClientFactory.CreateAsync(transport);
+
+    // Act
+    var tools = await client.ListToolsAsync();
+
+    // Assert
+    Assert.Contains(tools, t => t.Name == expectedToolName);
+}
+```
+
+## Testing Error Scenarios
+
+```csharp
+[Fact]
+public async Task CallTool_WithInvalidParameters_ReturnsErrorResponse()
+{
+    // Arrange
+    var factory = new WebApplicationFactory<Program>();
+    var transport = new SseClientTransport(
+        new SseClientTransportOptions { Endpoint = new Uri("http://localhost:5000/sse") },
+        factory.CreateClient());
+    
+    var client = await McpClientFactory.CreateAsync(transport);
+
+    // Act
+    var result = await client.CallToolAsync(
+        PackageTools.SearchPackages,
+        new { query = "", limit = -1 });  // Invalid parameters
+
+    // Assert
+    Assert.NotNull(result);
+    // Verify error is returned in structured format
+    var content = result.Content[0].Text;
+    Assert.Contains("error", content, StringComparison.OrdinalIgnoreCase);
+}
+```
+
+## Test Fixtures for Reusability
+
+Use fixtures to avoid duplicating MCP client setup:
+
+```csharp
+public sealed class McpServerFixture : IAsyncLifetime
+{
+    private WebApplicationFactory<Program>? _factory;
+    
+    public McpClient Client { get; private set; } = null!;
+    public WebApplicationFactory<Program> Factory => _factory!;
+
+    public async Task InitializeAsync()
+    {
+        _factory = new WebApplicationFactory<Program>()
+            .WithWebHostBuilder(builder =>
+            {
+                builder.UseUrls("http://localhost:5000");
+            });
+
+        var transport = new SseClientTransport(
+            new SseClientTransportOptions
+            {
+                Endpoint = new Uri("http://localhost:5000/sse"),
+            },
+            _factory.CreateClient());
+
+        Client = await McpClientFactory.CreateAsync(transport);
+    }
+
+    public async Task DisposeAsync()
+    {
+        if (_factory != null)
+        {
+            await _factory.DisposeAsync();
+        }
+    }
+}
+
+// Usage in test class
+public sealed class PackageToolsTests : IClassFixture<McpServerFixture>
+{
+    private readonly McpServerFixture _fixture;
+
+    public PackageToolsTests(McpServerFixture fixture)
+    {
+        _fixture = fixture;
+    }
+
+    [Fact]
+    public async Task ListTools_ShouldReturnRegisteredTools()
+    {
+        // Arrange - fixture provides ready client
+        var client = _fixture.Client;
+
+        // Act
+        var tools = await client.ListToolsAsync();
+
+        // Assert
+        Assert.Single(tools);
+        Assert.Equal(PackageTools.SearchPackages, tools[0].Name);
+    }
+    
+    [Fact]
+    public async Task SearchPackages_ShouldReturnResults()
+    {
+        // Reuse same client - much faster than creating new factory per test
+        var result = await _fixture.Client.CallToolAsync(
+            PackageTools.SearchPackages,
+            new { query = "Newtonsoft.Json", limit = 5 });
+
+        Assert.NotNull(result);
+    }
+}
+```
+
+**Benefits:**
+- Single MCP client initialization per test class (~80% faster test execution)
+- Shared factory reduces resource usage
+- Cleaner test methods (no setup boilerplate)
+- Proper cleanup via `IAsyncLifetime`
+
+## Testing with Test Containers
+
+For services requiring external dependencies (e.g., database, Redis):
+
+```csharp
+// Install: dotnet add package Testcontainers.MsSql
+using Testcontainers.MsSql;
+
+public sealed class PackageToolsWithDatabaseTests : IAsyncLifetime
+{
+    private readonly MsSqlContainer _dbContainer;
+    
+    public PackageToolsWithDatabaseTests()
+    {
+        _dbContainer = new MsSqlBuilder()
+            .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
+            .Build();
+    }
+
+    public async Task InitializeAsync()
+    {
+        await _dbContainer.StartAsync();
+    }
+
+    public async Task DisposeAsync()
+    {
+        await _dbContainer.StopAsync();
+    }
+
+    [Fact]
+    public async Task SearchPackages_AgainstRealDatabase_ReturnsResults()
+    {
+        // Test against real containerized database
+        var factory = new WebApplicationFactory<Program>()
+            .WithWebHostBuilder(builder =>
+            {
+                builder.ConfigureServices(services =>
+                {
+                    // Override connection string to use test container
+                    var connectionString = _dbContainer.GetConnectionString();
+                    services.AddDbContext<PackageDbContext>(options =>
+                        options.UseSqlServer(connectionString));
+                });
+            });
+
+        var transport = new SseClientTransport(
+            new SseClientTransportOptions { Endpoint = new Uri("http://localhost:5000/sse") },
+            factory.CreateClient());
+        
+        var client = await McpClientFactory.CreateAsync(transport);
+
+        var result = await client.CallToolAsync(
+            PackageTools.SearchPackages,
+            new { query = "test" });
+
+        Assert.NotNull(result);
+    }
+}
+```
+
+**Available Testcontainers:**
+- `Testcontainers.MsSql` - SQL Server
+- `Testcontainers.PostgreSql` - PostgreSQL
+- `Testcontainers.Redis` - Redis
+- `Testcontainers.MongoDb` - MongoDB
+- `Microcks.Testcontainers` - API mocking and testing
+- Many more at [dotnet.testcontainers.org](https://dotnet.testcontainers.org/)
+
+## Testing Cancellation
+
+```csharp
+[Fact]
+public async Task LongRunningTool_SupportsCancellation()
+{
+    // Arrange
+    var mockService = Substitute.For<IPackageService>();
+    mockService.SearchAsync(Arg.Any<string>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
+        .Returns(async callInfo =>
+        {
+            var ct = callInfo.Arg<CancellationToken>();
+            await Task.Delay(TimeSpan.FromSeconds(10), ct);
+            return Array.Empty<PackageMetadata>();
+        });
+    
+    var tools = new PackageTools(mockService);
+    var cts = new CancellationTokenSource();
+
+    // Act
+    var task = tools.SearchAsync("test", 10, cts.Token);
+    cts.CancelAfter(100); // Cancel after 100ms
+
+    // Assert
+    await Assert.ThrowsAsync<TaskCanceledException>(() => task);
+}
+```
+
+## Common Test Mistakes
+
+| Mistake | Fix |
+|---------|-----|
+| No `WebApplicationFactory` in integration tests | Can't test real transport → Use factory pattern |
+| Port conflicts in parallel tests | Use unique ports per test or dynamic port allocation |
+| Missing cancellation tokens | Can't test cancellation → Always pass CancellationToken |
+| Testing only happy path | Add error scenario tests with invalid inputs |
+| Not testing tool discovery | Test both `ListToolsAsync` and `CallToolAsync` |
+| Magic strings for tool names | Use constants defined in tool class |
+| Not cleaning up resources | Implement `IAsyncLifetime` for proper cleanup |
PATCH

echo "Gold patch applied."
