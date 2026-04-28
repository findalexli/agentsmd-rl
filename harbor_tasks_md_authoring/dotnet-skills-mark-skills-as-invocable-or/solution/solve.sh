#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "invocable: false" "skills/akka/aspire-configuration/SKILL.md" && grep -qF "invocable: false" "skills/akka/best-practices/SKILL.md" && grep -qF "invocable: false" "skills/akka/hosting-actor-patterns/SKILL.md" && grep -qF "invocable: false" "skills/akka/management/SKILL.md" && grep -qF "invocable: false" "skills/akka/testing-patterns/SKILL.md" && grep -qF "invocable: false" "skills/aspire/integration-testing/SKILL.md" && grep -qF "invocable: false" "skills/aspire/service-defaults/SKILL.md" && grep -qF "invocable: false" "skills/aspnetcore/transactional-emails/SKILL.md" && grep -qF "invocable: false" "skills/csharp/api-design/SKILL.md" && grep -qF "invocable: false" "skills/csharp/coding-standards/SKILL.md" && grep -qF "invocable: false" "skills/csharp/concurrency-patterns/SKILL.md" && grep -qF "invocable: false" "skills/csharp/type-design-performance/SKILL.md" && grep -qF "invocable: false" "skills/data/database-performance/SKILL.md" && grep -qF "invocable: false" "skills/data/efcore-patterns/SKILL.md" && grep -qF "invocable: false" "skills/dotnet/local-tools/SKILL.md" && grep -qF "invocable: false" "skills/dotnet/package-management/SKILL.md" && grep -qF "invocable: false" "skills/dotnet/project-structure/SKILL.md" && grep -qF "invocable: false" "skills/dotnet/serialization/SKILL.md" && grep -qF "invocable: true" "skills/dotnet/slopwatch/SKILL.md" && grep -qF "invocable: true" "skills/meta/marketplace-publishing/SKILL.md" && grep -qF "invocable: false" "skills/meta/skills-index-snippets/SKILL.md" && grep -qF "invocable: false" "skills/microsoft-extensions/configuration/SKILL.md" && grep -qF "invocable: false" "skills/microsoft-extensions/dependency-injection/SKILL.md" && grep -qF "invocable: false" "skills/playwright/ci-caching/SKILL.md" && grep -qF "invocable: true" "skills/testing/crap-analysis/SKILL.md" && grep -qF "invocable: false" "skills/testing/playwright-blazor/SKILL.md" && grep -qF "invocable: false" "skills/testing/snapshot-testing/SKILL.md" && grep -qF "invocable: false" "skills/testing/testcontainers/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/akka/aspire-configuration/SKILL.md b/skills/akka/aspire-configuration/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: akka-net-aspire-configuration
 description: Configure Akka.NET with .NET Aspire for local development and production deployments. Covers actor system setup, clustering, persistence, Akka.Management integration, and Aspire orchestration patterns.
+invocable: false
 ---
 
 # Configuring Akka.NET with .NET Aspire
diff --git a/skills/akka/best-practices/SKILL.md b/skills/akka/best-practices/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: akka-net-best-practices
 description: Critical Akka.NET best practices including EventStream vs DistributedPubSub, supervision strategies, error handling, Props vs DependencyResolver, work distribution patterns, and cluster/local mode abstractions for testability.
+invocable: false
 ---
 
 # Akka.NET Best Practices
diff --git a/skills/akka/hosting-actor-patterns/SKILL.md b/skills/akka/hosting-actor-patterns/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: akka-hosting-actor-patterns
 description: Patterns for building entity actors with Akka.Hosting - GenericChildPerEntityParent, message extractors, cluster sharding abstraction, akka-reminders, and ITimeProvider. Supports both local testing and clustered production modes.
+invocable: false
 ---
 
 # Akka.Hosting Actor Patterns
diff --git a/skills/akka/management/SKILL.md b/skills/akka/management/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: akka-net-management
 description: Akka.Management for cluster bootstrapping, service discovery (Kubernetes, Azure, Config), health checks, and dynamic cluster formation without static seed nodes.
+invocable: false
 ---
 
 # Akka.NET Management and Service Discovery
diff --git a/skills/akka/testing-patterns/SKILL.md b/skills/akka/testing-patterns/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: akka-net-testing-patterns
 description: Write unit and integration tests for Akka.NET actors using modern Akka.Hosting.TestKit patterns. Covers dependency injection, TestProbes, persistence testing, and actor interaction verification. Includes guidance on when to use traditional TestKit.
+invocable: false
 ---
 
 # Akka.NET Testing Patterns
diff --git a/skills/aspire/integration-testing/SKILL.md b/skills/aspire/integration-testing/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: aspire-integration-testing
 description: Write integration tests using .NET Aspire's testing facilities with xUnit. Covers test fixtures, distributed application setup, endpoint discovery, and patterns for testing ASP.NET Core apps with real dependencies.
+invocable: false
 ---
 
 # Integration Testing with .NET Aspire + xUnit
diff --git a/skills/aspire/service-defaults/SKILL.md b/skills/aspire/service-defaults/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: aspire-service-defaults
 description: Create a shared ServiceDefaults project for Aspire applications. Centralizes OpenTelemetry, health checks, resilience, and service discovery configuration across all services.
+invocable: false
 ---
 
 # Aspire Service Defaults
diff --git a/skills/aspnetcore/transactional-emails/SKILL.md b/skills/aspnetcore/transactional-emails/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: transactional-emails
 description: Build transactional emails using MJML templates with variable substitution. Render responsive HTML that works across email clients. Test with Mailpit/Mailhog in development via Aspire.
+invocable: false
 ---
 
 # Transactional Emails with MJML
diff --git a/skills/csharp/api-design/SKILL.md b/skills/csharp/api-design/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: api-design
 description: Design stable, compatible public APIs using extend-only design principles. Manage API compatibility, wire compatibility, and versioning for NuGet packages and distributed systems.
+invocable: false
 ---
 
 # Public API Design and Compatibility
diff --git a/skills/csharp/coding-standards/SKILL.md b/skills/csharp/coding-standards/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: modern-csharp-coding-standards
 description: Write modern, high-performance C# code using records, pattern matching, value objects, async/await, Span<T>/Memory<T>, and best-practice API design patterns. Emphasizes functional-style programming with C# 12+ features.
+invocable: false
 ---
 
 # Modern C# Coding Standards
diff --git a/skills/csharp/concurrency-patterns/SKILL.md b/skills/csharp/concurrency-patterns/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: csharp-concurrency-patterns
 description: Choosing the right concurrency abstraction in .NET - from async/await for I/O to Channels for producer/consumer to Akka.NET for stateful entity management. Avoid locks and manual synchronization unless absolutely necessary.
+invocable: false
 ---
 
 # .NET Concurrency: Choosing the Right Tool
diff --git a/skills/csharp/type-design-performance/SKILL.md b/skills/csharp/type-design-performance/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: type-design-performance
 description: Design .NET types for performance. Seal classes, use readonly structs, prefer static pure functions, avoid premature enumeration, and choose the right collection types.
+invocable: false
 ---
 
 # Type Design for Performance
diff --git a/skills/data/database-performance/SKILL.md b/skills/data/database-performance/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: database-performance
 description: Database access patterns for performance. Separate read/write models, avoid N+1 queries, use AsNoTracking, apply row limits, and never do application-side joins. Works with EF Core and Dapper.
+invocable: false
 ---
 
 # Database Performance Patterns
diff --git a/skills/data/efcore-patterns/SKILL.md b/skills/data/efcore-patterns/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: efcore-patterns
 description: Entity Framework Core best practices including NoTracking by default, query splitting for navigation collections, migration management, dedicated migration services, and common pitfalls to avoid.
+invocable: false
 ---
 
 # Entity Framework Core Patterns
diff --git a/skills/dotnet/local-tools/SKILL.md b/skills/dotnet/local-tools/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: dotnet-local-tools
 description: Managing local .NET tools with dotnet-tools.json for consistent tooling across development environments and CI/CD pipelines.
+invocable: false
 ---
 
 # .NET Local Tools
diff --git a/skills/dotnet/package-management/SKILL.md b/skills/dotnet/package-management/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: package-management
 description: Manage NuGet packages using Central Package Management (CPM) and dotnet CLI commands. Never edit XML directly - use dotnet add/remove/list commands. Use shared version variables for related packages.
+invocable: false
 ---
 
 # NuGet Package Management
diff --git a/skills/dotnet/project-structure/SKILL.md b/skills/dotnet/project-structure/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: dotnet-project-structure
 description: Modern .NET project structure including .slnx solution format, Directory.Build.props, central package management, SourceLink, version management with RELEASE_NOTES.md, and SDK pinning with global.json.
+invocable: false
 ---
 
 # .NET Project Structure and Build Configuration
diff --git a/skills/dotnet/serialization/SKILL.md b/skills/dotnet/serialization/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: serialization
 description: Choose the right serialization format for .NET applications. Prefer schema-based formats (Protobuf, MessagePack) over reflection-based (Newtonsoft.Json). Use System.Text.Json with AOT source generators for JSON scenarios.
+invocable: false
 ---
 
 # Serialization in .NET
diff --git a/skills/dotnet/slopwatch/SKILL.md b/skills/dotnet/slopwatch/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: dotnet-slopwatch
 description: Use Slopwatch to detect LLM reward hacking in .NET code changes. Run after every code modification to catch disabled tests, suppressed warnings, empty catch blocks, and other shortcuts that mask real problems.
+invocable: true
 ---
 
 # Slopwatch: LLM Anti-Cheat for .NET
diff --git a/skills/meta/marketplace-publishing/SKILL.md b/skills/meta/marketplace-publishing/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: marketplace-publishing
 description: Workflow for publishing skills and agents to the dotnet-skills Claude Code marketplace. Covers adding new content, updating plugin.json, validation, and release tagging.
+invocable: true
 ---
 
 # Marketplace Publishing Workflow
diff --git a/skills/meta/skills-index-snippets/SKILL.md b/skills/meta/skills-index-snippets/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: skills-index-snippets
 description: Create and maintain AGENTS.md / CLAUDE.md snippet indexes that route tasks to the correct dotnet-skills skills and agents (including compressed Vercel-style indexes).
+invocable: false
 ---
 
 # Maintaining Skill Index Snippets (AGENTS.md / CLAUDE.md)
diff --git a/skills/microsoft-extensions/configuration/SKILL.md b/skills/microsoft-extensions/configuration/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: microsoft-extensions-configuration
 description: Microsoft.Extensions.Options patterns including IValidateOptions, strongly-typed settings, validation on startup, and the Options pattern for clean configuration management.
+invocable: false
 ---
 
 # Microsoft.Extensions Configuration Patterns
diff --git a/skills/microsoft-extensions/dependency-injection/SKILL.md b/skills/microsoft-extensions/dependency-injection/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: dependency-injection-patterns
 description: Organize DI registrations using IServiceCollection extension methods. Group related services into composable Add* methods for clean Program.cs and reusable configuration in tests.
+invocable: false
 ---
 
 # Dependency Injection Patterns
diff --git a/skills/playwright/ci-caching/SKILL.md b/skills/playwright/ci-caching/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: playwright-ci-caching
 description: Cache Playwright browser binaries in CI/CD pipelines (GitHub Actions, Azure DevOps) to avoid 1-2 minute download overhead on every build.
+invocable: false
 ---
 
 # Caching Playwright Browsers in CI/CD
diff --git a/skills/testing/crap-analysis/SKILL.md b/skills/testing/crap-analysis/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: crap-analysis
 description: Analyze code coverage and CRAP (Change Risk Anti-Patterns) scores to identify high-risk code. Use OpenCover format with ReportGenerator for Risk Hotspots showing cyclomatic complexity and untested code paths.
+invocable: true
 ---
 
 # CRAP Score Analysis
diff --git a/skills/testing/playwright-blazor/SKILL.md b/skills/testing/playwright-blazor/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: playwright-blazor-testing
 description: Write UI tests for Blazor applications (Server or WebAssembly) using Playwright. Covers navigation, interaction, authentication, selectors, and common Blazor-specific patterns.
+invocable: false
 ---
 
 # Testing Blazor Applications with Playwright
diff --git a/skills/testing/snapshot-testing/SKILL.md b/skills/testing/snapshot-testing/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: snapshot-testing
 description: Use Verify for snapshot testing in .NET. Approve API surfaces, HTTP responses, rendered emails, and serialized outputs. Detect unintended changes through human-reviewed baseline files.
+invocable: false
 ---
 
 # Snapshot Testing with Verify
diff --git a/skills/testing/testcontainers/SKILL.md b/skills/testing/testcontainers/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: testcontainers-integration-tests
 description: Write integration tests using TestContainers for .NET with xUnit. Covers infrastructure testing with real databases, message queues, and caches in Docker containers instead of mocks.
+invocable: false
 ---
 
 # Integration Testing with TestContainers
PATCH

echo "Gold patch applied."
