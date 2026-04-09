#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17275
cat <<'PATCH' | git apply -
diff --git a/dotnet/test/support/AssemblyFixture.cs b/dotnet/test/support/AssemblyFixture.cs
new file mode 100644
index 0000000000000..ba9c93fee50f5
--- /dev/null
+++ b/dotnet/test/support/AssemblyFixture.cs
@@ -0,0 +1,55 @@
+// <copyright file="AssemblyFixture.cs" company="Selenium Committers">
+// Licensed to the Software Freedom Conservancy (SFC) under one
+// or more contributor license agreements.  See the NOTICE file
+// distributed with this work for additional information
+// regarding copyright ownership.  The SFC licenses this file
+// to you under the Apache License, Version 2.0 (the
+// "License"); you may not use this file except in compliance
+// with the License.  You may obtain a copy of the License at
+//
+//   http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing,
+// software distributed under the License is distributed on an
+// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+// KIND, either express or implied.  See the License for the
+// specific language governing permissions and limitations
+// under the License.
+// </copyright>
+
+using System.Threading.Tasks;
+using NUnit.Framework;
+using OpenQA.Selenium.Environment;
+
+namespace OpenQA.Selenium.Support;
+
+[SetUpFixture]
+public class AssemblyFixture
+{
+    public AssemblyFixture()
+    {
+    }
+
+    [OneTimeSetUp]
+    public async Task RunBeforeAnyTestAsync()
+    {
+        Internal.Logging.Log.SetLevel(Internal.Logging.LogEventLevel.Trace);
+
+        await EnvironmentManager.Instance.WebServer.StartAsync();
+        if (EnvironmentManager.Instance.Browser == Browser.Remote)
+        {
+            await EnvironmentManager.Instance.RemoteServer.StartAsync();
+        }
+    }
+
+    [OneTimeTearDown]
+    public async Task RunAfterAnyTestsAsync()
+    {
+        EnvironmentManager.Instance.CloseCurrentDriver();
+        await EnvironmentManager.Instance.WebServer.StopAsync();
+        if (EnvironmentManager.Instance.Browser == Browser.Remote)
+        {
+            await EnvironmentManager.Instance.RemoteServer.StopAsync();
+        }
+    }
+}
diff --git a/dotnet/test/support/UI/PopupWindowFinderTests.cs b/dotnet/test/support/UI/PopupWindowFinderTests.cs
index faf7a595da985..e65012ea09b2a 100644
--- a/dotnet/test/support/UI/PopupWindowFinderTests.cs
+++ b/dotnet/test/support/UI/PopupWindowFinderTests.cs
@@ -17,29 +17,13 @@
 // under the License.
 // </copyright>

-using System.Threading.Tasks;
 using NUnit.Framework;
-using OpenQA.Selenium.Environment;

 namespace OpenQA.Selenium.Support.UI;

 [TestFixture]
 public class PopupWindowFinderTests : DriverTestFixture
 {
-    //TODO: Move these to a standalone class when more tests rely on the server being up
-    [OneTimeSetUp]
-    public async Task RunBeforeAnyTestAsync()
-    {
-        await EnvironmentManager.Instance.WebServer.StartAsync();
-    }
-
-    [OneTimeTearDown]
-    public async Task RunAfterAnyTestsAsync()
-    {
-        EnvironmentManager.Instance.CloseCurrentDriver();
-        await EnvironmentManager.Instance.WebServer.StopAsync();
-    }
-
     [Test]
     public void ShouldFindPopupWindowUsingAction()
     {
diff --git a/dotnet/test/support/UI/SelectBrowserTests.cs b/dotnet/test/support/UI/SelectBrowserTests.cs
index ad7c7a08e0f4e..055195263f156 100644
--- a/dotnet/test/support/UI/SelectBrowserTests.cs
+++ b/dotnet/test/support/UI/SelectBrowserTests.cs
@@ -19,28 +19,13 @@

 using System;
 using System.Collections.Generic;
-using System.Threading.Tasks;
 using NUnit.Framework;
-using OpenQA.Selenium.Environment;

 namespace OpenQA.Selenium.Support.UI;

 [TestFixture]
 public class SelectBrowserTests : DriverTestFixture
 {
-    [OneTimeSetUp]
-    public async Task RunBeforeAnyTestAsync()
-    {
-        await EnvironmentManager.Instance.WebServer.StartAsync();
-    }
-
-    [OneTimeTearDown]
-    public async Task RunAfterAnyTestsAsync()
-    {
-        EnvironmentManager.Instance.CloseCurrentDriver();
-        await EnvironmentManager.Instance.WebServer.StopAsync();
-    }
-
     [SetUp]
     public void Setup()
     {
PATCH

# Verify the patch was applied by checking for a distinctive line
grep -q "class AssemblyFixture" dotnet/test/support/AssemblyFixture.cs && echo "Patch applied successfully"
