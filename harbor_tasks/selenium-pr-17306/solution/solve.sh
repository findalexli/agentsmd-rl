#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if patch already applied
if grep -q "public abstract class Command<TParameters, TResult>" dotnet/src/webdriver/BiDi/Command.cs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/dotnet/src/webdriver/BUILD.bazel b/dotnet/src/webdriver/BUILD.bazel
index 65f32ecbd81d8..267059219c6f0 100644
--- a/dotnet/src/webdriver/BUILD.bazel
+++ b/dotnet/src/webdriver/BUILD.bazel
@@ -48,9 +48,6 @@ csharp_library(
         "**/*.cs",
     ]) + ["//dotnet/src/webdriver/DevTools:srcs"] + devtools_version_targets(),
     out = "WebDriver",
-    internals_visible_to = [
-        "WebDriver.Tests",
-    ],
     langversion = "14.0",
     nullable = "enable",
     target_frameworks = [
@@ -81,9 +78,6 @@ csharp_library(
         "**/*.cs",
     ]) + ["//dotnet/src/webdriver/DevTools:srcs"] + devtools_version_targets(),
     out = "WebDriver",
-    internals_visible_to = [
-        "WebDriver.Tests",
-    ],
     langversion = "14.0",
     nullable = "enable",
     resources = [],
@@ -118,9 +112,6 @@ csharp_library(
     defines = [
         "NET8_0_OR_GREATER",
     ],
-    internals_visible_to = [
-        "WebDriver.Tests",
-    ],
     langversion = "14.0",
     nullable = "enable",
     resources = [],
diff --git a/dotnet/src/webdriver/BiDi/Command.cs b/dotnet/src/webdriver/BiDi/Command.cs
index 43ffb9212a4d5..edd887fdc6aaa 100644
--- a/dotnet/src/webdriver/BiDi/Command.cs
+++ b/dotnet/src/webdriver/BiDi/Command.cs
@@ -35,7 +35,7 @@ protected Command(string method)
     public long Id { get; internal set; }
 }

-internal abstract class Command<TParameters, TResult>(TParameters @params, string method) : Command(method)
+public abstract class Command<TParameters, TResult>(TParameters @params, string method) : Command(method)
     where TParameters : Parameters
     where TResult : EmptyResult
 {
@@ -43,7 +43,7 @@ internal abstract class Command<TParameters, TResult>(TParameters @params, strin
     public TParameters Params { get; } = @params;
 }

-internal record Parameters
+public record Parameters
 {
     public static Parameters Empty { get; } = new Parameters();
 }
diff --git a/dotnet/src/webdriver/Internal/Logging/ILogContext.cs b/dotnet/src/webdriver/Internal/Logging/ILogContext.cs
index 51ec04bbae93f..3d3dd26df3a9e 100644
--- a/dotnet/src/webdriver/Internal/Logging/ILogContext.cs
+++ b/dotnet/src/webdriver/Internal/Logging/ILogContext.cs
@@ -42,14 +42,14 @@ public interface ILogContext : IDisposable
     /// </summary>
     /// <typeparam name="T">The type for which to retrieve the logger.</typeparam>
     /// <returns>An instance of <see cref="ILogger"/> for the specified type.</returns>
-    internal ILogger GetLogger<T>();
+    ILogger GetLogger<T>();

     /// <summary>
     /// Gets a logger for the specified type.
     /// </summary>
     /// <param name="type">The type for which to retrieve the logger.</param>
     /// <returns>An instance of <see cref="ILogger"/> for the specified type.</returns>
-    internal ILogger GetLogger(Type type);
+    ILogger GetLogger(Type type);

     /// <summary>
     /// Checks whether logs emitting is enabled for a logger and a log event level.
diff --git a/dotnet/src/webdriver/Internal/Logging/ILogger.cs b/dotnet/src/webdriver/Internal/Logging/ILogger.cs
index 9408e92660bf6..26732f5a4d47c 100644
--- a/dotnet/src/webdriver/Internal/Logging/ILogger.cs
+++ b/dotnet/src/webdriver/Internal/Logging/ILogger.cs
@@ -22,7 +22,7 @@ namespace OpenQA.Selenium.Internal.Logging;
 /// <summary>
 /// Defines the interface through which log messages are emitted.
 /// </summary>
-internal interface ILogger
+public interface ILogger
 {
     /// <summary>
     /// Writes a trace-level log message.
diff --git a/dotnet/src/webdriver/Internal/Logging/Log.cs b/dotnet/src/webdriver/Internal/Logging/Log.cs
index 4a359ac911c35..7cf65e5b6f119 100644
--- a/dotnet/src/webdriver/Internal/Logging/Log.cs
+++ b/dotnet/src/webdriver/Internal/Logging/Log.cs
@@ -66,7 +66,7 @@ public static ILogContext CreateContext(LogEventLevel minimumLevel)
     /// Gets or sets the current log context.
     /// </summary>
     [AllowNull]
-    internal static ILogContext CurrentContext
+    public static ILogContext CurrentContext
     {
         get => _logContextManager.CurrentContext;
         set => _logContextManager.CurrentContext = value;
@@ -77,7 +77,7 @@ internal static ILogContext CurrentContext
     /// </summary>
     /// <typeparam name="T">The type to get the logger for.</typeparam>
     /// <returns>The logger.</returns>
-    internal static ILogger GetLogger<T>()
+    public static ILogger GetLogger<T>()
     {
         return _logContextManager.CurrentContext.GetLogger<T>();
     }
@@ -87,7 +87,7 @@ internal static ILogger GetLogger<T>()
     /// </summary>
     /// <param name="type">The type to get the logger for.</param>
     /// <returns>The logger.</returns>
-    internal static ILogger GetLogger(Type type)
+    public static ILogger GetLogger(Type type)
     {
         return _logContextManager.CurrentContext.GetLogger(type);
     }
diff --git a/dotnet/src/webdriver/Selenium.WebDriver.csproj b/dotnet/src/webdriver/Selenium.WebDriver.csproj
index 2f12e00ab7a95..af1c4d0504340 100644
--- a/dotnet/src/webdriver/Selenium.WebDriver.csproj
+++ b/dotnet/src/webdriver/Selenium.WebDriver.csproj
@@ -52,10 +52,6 @@
     <IsAotCompatible>true</IsAotCompatible>
   </PropertyGroup>-->

-  <ItemGroup>
-    <InternalsVisibleTo Include="WebDriver.Tests" />
-  </ItemGroup>
-
   <ItemGroup Condition=" '$(TargetFramework)' == 'net462' or '$(TargetFramework)' == 'netstandard2.0'">
     <PackageReference Include="System.Text.Json" Version="8.0.5" />
     <PackageReference Include="System.Threading.Channels" Version="8.0.0" />
PATCH

echo "Gold patch applied successfully."
