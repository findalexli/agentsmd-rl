#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shokoserver

# Idempotency guard
if grep -qF "**API versioning**: `v0` (version-less: auth + legacy Plex webhooks + index redi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -17,15 +17,17 @@ Target framework: `.NET 10.0`. Configurations: `Debug`, `Release`, `ApiLogging`,
 `.editorconfig` with ReSharper enforcement:
 - Line length: 160 characters
 - Modifier order: `private, protected, public, internal, sealed, new, override, virtual, abstract, static, extern, async, unsafe, volatile, readonly, required, file`
-- `var` when type is apparent; braces on new lines (`csharp_new_line_before_open_brace = all`)
+- **`var` preferred everywhere** — `csharp_style_var_elsewhere`, `csharp_style_var_for_built_in_types`, and `csharp_style_var_when_type_is_apparent` all set to `true` (enforced as warnings in `src/` paths)
+- Braces on new lines (`csharp_new_line_before_open_brace = all`)
+- Naming: `_camelCase` for instance fields, `_camelCase` for static fields, `PascalCase` for methods/classes/properties, `camelCase` for locals/parameters
 
 ## Architecture
 
 ### Project Layout
 
 - **`Shoko.Abstractions`** — NuGet package for plugin authors. Defines the interface contract between the core and plugins (`IPlugin`, `IShokoSeries`, `IShokoEpisode`, `IVideo`, `IUser`, and all service/metadata/video/user interfaces). Only update this when the plugin contract itself needs to change.
 - **`Shoko.Server`** — All implementation: API, database, repositories, services, scheduling, providers, models.
-- **`Shoko.CLI`** — Headless server entry point. Hosts `SystemService` as `IHostedService`.
+- **`Shoko.CLI`** — Headless server entry point. Instantiates and manages `SystemService` directly.
 - **`Shoko.TrayService`** — Cross-platform tray app (Avalonia) embedding the server. Runs on Windows, Linux, and macOS.
 - **`Plugins/`** — Built-in plugins (`ReleaseExporter`, `RelocationPlus`, `OfflineImporter`) built as separate projects and loaded at runtime.
 - **`Shoko.Tests`** — Unit tests.
@@ -35,8 +37,12 @@ Target framework: `.NET 10.0`. Configurations: `Debug`, `Release`, `ApiLogging`,
 
 ### Startup Sequence
 
+Entry points: `Shoko.CLI/Program.cs` (headless) or `Shoko.TrayService/Program.cs` (tray app). Both instantiate `new SystemService()` directly, which internally builds and starts the `IHost`.
+
 `Program.cs` → `SystemService` constructor (NLog, `PluginManager`, `ConfigurationService`, `SettingsProvider`) → `SystemService.StartAsync()` (builds and starts `IHost` / ASP.NET Core on port 8111) → `SystemService.LateStart()` (DB migrations via `DatabaseFixes`, init Quartz scheduler, UDP connection handler, file watchers).
 
+**Note:** `LateStart()` is skipped during first-run setup mode (`InSetupMode == true`). It runs either on normal startup or when `CompleteSetup()` transitions out of setup mode.
+
 Global service container is exposed via `Utils.ServiceContainer = _webHost.Services` for legacy code that predates DI,
 and should not be used for new code unless DI is not an option and only as a last resort.
 
@@ -69,7 +75,9 @@ and should not be used for new code unless DI is not an option and only as a las
 - During first-run setup, `InitUser` (synthetic admin) is used — no real auth required
 - No cookie sessions; every request is authenticated by API key
 
-**API versioning**: `v0` (version-less: auth + legacy Plex webhooks), `v1` (legacy REST, off by default), `v2` (legacy REST, can be kill-switched), `v3` (current, all new endpoints). Version can be resolved from query string, `api-version` header, or custom `ShokoApiReader`. `ApiVersionControllerFeatureProvider` excludes disabled versions at startup via individual flags (`EnableAPIv1`, `EnableAPIv2`, `EnableAPIv3`, `EnableLegacyPlexAPI`, `EnableAuthAPI`).
+**API versioning**: `v0` (version-less: auth + legacy Plex webhooks + index redirect), `v1` (legacy REST, off by default), `v2` (legacy REST, can be kill-switched), `v3` (current, all new endpoints). Version can be resolved from query string, `api-version` header, or custom `ShokoApiReader`. `ApiVersionControllerFeatureProvider` excludes disabled versions at startup via individual flags (`EnableAPIv1`, `EnableAPIv2`, `EnableAPIv3`, `EnableLegacyPlexAPI`, `EnableAuthAPI`).
+
+**Serialization**: MVC uses `AddNewtonsoftJson()` (not `System.Text.Json`) with: `MaxDepth = 10`, `DefaultContractResolver`, `NullValueHandling.Include`, `DefaultValueHandling.Populate`. SignalR also uses `AddNewtonsoftJsonProtocol()`.
 
 Plugin controllers are registered via `AddPluginControllers` during API setup.
 
@@ -119,14 +127,38 @@ Two variants in `Shoko.Server/Repositories/`:
 
 Always prefer a cached repository over a direct one when both exist for the same entity.
 
+**Access pattern**: Repositories are accessed via the `RepoFactory` static class (e.g., `RepoFactory.AnimeSeries.GetByID(id)`). `RepoFactory` is DI-registered but exposes static fields for convenience — this is a legacy pattern similar to `Utils.ServiceContainer`. This exists for compatibility where DI is unavailable, but DI should be used if possible.
+
 ### Scheduling
 
 Quartz.NET with a custom in-memory `ThreadPooledJobStore` (`Shoko.Server/Scheduling/`). Jobs in `Jobs/` are DI-resolved via `JobFactory`. `QueueStateEventHandler` fires domain events (job added/started/completed) consumed by `QueueEventEmitter` → SignalR clients. `DatabaseLocks/` provides named locks to prevent concurrent conflicting DB operations.
 
+**Note:** Quartz is referenced as local DLLs from `Dependencies/Quartz/` (not a NuGet package), using a custom/forked build.
+
 ### Plugin System
 
 `PluginManager` scans the `/plugins/` directory, loads assemblies, finds `IPlugin` implementations via reflection, and registers their services via `RegisterPlugins(IServiceCollection)`. `InitPlugins()` instantiates the plugins after the service container is available. `CorePlugin` is the built-in plugin that ships with the server.
 
+Plugins can also implement `IPluginApplicationRegistration` to register custom middleware via `RegisterServices(IApplicationBuilder, ApplicationPaths)` — invoked during `UseAPI()` after SignalR but before CORS.
+
+Plugin controllers are registered via `AddPluginControllers` during API setup.
+
+### Configuration System
+
+**No `appsettings.json`** exists in the repo. Configuration is code-based:
+- **`ServerSettings`** — primary settings class, persisted to `settings-server.json` via `[StorageLocation]` attribute
+- **`ConfigurationProvider<T>`** — generic provider using `INewtonsoftJsonConfiguration` for JSON serialization
+- **`SettingsProvider`** — singleton accessor (`Utils.SettingsProvider`) for runtime settings access
+- `appsettings.json` is configured as an **optional** overlay in the host builder but is not shipped
+
+### Testing
+
+- **Framework**: xUnit 2.7.0 with `Xunit.DependencyInjection` 9.1.0 for DI in tests
+- **Mocking**: Moq 4.20.70
+- **Coverage**: coverlet 6.0.2
+- **Test SDK**: Microsoft.NET.Test.Sdk 17.9.0
+- Unit tests in `Shoko.Tests/`, integration tests in `Shoko.IntegrationTests/`
+
 ### Database Migrations
 
 All schema migrations and data fixups are in `Shoko.Server/Databases/DatabaseFixes.cs`. Append new migrations; never modify existing ones. `Versions` class tracks the applied migration level. Supported backends: SQLite (default), MySQL/MariaDB, SQL Server — selected via `DatabaseFactory`.
@@ -137,6 +169,10 @@ All schema migrations and data fixups are in `Shoko.Server/Databases/DatabaseFix
 
 **`VideoLocal`** is the canonical record for a unique file, identified by its ED2K hash + file size. It holds hashes, `MediaInfo`, import date, and AniDB MyList ID. It does not store a path.
 
+**Note:** `VideoLocal.MediaInfo` is serialized using **MessagePack** via a custom NHibernate type (`MessagePackConverter<MediaContainer>`), not JSON.
+
+**Note:** `FilterPreset.Expression` and `FilterPreset.SortingExpression` use a custom NHibernate type (`FilterExpressionConverter`) for JSON serialization.
+
 **`VideoLocal_Place`** stores where a `VideoLocal` physically lives: a `ManagedFolderID` + `RelativePath`. One `VideoLocal` can have multiple places (the same file duplicated across folders). The absolute path is computed at runtime as `folder.Path + place.RelativePath`.
 
 **`ShokoManagedFolder`** (formerly `ImportFolder`) is a root directory Shoko monitors. Each folder has `IsWatched`, `IsDropSource`, and `IsDropDestination` flags used by the file relocation system.
PATCH

echo "Gold patch applied."
