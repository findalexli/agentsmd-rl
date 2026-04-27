#!/usr/bin/env bash
# Apply the gold patch from PR SeleniumHQ/selenium#17103.
#
# This script is run by the harness AFTER the agent's solution attempt to
# produce a "gold" reference image for validation. It must NOT fetch from
# the network; the patch is inlined as a HEREDOC.
set -euo pipefail

cd /workspace/selenium

# Idempotency: if the gold patch is already applied, skip.
if grep -q '\[Obsolete("This interface is no longer supported and will be removed in a future release (4.43)."\)\]' \
        dotnet/src/webdriver/Remote/ICommandServer.cs 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/dotnet/src/webdriver/DriverService.cs b/dotnet/src/webdriver/DriverService.cs
index df43fe2db85d6..f91629675b63c 100644
--- a/dotnet/src/webdriver/DriverService.cs
+++ b/dotnet/src/webdriver/DriverService.cs
@@ -21,21 +21,17 @@
 using System.Diagnostics.CodeAnalysis;
 using System.Globalization;
 using System.Net;
-using OpenQA.Selenium.Internal.Logging;
-using OpenQA.Selenium.Remote;

 namespace OpenQA.Selenium;

 /// <summary>
 /// Exposes the service provided by a native WebDriver server executable.
 /// </summary>
-public abstract class DriverService : ICommandServer
+public abstract class DriverService : IDisposable
 {
     private bool isDisposed;
     private Process? driverServiceProcess;

-    private static readonly ILogger _logger = Log.GetLogger(typeof(DriverService));
-
     /// <summary>
     /// Initializes a new instance of the <see cref="DriverService"/> class.
     /// </summary>
diff --git a/dotnet/src/webdriver/Remote/ICommandServer.cs b/dotnet/src/webdriver/Remote/ICommandServer.cs
index 56127603da958..5db2e6029d3b8 100644
--- a/dotnet/src/webdriver/Remote/ICommandServer.cs
+++ b/dotnet/src/webdriver/Remote/ICommandServer.cs
@@ -22,6 +22,7 @@ namespace OpenQA.Selenium.Remote;
 /// <summary>
 /// Provides a way to start a server that understands remote commands
 /// </summary>
+[Obsolete("This interface is no longer supported and will be removed in a future release (4.43).")]
 public interface ICommandServer : IDisposable
 {
     /// <summary>
PATCH

echo "Gold patch applied."
