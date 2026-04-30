#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dd-trace-dotnet

# Idempotency guard
if grep -qF "> **For AI Agents**: This file provides a navigation hub and quick reference. Ea" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,7 @@
 # Repository Guidelines
 
+> **For AI Agents**: This file provides a navigation hub and quick reference. Each section includes "📖 Load when..." guidance to help you decide which detailed documentation files to load based on your current task.
+
 ## Project Structure & Module Organization
 
 - tracer/src — Managed tracer, analyzers, tooling.
@@ -14,7 +16,7 @@
 
 - Auto-instrumentation: Native CLR profiler hooks the runtime (CallTarget) and loads the managed tracer.
 - Managed tracer: `Datadog.Trace` handles spans, context propagation, and library integrations.
-- Loader/home: Build outputs publish a “monitoring home”; the native loader boots the tracer from there.
+- Loader/home: Build outputs publish a "monitoring home"; the native loader boots the tracer from there.
 - Build system: Nuke coordinates .NET builds and CMake/vcpkg for native components.
 
 ## Tracer Structure
@@ -66,9 +68,8 @@
   - `Datadog.AutoInstrumentation.Generator` — Instrumentation metadata generators.
 - `Datadog.Tracer.Native` — Native interop glue and packaging metadata.
 
-### Tracer Structure (Detailed)
-
-Tree Overview
+<details>
+<summary>Detailed Tracer Structure (Tree View + Component Details)</summary>
 
 ```
 tracer/src/Datadog.Trace
@@ -110,6 +111,8 @@ tracer/src/Datadog.Trace
 └─ Vendors/                ─ Vendored deps
 ```
 
+**Component Details:**
+
 - ClrProfiler — Auto-instrumentation runtime
   - AutoInstrumentation — Integrations grouped by tech (AWS, AdoNet, AspNet/AspNetCore, Azure, Couchbase, Elasticsearch, GraphQL, Grpc, Http, IbmMq, Kafka, Logging, MongoDb, Msmq, OpenTelemetry, Process, Protobuf, RabbitMQ, Redis, Remoting, RestSharp, Testing, TraceAnnotations, Wcf).
   - CallTarget — Invoker, handlers, state structs, async continuations and helpers.
@@ -162,63 +165,58 @@ tracer/src/Datadog.Trace
 - Util — Common utilities (time, concurrency, env, etc.).
 - Vendors — Vendored dependencies (e.g., Newtonsoft patches) kept in sync.
 
-## Build, Test, and Development Commands
-
-- Build tracer home (default): `./tracer/build.sh` or `powershell ./tracer/build.ps1`.
-- Show config: `./tracer/build.sh Info`.
-- Unit tests (managed): `./tracer/build.sh BuildAndRunManagedUnitTests`.
-- Unit tests (native): `./tracer/build.sh RunNativeUnitTests`.
-- Integration tests: Linux `BuildAndRunLinuxIntegrationTests`, macOS `BuildAndRunOsxIntegrationTests`, Windows `BuildAndRunWindowsIntegrationTests`.
-- Package artifacts: `./tracer/build.sh PackageTracerHome`.
-- Coverage: append `--code-coverage-enabled true`.
-
-## Nuke Targets
-
-- Usage: `./tracer/build.sh <Target> [--option value]` (Windows: `powershell ./tracer/build.ps1 <Target>`). List all with `--help`.
-- Core
-  - `Info` — Print current build config.
-  - `Clean` — Remove build outputs/obj/bin.
-  - `BuildTracerHome` — Build native + managed tracer and publish monitoring home (default).
-  - `BuildProfilerHome` — Build/provision profiler artifacts.
-  - `BuildNativeLoader` — Build and publish native loader.
-  - `PackNuGet` / `PackageTracerHome` — Create NuGet/MSI/zip artifacts.
-- Tests (managed/native)
-  - `BuildAndRunManagedUnitTests` — Build and run managed unit tests.
-  - `RunNativeUnitTests` — Build and run native unit tests.
-  - `RunIntegrationTests` — Execute integration tests (used by OS-specific wrappers below).
-  - Debugger: `BuildAndRunDebuggerIntegrationTests`.
-- Platform wrappers
-  - Windows: `BuildAndRunWindowsIntegrationTests`, `BuildAndRunWindowsRegressionTests`, `BuildAndRunWindowsAzureFunctionsTests`.
-  - Linux: `BuildAndRunLinuxIntegrationTests`.
-  - macOS: `BuildAndRunOsxIntegrationTests`.
-- Profiler & Native
-  - `CompileProfilerNativeSrc`, `CompileProfilerNativeTests`, `RunProfilerNativeUnitTests{Windows|Linux}`.
-  - Static analysis: `RunClangTidyProfiler{Windows|Linux}`, `RunCppCheckProfiler{Windows|Linux}`.
-  - Native loader tests: `CompileNativeLoader*`, `RunNativeLoaderTests{Windows|Linux}`.
-- Tools & Utilities
-  - `BuildRunnerTool`, `PackRunnerToolNuget`, `BuildStandaloneTool`, `InstallDdTraceTool`.
-  - `RunBenchmarks` — Execute performance benchmarks.
-  - `UpdateSnapshots`, `PrintSnapshotsDiff` — Snapshot testing utilities.
-  - `UpdateVersion`, `GenerateSpanDocumentation`, `RunInstrumentationGenerator` — Maintenance.
-
-## macOS Development
-
-- Prereqs: Install .NET SDK, Xcode Command Line Tools, and `cmake` (`brew install cmake`).
-- Build: `./tracer/build.sh Clean BuildTracerHome`.
-- Unit tests: `./tracer/build.sh BuildAndRunManagedUnitTests BuildAndRunNativeUnitTests`.
-- Integration tests: `docker-compose up StartDependencies.OSXARM64`; run `./tracer/build.sh BuildAndRunOsxIntegrationTests`; `docker-compose down` to stop.
-- Filters as needed: `--framework net6.0` and `--filter "Category=Smoke"`.
-- Apple Silicon: Some services are x86-only; see `docker-compose.yml` comments. Consider Colima if you need amd64 containers.
-- Details: see `tracer/README.MD` (macOS section).
-
-## Coding Style & Naming Conventions
-
-- C#: see `.editorconfig` (4-space indent, `System.*` first, prefer `var`). Types/methods PascalCase; locals camelCase.
-  - When a "using" directive is missing in a file, add it instead of using fully-qualified type names.
-  - Use modern C# syntax, but avoid syntax that requires types not available in older runtimes (for example, don't use syntax that requires ValueTuple because is not included in .NET Framework 4.6.1)
-  - Prefer modern collection expressions (`[]`)
-- StyleCop: see `tracer/stylecop.json`; address warnings before pushing.
-- C/C++: see `.clang-format`; keep consistent naming.
+</details>
+
+## Build & Development
+
+**Quick start:**
+- Build: `./tracer/build.sh` (Linux/macOS) or `.\tracer\build.cmd` (Windows)
+- Unit tests: `./tracer/build.sh BuildAndRunManagedUnitTests`
+- Integration tests: `BuildAndRunLinuxIntegrationTests` / `BuildAndRunWindowsIntegrationTests` / `BuildAndRunOsxIntegrationTests`
+
+📖 **Load when**: Setting up development environment, running builds, or troubleshooting build issues
+- **`tracer/README.MD`** — Complete development setup guide (VS requirements, Docker, Dev Containers, platform-specific build commands, and Nuke targets)
+
+## Creating Integrations
+
+**Quick reference:**
+- Location: `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/<Area>/<Integration>.cs`
+- Add `[InstrumentMethod]` attribute with assembly/type/method details and version range
+- Implement `OnMethodBegin` and `OnMethodEnd`/`OnAsyncMethodEnd` handlers
+- Use duck typing constraints (`where TReq : IMyShape, IDuckType`) or `obj.DuckCast<IMyShape>()` for third-party types
+- Tests: Add under `tracer/test/Datadog.Trace.ClrProfiler.IntegrationTests` with samples in `tracer/test/test-applications/integrations`
+- Generate boilerplate: `./tracer/build.ps1 RunInstrumentationGenerator`
+
+📖 **Load when**: Creating a new integration or adding instrumentation to an existing library
+- **`docs/development/AutomaticInstrumentation.md`** — Complete guide to creating integrations, CallTarget wiring, testing strategies, package version configuration, and CI testing
+
+📖 **Load when**: Working with third-party types that can't be directly referenced or need version-agnostic access
+- **`docs/development/DuckTyping.md`** — Duck typing patterns, proxy types, binding attributes, best practices, and performance benchmarks
+
+## Azure Functions & Serverless
+
+**Quick reference:**
+- **Setup**: Use Azure App Services Site Extension on Windows Premium/Elastic Premium/Dedicated plans; use `Datadog.AzureFunctions` NuGet package for Linux Consumption/Container Apps
+- **Tests**: `BuildAndRunWindowsAzureFunctionsTests` Nuke target; samples under `tracer/test/test-applications/azure-functions/`
+- **Dependencies**: `Datadog.AzureFunctions` → `Datadog.Serverless.Compat` ([datadog-serverless-compat-dotnet](https://github.com/DataDog/datadog-serverless-compat-dotnet)) contains agent executable
+
+📖 **Load when**: Working on Azure Functions instrumentation or debugging serverless issues
+- **`docs/development/AzureFunctions.md`** — In-process vs isolated worker models, instrumentation specifics, ASP.NET Core integration, GRPC context propagation, and debugging guide
+
+📖 **Load when**: Working on AWS Lambda or general serverless instrumentation
+- **`docs/development/Serverless.md`** — Serverless instrumentation patterns across cloud providers
+
+## Coding Standards
+
+**C# style:**
+- See `.editorconfig` (4-space indent, `System.*` first, prefer `var`). Types/methods PascalCase; locals camelCase
+- Add missing `using` directives instead of fully-qualified type names
+- Use modern C# syntax, but avoid features requiring types unavailable in older runtimes (e.g., no `ValueTuple` syntax for .NET Framework 4.6.1)
+- Prefer modern collection expressions (`[]`)
+- StyleCop: see `tracer/stylecop.json`; address warnings before pushing
+
+**C/C++ style:**
+- See `.clang-format`; keep consistent naming
 
 ## Logging Guidelines
 
@@ -242,157 +240,62 @@ Use clear, customer-facing terminology in log messages to avoid confusion. `Prof
 
 ## Performance Guidelines
 
-- Minimize heap allocations: The tracer runs in-process with customer applications and must have minimal performance impact. Avoid unnecessary object allocations, prefer value types where appropriate, use object pooling for frequently allocated objects, and cache reusable instances.
+The tracer runs in-process with customer applications and must have minimal performance impact.
 
-### Performance-Critical Code Paths
+**Critical code paths:**
+1. **Bootstrap/Startup Code**: Managed loader, tracer initialization, static constructors, configuration loading, integration registration
+2. **Hot Paths**: Span creation/tagging, context propagation, sampling decisions, instrumentation callbacks, request/response pipeline
 
-Performance is especially critical in two areas:
+**Key patterns:**
+- **Zero-Allocation Provider Structs**: Use `readonly struct` with generic type parameters and interface constraints to avoid boxing
+  - Example: `EnvironmentVariableProvider` in managed loader
+- **Avoid Allocation in Logging**: Use format strings (`Log("value: {0}", x)`) instead of interpolation (`Log($"value: {x}")`)
+- **Avoid params Array Allocations**: Provide overloads for common cases (0, 1, 2 args)
 
-1. **Bootstrap/Startup Code**: Initialization code runs at application startup in every instrumented process, including:
-   - The managed loader (`Datadog.Trace.ClrProfiler.Managed.Loader`)
-   - Tracer initialization in `Datadog.Trace` (static constructors, configuration loading, first tracer instance creation)
-   - Integration registration and setup
+## Testing
 
-   Any allocations or inefficiencies here directly impact application startup time and customer experience. This code must be extremely efficient.
+**Frameworks:** xUnit (managed), GoogleTest (native)
+**Test style:** Inline results in assertions: `SomeMethod().Should().Be(expected)`
+**Docker:** Many integration tests require Docker; services in `docker-compose.yml`
+**Filters:** `--filter "Category=Smoke"`, `--framework net6.0`
 
-2. **Hot Paths**: Code that executes frequently during application runtime, such as:
-   - Span creation and tagging (executes on every traced operation)
-   - Context propagation (executes on every HTTP request/response)
-   - Sampling decisions (executes on every trace)
-   - Integration instrumentation callbacks (executes on every instrumented method call)
-   - Any code in the request/response pipeline
-
-In these areas, even small inefficiencies are multiplied by the frequency of execution and can significantly impact application performance.
-
-### Performance Optimization Patterns
-
-**Zero-Allocation Provider Structs**
-- Use `readonly struct` implementing interfaces instead of classes for frequently-instantiated abstractions
-- Use generic type parameters with interface constraints to avoid boxing: `<TProvider> where TProvider : IProvider`
-- Example: `EnvironmentVariableProvider` in managed loader (see tracer/src/Datadog.Trace.ClrProfiler.Managed.Loader)
-- Benefits: Zero heap allocations, no boxing, better JIT optimization
-
-**Avoid Allocation in Logging**
-- Use format strings (`Log("value: {0}", x)`) instead of interpolation (`Log($"value: {x}")`)
-- Allows logger to check level before formatting
-- Critical in startup and hot paths where logging is frequent
-
-**Avoid params Array Allocations**
-- Provide overloads for common cases (0, 1, 2 args) that avoid `params object?[]` array allocation
-- Keep params overload as fallback for 3+ args
-- Example: Logging methods with multiple overloads for different argument counts
-
-## Testing Guidelines
-
-- Frameworks: xUnit (managed), GoogleTest (native).
-- Projects: `*.Tests.csproj` under `tracer/test`, native under `profiler/test`.
-- Filters: `--filter "Category=Smoke"`, `--framework net6.0` as needed.
-- Docker: Many integration tests require Docker; services in `docker-compose.yml`.
-- Test style: Inline result variables in assertions. Prefer `SomeMethod().Should().Be(expected)` over storing intermediate `result` variables.
-
-### Testing Patterns
-
-**Abstraction for Testability**
+**Testing patterns:**
 - Extract interfaces for environment/filesystem dependencies (e.g., `IEnvironmentVariableProvider`)
-- Allows mocking in unit tests without affecting production performance
 - Use struct implementations with generic constraints for zero-allocation production code
-- Example: Managed loader tests use `MockEnvironmentVariableProvider` for isolation (see tracer/test/Datadog.Trace.Tests/ClrProfiler/Managed/Loader/)
+- Example: Managed loader tests use `MockEnvironmentVariableProvider` (see `tracer/test/Datadog.Trace.Tests/ClrProfiler/Managed/Loader/`)
 
 ## Commit & Pull Request Guidelines
 
-- Commits: Imperative; optional scope tag (e.g., `fix(telemetry): …` or `[Debugger] …`); reference issues. Keep messages concise - avoid including full diffs or extensive details in the commit message.
-- PRs: Clear description, linked issues, risks/rollout, screenshots/logs if behavior changes.
-  - Follow the existing PR description template in `.github/pull_request_template.md`
-  - Keep descriptions concise - provide essential context without excessive detail
-  - Focus on "what" and "why", with brief "how" for complex changes
-- CI: All checks green; include tests/docs for changes.
-
-## Internal Docs & References
-
-- docs/README.md — Overview and links
-- docs/CONTRIBUTING.md — Contribution process
-- tracer/README.MD — Dev setup and targets
-- docs/development/AutomaticInstrumentation.md — Adding integrations
-- docs/development/DuckTyping.md — Duck typing guide
-- docs/development/CI/RunSmokeTestsLocally.md — Smoke tests locally
-- docs/development/UpdatingTheSdk.md — SDK updates
-- docs/RUNTIME_SUPPORT_POLICY.md — Supported runtimes
-
-## CallTarget Wiring
-
-- Define an integration class decorated with `InstrumentMethod` describing the target assembly/type/method, version range, and integration name. Example: `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/Couchbase/ClusterNodeIntegration.cs` and attribute API in `tracer/src/Datadog.Trace/ClrProfiler/InstrumentMethodAttribute.cs`.
-- Build collects attributes and generates native definitions used by the CLR profiler (see generator `tracer/build/_build/CodeGenerators/CallTargetsGenerator.cs`). This emits a C++ list (registered at startup) and a JSON snapshot.
-- Native CLR profiler (C++) registers those definitions and rewrites IL for matched methods during JIT/ReJIT to call the managed invoker.
-- The managed entry point is `CallTargetInvoker` (`tracer/src/Datadog.Trace/ClrProfiler/CallTarget/CallTargetInvoker.cs`). It invokes `OnMethodBegin` and `OnMethodEnd`/`OnAsyncMethodEnd` on your integration type, handling generics, ref/out, and async continuations.
-- `OnMethodBegin` returns `CallTargetState`, which can contain a tracing `Scope` to represent the span. That state flows to the end handler; async returns are awaited and then `OnAsyncMethodEnd` runs.
-- Integrations typically create a scope in `OnMethodBegin` and tag/finish it in the end handler. See the Couchbase example’s `OnMethodBegin`/`OnAsyncMethodEnd` methods.
-- Enable/disable per-integration via config (IntegrationName), and by framework/versions declared in the attribute.
-- For a full walkthrough and patterns, read `docs/development/AutomaticInstrumentation.md`.
-
-## Duck Typing Mechanism
-
-- Purpose: Interact with external types across versions without adding hard dependencies. Provides fast, strongly-typed access via generated proxies.
-- Shape interfaces: Define minimal contracts (properties/methods) you need, e.g., `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/AWS/Kinesis/IPutRecordsRequest.cs` and `IAmazonKinesisRequestWithStreamName.cs`.
-- Interface + IDuckType constraints: In CallTarget integrations, use `where TReq : IMyShape, IDuckType`. Example: `PutRecordsIntegration.OnMethodBegin` in `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/AWS/Kinesis/PutRecordsIntegration.cs`.
-- Creating proxies:
-  - Generic constraints (above) let the woven callsite pass a proxy automatically.
-  - At runtime by type: `DuckType.GetOrCreateProxyType(typeof(IMyShape), targetType)` and `CreateInstance(...)` (see `tracer/src/Datadog.Trace/OTelMetrics/OtlpMetricsExporter.cs`).
-  - From an instance: `obj.DuckCast<IMyShape>()` for nested values (see `GetRecordsIntegration` `DuckCast<IRecord>` in `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/AWS/Kinesis/GetRecordsIntegration.cs`).
-- Accessing originals: All proxies implement `IDuckType` (`tracer/src/Datadog.Trace/DuckTyping/IDuckType.cs`) exposing `Instance` and `Type`.
-- Binding rules: Name/signature matching; support for properties/fields/methods. Use attributes in `tracer/src/Datadog.Trace/DuckTyping/` to control binding:
-  - `[DuckField]`, `[DuckPropertyOrField]`, `[DuckIgnore]`, `[DuckInclude]`, `[DuckReverseMethod]`, `[DuckCopy]`, `[DuckAsClass]`, `[DuckType]`, `[DuckTypeTarget]`.
-- Visibility: Proxies can access non-public members; the library emits IL and uses `IgnoresAccessChecksToAttribute` if present (`tracer/src/Datadog.Trace/DuckTyping/IgnoresAccessChecksToAttribute.cs`).
-- Nullability/perf: Enable `#nullable` in new files; proxies are cached per (shape,target) for low overhead. See core implementation `tracer/src/Datadog.Trace/DuckTyping/DuckType.cs` and partials.
-- Guidance: Prefer interface shapes; avoid vendor types in signatures; check for `proxy.Instance != null` before use; keep shapes stable across upstream versions. Deep dive: `docs/development/DuckTyping.md`.
-
-## Integrations
-
-- Location: `tracer/src/Datadog.Trace/ClrProfiler/AutoInstrumentation/<Area>/<Integration>.cs`. Place shape interfaces and shared helpers in the same `<Area>` folder (e.g., `AWS/Kinesis/*`, `Couchbase/*`, `GraphQL/*`).
-- Create one
-  - Add shape interfaces for third‑party types you consume (no direct package refs).
-  - Add an integration class with one or more `InstrumentMethod` attributes specifying: `AssemblyName`, `TypeName`, `MethodName`, `ReturnTypeName`, `ParameterTypeNames`, `MinimumVersion`, `MaximumVersion`, `IntegrationName` (and `CallTargetIntegrationKind` if needed).
-  - Implement static handlers: `OnMethodBegin` returns `CallTargetState`; end handlers are `OnMethodEnd` for sync or `OnAsyncMethodEnd` for async. Use `Tracer.Instance` to create a `Scope`, tag it, and dispose in the end handler.
-  - Use duck typing in method generics: `where TReq : IMyShape, IDuckType` and `DuckCast<TShape>()` for nested members. Examples: `AWS/Kinesis/PutRecordsIntegration.cs`, `Couchbase/ClusterNodeIntegration.cs`.
-- Build/registration: Definitions are discovered and generated during build; no manual native changes required.
-- Tests: Add tests under `tracer/test/Datadog.Trace.ClrProfiler.IntegrationTests` and corresponding samples under `tracer/test/test-applications/integrations`. Run with OS‑specific Nuke targets; filter with `--filter`/`--framework`.
-
-## Azure Functions
-
-### Automatic Instrumentation Setup
-
-**Windows (Premium / Elastic Premium / Dedicated / App Services hosting plans)**
-- Use the Azure App Services Site Extension, not the NuGet package.
-
-**Other scenarios (e.g., Linux Consumption, Container Apps)**
-- Add NuGet package: `Datadog.AzureFunctions`
-- Configure environment variables:
-
-**Windows environment variables:**
-```
-CORECLR_ENABLE_PROFILING=1
-CORECLR_PROFILER={846F5F1C-F9AE-4B07-969E-05C26BC060D8}
-CORECLR_PROFILER_PATH_64=C:\home\site\wwwroot\datadog\win-x64\Datadog.Trace.ClrProfiler.Native.dll
-CORECLR_PROFILER_PATH_32=C:\home\site\wwwroot\datadog\win-x86\Datadog.Trace.ClrProfiler.Native.dll
-DD_DOTNET_TRACER_HOME=C:\home\site\wwwroot\datadog
-DOTNET_STARTUP_HOOKS=C:\home\site\wwwroot\Datadog.Serverless.Compat.dll
-```
-
-**Linux environment variables:**
-```
-CORECLR_ENABLE_PROFILING=1
-CORECLR_PROFILER={846F5F1C-F9AE-4B07-969E-05C26BC060D8}
-CORECLR_PROFILER_PATH=/home/site/wwwroot/datadog/linux-x64/Datadog.Trace.ClrProfiler.Native.so
-DD_DOTNET_TRACER_HOME=/home/site/wwwroot/datadog
-DOTNET_STARTUP_HOOKS=/home/site/wwwroot/Datadog.Serverless.Compat.dll
-```
-
-### Development & Testing
-
-- Integration details: See `docs/development/AzureFunctions.md` for in-process vs isolated worker model differences, instrumentation specifics, and ASP.NET Core integration.
-- Tests: `BuildAndRunWindowsAzureFunctionsTests` Nuke target; samples under `tracer/test/test-applications/azure-functions/`.
-- Dependencies: `Datadog.AzureFunctions` transitively references `Datadog.Serverless.Compat` ([datadog-serverless-compat-dotnet](https://github.com/DataDog/datadog-serverless-compat-dotnet)), which contains the Datadog Agent executable. The agent process is started either via `DOTNET_STARTUP_HOOKS` or by calling `Datadog.Serverless.CompatibilityLayer.Start()` explicitly during bootstrap in user code.
-
-## Security & Configuration Tips
+**Commits:**
+- Imperative mood; optional scope tag (e.g., `fix(telemetry): …` or `[Debugger] …`)
+- Reference issues when applicable
+- Keep messages concise - avoid full diffs or extensive details
+
+**Pull Requests:**
+- Follow `.github/pull_request_template.md`
+- Clear description, linked issues, risks/rollout notes
+- Keep concise - essential context without excessive detail
+- Focus on "what" and "why", brief "how" for complex changes
+- Include tests/docs for changes
+- CI: All checks must pass
+
+## Documentation References
+
+**Core docs:**
+- `docs/README.md` — Overview and links
+- `docs/CONTRIBUTING.md` — Contribution process and external PR policies
+- `tracer/README.MD` — Dev setup, platform requirements, and build targets
+- `docs/RUNTIME_SUPPORT_POLICY.md` — Supported runtimes
+
+**Development guides:**
+- `docs/development/AutomaticInstrumentation.md` — Creating integrations
+- `docs/development/DuckTyping.md` — Duck typing guide
+- `docs/development/AzureFunctions.md` — Azure Functions integration
+- `docs/development/Serverless.md` — Serverless instrumentation
+- `docs/development/UpdatingTheSdk.md` — SDK updates
+- `docs/development/CI/RunSmokeTestsLocally.md` — Running smoke tests locally
+
+## Security & Configuration
 
 - Do not commit secrets; prefer env vars (`DD_*`). `.env` should not contain credentials.
 - Use `global.json` SDK; confirm with `dotnet --version`.
PATCH

echo "Gold patch applied."
