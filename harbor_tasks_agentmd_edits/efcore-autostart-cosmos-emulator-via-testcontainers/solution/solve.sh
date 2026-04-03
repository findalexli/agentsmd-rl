#!/usr/bin/env bash
set -euo pipefail

cd /workspace/efcore

# Idempotent: skip if already applied
if grep -q 'CosmosDbContainer' test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/cosmos-provider/SKILL.md b/.agents/skills/cosmos-provider/SKILL.md
index fb3634430ef..b3430ac644e 100644
--- a/.agents/skills/cosmos-provider/SKILL.md
+++ b/.agents/skills/cosmos-provider/SKILL.md
@@ -21,12 +21,7 @@ Non-relational provider with its own parallel query pipeline. Uses JSON for docu
 - `ETag` for optimistic concurrency
 - No cross-container joins

-## Azure Cosmos DB Emulator in Docker
+## Azure Cosmos DB Emulator for Tests

-Cosmos tests on Helix start the emulator from the work item via `PreCommands` that run a Docker container using:
-- `eng/testing/run-cosmos-container.ps1`
-- `eng/testing/run-cosmos-container.sh`
-
-These scripts can be invoked locally for testing on machines that don't have the emulator installed, but have docker available.
-
-The `Test__Cosmos__SkipConnectionCheck=true` env var is set to prevent tests from being skipped when the emulator failed to start.
+- `TestEnvironment.InitializeAsync()` auto-starts a `Testcontainers.CosmosDb` container when `Test__Cosmos__DefaultConnection` is not set. Set the env var to use an existing emulator instead.
+- Skip tests requiring unsupported features on the Linux emulator with `[CosmosCondition(CosmosCondition.IsNotLinuxEmulator)]`.
diff --git a/.github/workflows/copilot-setup-steps.yml b/.github/workflows/copilot-setup-steps.yml
index 5585f472d98..668da85e203 100644
--- a/.github/workflows/copilot-setup-steps.yml
+++ b/.github/workflows/copilot-setup-steps.yml
@@ -63,6 +63,8 @@ jobs:
       - name: Export environment variables for the agent's session
         run: |
           echo "Test__SqlServer__DefaultConnection=Server=localhost;Database=test;User=SA;Password=PLACEHOLDERPass$$w0rd;Connect Timeout=60;ConnectRetryCount=0;Trust Server Certificate=true" >> "$GITHUB_ENV"
+          echo "Test__Cosmos__DefaultConnection=https://localhost:8081" >> "$GITHUB_ENV"
           echo "Test__Cosmos__EmulatorType=linux" >> "$GITHUB_ENV"
+          echo "Test__Cosmos__SkipConnectionCheck=true" >> "$GITHUB_ENV"
           echo "DOTNET_ROOT=$PWD/.dotnet/" >> "$GITHUB_ENV"
           echo "$PWD/.dotnet/" >> $GITHUB_PATH
\ No newline at end of file
diff --git a/eng/helix.proj b/eng/helix.proj
index b8916309738..383d7816e73 100644
--- a/eng/helix.proj
+++ b/eng/helix.proj
@@ -64,8 +64,12 @@
       <PreCommands>$(PreCommands); SqlLocalDB start</PreCommands>
     </XUnitProject>
   </ItemGroup>
-
+
   <ItemGroup Condition = "'$(HelixTargetQueue.StartsWith(`Windows.11`))'">
+    <XUnitProject Remove="$(CosmosTests)"/>
+  </ItemGroup>
+
+  <ItemGroup Condition = "'$(HelixTargetQueue.StartsWith(`Windows.Server2025.Amd64`))'">
     <XUnitProject Update="$(CosmosTests)">
       <PreCommands>$(PreCommands); set Test__Cosmos__SkipConnectionCheck=true</PreCommands>
     </XUnitProject>
@@ -80,14 +84,11 @@
     </XUnitProject>
   </ItemGroup>

-  <!-- Start Cosmos emulator in Docker on Ubuntu and only run Cosmos tests -->
+  <!-- Run Cosmos tests on Ubuntu with Docker support (testcontainer auto-starts the emulator) -->
   <ItemGroup Condition = "'$(HelixTargetQueue)' == 'Ubuntu.2204.Amd64.XL.Open' OR '$(HelixTargetQueue)' == 'Ubuntu.2204.Amd64.XL'">
     <XUnitProject Remove="$(RepoRoot)/test/**/*.csproj"/>
     <XUnitProject Remove="$(RepoRoot)/test/**/*.fsproj"/>
-    <XUnitProject Include="$(CosmosTests)">
-      <PreCommands>$(PreCommands); chmod +x $HELIX_CORRELATION_PAYLOAD/testing/run-cosmos-container.sh; $HELIX_CORRELATION_PAYLOAD/testing/run-cosmos-container.sh; export Test__Cosmos__DefaultConnection=https://localhost:8081; export Test__Cosmos__SkipConnectionCheck=true; export Test__Cosmos__EmulatorType=linux</PreCommands>
-      <PostCommands>$(PostCommands); docker stop cosmos-emulator || true; docker rm -f cosmos-emulator || true</PostCommands>
-    </XUnitProject>
+    <XUnitProject Include="$(CosmosTests)"/>
   </ItemGroup>

   <!-- Run tests that don't need SqlServer or Cosmos on bare Ubuntu -->
diff --git a/eng/testing/run-cosmos-container.ps1 b/eng/testing/run-cosmos-container.ps1
deleted file mode 100644
index e5cde422b52..00000000000
--- a/eng/testing/run-cosmos-container.ps1
+++ /dev/null
@@ -1,61 +0,0 @@
-# Starts the Azure Cosmos DB Emulator in a Windows Docker container and waits for it to be ready.
-# Tests run on the host machine connecting to the emulator via https://localhost:8081.
-# Usage: .\run-cosmos-container.ps1
-param()
-
-$ErrorActionPreference = 'Stop'
-$image = 'mcr.microsoft.com/cosmosdb/windows/azure-cosmos-emulator'
-$containerName = 'cosmos-emulator'
-$port = 8081
-$maxRetries = 90
-$retryDelaySec = 2
-
-Write-Host "Pulling image: $image"
-docker pull $image
-if ($LASTEXITCODE -ne 0) { throw "docker pull failed with exit code $LASTEXITCODE" }
-
-Write-Host "Checking for existing container named $containerName..."
-$existingContainerId = docker ps -a --filter "name=^${containerName}$" --format '{{.ID}}'
-if ($LASTEXITCODE -ne 0) { throw "docker ps failed with exit code $LASTEXITCODE" }
-if ($existingContainerId) {
-    Write-Host "Existing container '$containerName' found. Stopping and removing it..."
-    docker stop $containerName 2>$null
-    docker rm -f $containerName
-    if ($LASTEXITCODE -ne 0) { throw "docker rm failed with exit code $LASTEXITCODE" }
-}
-
-# -t is required because Start.ps1 sets [Console]::BufferWidth which needs a TTY handle.
-Write-Host "Starting Cosmos DB Emulator container on port $port..."
-docker run -d -t `
-    --name $containerName `
-    --publish "${port}:8081" `
-    --memory 2G `
-    $image
-if ($LASTEXITCODE -ne 0) { throw "docker run failed with exit code $LASTEXITCODE" }
-
-Write-Host "Waiting for emulator to be ready (up to $($maxRetries * $retryDelaySec)s)..."
-$ready = $false
-for ($i = 0; $i -lt $maxRetries; $i++) {
-    Start-Sleep -Seconds $retryDelaySec
-    # Any HTTP response (even 401) means the emulator is up and accepting connections.
-    $null = & curl.exe -k "https://localhost:${port}/" --silent --output NUL --max-time 5
-    if ($LASTEXITCODE -eq 0) {
-        $ready = $true
-    } else {
-        Write-Host "  Attempt $($i+1)/$maxRetries - not ready yet..."
-    }
-    if ($ready) {
-        Write-Host "Cosmos DB Emulator is ready on port $port."
-        break
-    }
-}
-
-if (-not $ready) {
-    Write-Host "Emulator did not become ready. Container logs:"
-    docker logs $containerName
-    docker stop $containerName 2>$null
-    docker rm -f $containerName 2>$null
-    exit 1
-}
-
-exit 0
diff --git a/eng/testing/run-cosmos-container.sh b/eng/testing/run-cosmos-container.sh
deleted file mode 100644
index 8005f6b12b5..00000000000
--- a/eng/testing/run-cosmos-container.sh
+++ /dev/null
@@ -1,51 +0,0 @@
-#!/usr/bin/env bash
-# Starts the Azure Cosmos DB Linux (vNext) Emulator in a Docker container and waits for it to be ready.
-# Tests run on the host machine connecting to the emulator via https://localhost:8081.
-# The --protocol https flag is required because the .NET SDK does not support HTTP mode.
-# Usage: ./run-cosmos-container.sh
-
-set -e
-
-image='mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview'
-container_name='cosmos-emulator'
-port=8081
-max_retries=30
-retry_delay=2
-
-echo "Pulling image: $image"
-docker pull "$image"
-
-if docker ps -a --format '{{.Names}}' | grep -Eq "^${container_name}\$"; then
-    echo "Removing existing Cosmos DB Emulator container: $container_name"
-    docker rm -f "$container_name"
-fi
-
-echo "Starting Cosmos DB Emulator container on port $port with HTTPS..."
-docker run -d \
-    --name "$container_name" \
-    --publish "${port}:8081" \
-    "$image" \
-    --protocol https \
-    --enable-explorer false
-
-echo "Waiting for emulator to be ready (up to ~$((max_retries * retry_delay))s)..."
-ready=false
-for i in $(seq 1 "$max_retries"); do
-    sleep "$retry_delay"
-    if curl -ks --connect-timeout "$retry_delay" --max-time "$retry_delay" "https://localhost:${port}/" -o /dev/null; then
-        ready=true
-        echo "Cosmos DB Emulator is ready."
-        break
-    fi
-    echo "  Attempt $i/$max_retries - not ready yet..."
-done
-
-if [ "$ready" != true ]; then
-    echo "Emulator did not become ready. Container logs:"
-    docker logs "$container_name"
-    docker stop "$container_name" 2>/dev/null || true
-    docker rm -f "$container_name" 2>/dev/null || true
-    exit 1
-fi
-
-exit 0
diff --git a/test/Directory.Packages.props b/test/Directory.Packages.props
index 2dcd2f6da76..936b20c8b55 100644
--- a/test/Directory.Packages.props
+++ b/test/Directory.Packages.props
@@ -18,5 +18,6 @@
     <PackageVersion Include="OpenTelemetry.Exporter.InMemory" Version="$(OpenTelemetryExporterInMemoryVersion)" />
     <PackageVersion Include="SQLitePCLRaw.provider.sqlite3" Version="$(SQLitePCLRawVersion)" />
     <PackageVersion Include="SQLitePCLRaw.provider.winsqlite3" Version="$(SQLitePCLRawVersion)" />
+    <PackageVersion Include="Testcontainers.CosmosDb" Version="4.11.0" />
   </ItemGroup>
 </Project>
diff --git a/test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj b/test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj
index 5be9cabc700..afcf4bb3261 100644
--- a/test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj
+++ b/test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj
@@ -80,6 +80,7 @@
     <PackageReference Include="Microsoft.Extensions.Configuration.Json" />
     <PackageReference Include="Azure.Identity" />
     <PackageReference Include="Azure.ResourceManager.CosmosDB" />
+    <PackageReference Include="Testcontainers.CosmosDb" />
   </ItemGroup>

 </Project>
diff --git a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs
index e516a5b791b..f19ee56afb8 100644
--- a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs
+++ b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs
@@ -7,16 +7,25 @@ namespace Microsoft.EntityFrameworkCore.TestUtilities;

 public static class CosmosDbContextOptionsBuilderExtensions
 {
+    private static HttpMessageHandler? _handler;
+    private static Func<HttpClient>? _httpClientFactory;
+
     public static CosmosDbContextOptionsBuilder ApplyConfiguration(this CosmosDbContextOptionsBuilder optionsBuilder)
     {
+        if (_httpClientFactory == null)
+        {
+            _handler = TestEnvironment.HttpMessageHandler
+                ?? new HttpClientHandler
+                {
+                    ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
+                };
+            _httpClientFactory = () => new HttpClient(_handler, disposeHandler: false);
+        }
+
         optionsBuilder
             .ExecutionStrategy(d => new TestCosmosExecutionStrategy(d))
             .RequestTimeout(TimeSpan.FromMinutes(20))
-            .HttpClientFactory(() => new HttpClient(
-                new HttpClientHandler
-                {
-                    ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
-                }))
+            .HttpClientFactory(_httpClientFactory)
             .ConnectionMode(ConnectionMode.Gateway);

         return optionsBuilder;
diff --git a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs
index 2cb8cbdb14a..e7f41302d60 100644
--- a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs
+++ b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs
@@ -79,10 +79,10 @@ private static string CreateName(string name)
             ? name
             : name + _runId;

-    public string ConnectionUri { get; }
+    public string ConnectionUri { get; private set; }
     public string AuthToken { get; }
     public TokenCredential TokenCredential { get; }
-    public string ConnectionString { get; }
+    public string ConnectionString { get; private set; }

     private static readonly SemaphoreSlim _connectionSemaphore = new(1, 1);

@@ -175,6 +175,12 @@ private static bool IsNotConfigured(Exception exception)

     protected override async Task InitializeAsync(Func<DbContext> createContext, Func<DbContext, Task>? seed, Func<DbContext, Task>? clean)
     {
+        await TestEnvironment.InitializeAsync().ConfigureAwait(false);
+
+        // Update connection details in case InitializeAsync changed them (e.g., testcontainer started).
+        ConnectionUri = TestEnvironment.DefaultConnection;
+        ConnectionString = TestEnvironment.ConnectionString;
+
         _initialized = true;

         if (_connectionAvailable == false)
diff --git a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs
index b51f94f0da1..2c4a512a9fa 100644
--- a/test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs
+++ b/test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs
@@ -4,6 +4,7 @@
 using Azure.Core;
 using Azure.Identity;
 using Microsoft.Extensions.Configuration;
+using Testcontainers.CosmosDb;

 namespace Microsoft.EntityFrameworkCore.TestUtilities;

@@ -22,15 +23,124 @@ public static class TestEnvironment
         .Build()
         .GetSection("Test:Cosmos");

-    public static string DefaultConnection { get; } = string.IsNullOrEmpty(Config["DefaultConnection"])
+    private static CosmosDbContainer _container;
+    private static bool _initialized;
+    private static readonly SemaphoreSlim _initSemaphore = new(1, 1);
+
+    public static string DefaultConnection { get; private set; } = string.IsNullOrEmpty(Config["DefaultConnection"])
         ? "https://localhost:8081"
         : Config["DefaultConnection"];

+    internal static HttpMessageHandler HttpMessageHandler { get; private set; }
+
+    public static async Task InitializeAsync()
+    {
+        if (_initialized)
+        {
+            return;
+        }
+
+        await _initSemaphore.WaitAsync().ConfigureAwait(false);
+
+        try
+        {
+            if (_initialized)
+            {
+                return;
+            }
+
+            // If a connection string is specified (env var, config.json...), always use that.
+            var configured = Config["DefaultConnection"];
+            if (!string.IsNullOrEmpty(configured))
+            {
+                DefaultConnection = configured;
+                _initialized = true;
+                return;
+            }
+
+            // Try to connect to the default emulator endpoint (e.g. Windows emulator or
+            // a manually-started Docker container).
+            if (await TryProbeEmulatorAsync("https://localhost:8081").ConfigureAwait(false))
+            {
+                DefaultConnection = "https://localhost:8081";
+                _initialized = true;
+                return;
+            }
+
+            // Start a testcontainer with the Linux emulator.
+            CosmosDbContainer container;
+            try
+            {
+                container = new CosmosDbBuilder("mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview")
+                    .Build();
+                await container.StartAsync().ConfigureAwait(false);
+            }
+            catch (Exception ex)
+            {
+                throw new InvalidOperationException(
+                    "Failed to start the Cosmos DB emulator testcontainer. "
+                    + "Ensure that either the Cosmos DB emulator is running on localhost:8081, "
+                    + "or Docker is installed and running, "
+                    + "or set the 'Test__Cosmos__DefaultConnection' environment variable to connect to "
+                    + "an existing emulator or Cosmos DB instance.",
+                    ex);
+            }
+
+            _container = container;
+
+            AppDomain.CurrentDomain.ProcessExit += (_, _) =>
+            {
+                try
+                {
+                    _container.DisposeAsync().AsTask().GetAwaiter().GetResult();
+                }
+                catch
+                {
+                    // Best-effort cleanup: container may already be stopped or Docker daemon
+                    // may have exited before the process exit handler runs.
+                }
+            };
+
+            DefaultConnection = new UriBuilder(
+                Uri.UriSchemeHttp,
+                _container.Hostname,
+                _container.GetMappedPublicPort(CosmosDbBuilder.CosmosDbPort)).ToString();
+            HttpMessageHandler = _container.HttpMessageHandler;
+
+            _initialized = true;
+        }
+        finally
+        {
+            _initSemaphore.Release();
+        }
+    }
+
+    private static async Task<bool> TryProbeEmulatorAsync(string endpoint)
+    {
+        try
+        {
+            using var handler = new HttpClientHandler
+            {
+                ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
+            };
+            using var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(3) };
+            // Any successful response (even 401) means the emulator is up and accepting connections.
+            using var response = await client.GetAsync(endpoint).ConfigureAwait(false);
+            return true;
+        }
+        catch
+        {
+            // Expected: HttpRequestException (connection refused), TaskCanceledException (timeout),
+            // or SocketException when the emulator is not running.
+            return false;
+        }
+    }
+
     public static string AuthToken { get; } = string.IsNullOrEmpty(Config["AuthToken"])
         ? _emulatorAuthToken
         : Config["AuthToken"];

-    public static string ConnectionString { get; } = $"AccountEndpoint={DefaultConnection};AccountKey={AuthToken}";
+    public static string ConnectionString => $"AccountEndpoint={DefaultConnection};AccountKey={AuthToken}";

     public static bool UseTokenCredential { get; } = string.Equals(Config["UseTokenCredential"], "true", StringComparison.OrdinalIgnoreCase);

@@ -45,12 +155,14 @@ public static class TestEnvironment
         ? AzureLocation.WestUS
         : Enum.Parse<AzureLocation>(Config["AzureLocation"]);

-    public static bool IsEmulator { get; } = !UseTokenCredential && (AuthToken == _emulatorAuthToken);
+    public static bool IsEmulator => !UseTokenCredential && (AuthToken == _emulatorAuthToken);

     public static bool SkipConnectionCheck { get; } = string.Equals(Config["SkipConnectionCheck"], "true", StringComparison.OrdinalIgnoreCase);

-    public static string EmulatorType { get; } = Config["EmulatorType"] ?? (!OperatingSystem.IsWindows() ? "linux" : "");
+    public static string EmulatorType => _container != null
+        ? "linux"
+        : Config["EmulatorType"] ?? (!OperatingSystem.IsWindows() ? "linux" : "");

-    public static bool IsLinuxEmulator { get; } = IsEmulator
+    public static bool IsLinuxEmulator => IsEmulator
         && EmulatorType.Equals("linux", StringComparison.OrdinalIgnoreCase);
 }
diff --git a/test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json b/test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json
index 005eaf2a8a6..9edbace42c6 100644
--- a/test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json
+++ b/test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json
@@ -1,7 +1,7 @@
 {
   "Test": {
     "Cosmos": {
-      "DefaultConnection": "https://localhost:8081",
+      "DefaultConnection": null,
       "AuthToken": "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
     }
   }

PATCH

echo "Patch applied successfully."
