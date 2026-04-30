#!/bin/bash
set -e

cd /workspace/selenium

# Check if already patched (idempotency check)
if grep -q "private readonly Lazy<V143Network> network" dotnet/src/webdriver/DevTools/v143/V143Domains.cs; then
    echo "Already patched, skipping"
    exit 0
fi

# Apply the gold patch for CDP domain lifecycle fix
cat <<'PATCH' | git apply -
diff --git a/dotnet/src/webdriver/DevTools/v143/V143Domains.cs b/dotnet/src/webdriver/DevTools/v143/V143Domains.cs
index 93b1bd51cd426..d402f2d79f817 100644
--- a/dotnet/src/webdriver/DevTools/v143/V143Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v143/V143Domains.cs
@@ -25,6 +25,10 @@ namespace OpenQA.Selenium.DevTools.V143;
 public class V143Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V143Network> network;
+    private readonly Lazy<V143JavaScript> javaScript;
+    private readonly Lazy<V143Target> target;
+    private readonly Lazy<V143Log> log;

     /// <summary>
     /// Initializes a new instance of the V143Domains class.
@@ -34,6 +38,10 @@ public class V143Domains : DevToolsDomains
     public V143Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V143Network>(() => new V143Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V143JavaScript>(() => new V143JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V143Target>(() => new V143Target(domains.Target));
+        this.log = new Lazy<V143Log>(() => new V143Log(domains.Log));
     }

     /// <summary>
@@ -49,20 +57,20 @@ public class V143Domains : DevToolsDomains
     /// <summary>
     /// Gets the object used for manipulating network information in the browser.
     /// </summary>
-    public override DevTools.Network Network => new V143Network(domains.Network, domains.Fetch);
+    public override DevTools.Network Network => this.network.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's JavaScript execution.
     /// </summary>
-    public override JavaScript JavaScript => new V143JavaScript(domains.Runtime, domains.Page);
+    public override JavaScript JavaScript => this.javaScript.Value;

     /// <summary>
     /// Gets the object used for manipulating DevTools Protocol targets.
     /// </summary>
-    public override DevTools.Target Target => new V143Target(domains.Target);
+    public override DevTools.Target Target => this.target.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's logs.
     /// </summary>
-    public override DevTools.Log Log => new V143Log(domains.Log);
+    public override DevTools.Log Log => this.log.Value;
 }
diff --git a/dotnet/src/webdriver/DevTools/v144/V144Domains.cs b/dotnet/src/webdriver/DevTools/v144/V144Domains.cs
index 989178ce71ab8..e7dd4fcb8c392 100644
--- a/dotnet/src/webdriver/DevTools/v144/V144Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v144/V144Domains.cs
@@ -25,6 +25,10 @@ namespace OpenQA.Selenium.DevTools.V144;
 public class V144Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V144Network> network;
+    private readonly Lazy<V144JavaScript> javaScript;
+    private readonly Lazy<V144Target> target;
+    private readonly Lazy<V144Log> log;

     /// <summary>
     /// Initializes a new instance of the V144Domains class.
@@ -34,6 +38,10 @@ public class V144Domains : DevToolsDomains
     public V144Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V144Network>(() => new V144Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V144JavaScript>(() => new V144JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V144Target>(() => new V144Target(domains.Target));
+        this.log = new Lazy<V144Log>(() => new V144Log(domains.Log));
     }

     /// <summary>
@@ -49,20 +57,20 @@ public class V144Domains : DevToolsDomains
     /// <summary>
     /// Gets the object used for manipulating network information in the browser.
     /// </summary>
-    public override DevTools.Network Network => new V144Network(domains.Network, domains.Fetch);
+    public override DevTools.Network Network => this.network.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's JavaScript execution.
     /// </summary>
-    public override JavaScript JavaScript => new V144JavaScript(domains.Runtime, domains.Page);
+    public override JavaScript JavaScript => this.javaScript.Value;

     /// <summary>
     /// Gets the object used for manipulating DevTools Protocol targets.
     /// </summary>
-    public override DevTools.Target Target => new V144Target(domains.Target);
+    public override DevTools.Target Target => this.target.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's logs.
     /// </summary>
-    public override DevTools.Log Log => new V144Log(domains.Log);
+    public override DevTools.Log Log => this.log.Value;
 }
diff --git a/dotnet/src/webdriver/DevTools/v145/V145Domains.cs b/dotnet/src/webdriver/DevTools/v145/V145Domains.cs
index 9d5b22a889bba..333f047ed2757 100644
--- a/dotnet/src/webdriver/DevTools/v145/V145Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v145/V145Domains.cs
@@ -25,6 +25,10 @@ namespace OpenQA.Selenium.DevTools.V145;
 public class V145Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V145Network> network;
+    private readonly Lazy<V145JavaScript> javaScript;
+    private readonly Lazy<V145Target> target;
+    private readonly Lazy<V145Log> log;

     /// <summary>
     /// Initializes a new instance of the V145Domains class.
@@ -34,6 +38,10 @@ public class V145Domains : DevToolsDomains
     public V145Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V145Network>(() => new V145Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V145JavaScript>(() => new V145JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V145Target>(() => new V145Target(domains.Target));
+        this.log = new Lazy<V145Log>(() => new V145Log(domains.Log));
     }

     /// <summary>
@@ -49,20 +57,20 @@ public class V145Domains : DevToolsDomains
     /// <summary>
     /// Gets the object used for manipulating network information in the browser.
     /// </summary>
-    public override DevTools.Network Network => new V145Network(domains.Network, domains.Fetch);
+    public override DevTools.Network Network => this.network.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's JavaScript execution.
     /// </summary>
-    public override JavaScript JavaScript => new V145JavaScript(domains.Runtime, domains.Page);
+    public override JavaScript JavaScript => this.javaScript.Value;

     /// <summary>
     /// Gets the object used for manipulating DevTools Protocol targets.
     /// </summary>
-    public override DevTools.Target Target => new V145Target(domains.Target);
+    public override DevTools.Target Target => this.target.Value;

     /// <summary>
     /// Gets the object used for manipulating the browser's logs.
     /// </summary>
-    public override DevTools.Log Log => new V145Log(domains.Log);
+    public override DevTools.Log Log => this.log.Value;
 }
diff --git a/dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs b/dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs
new file mode 100644
index 0000000000000..280e73b145321
--- /dev/null
+++ b/dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs
@@ -0,0 +1,41 @@
+// <copyright file="DevToolsDomainsTests.cs" company="Selenium Committers">
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
+using OpenQA.Selenium.DevTools;
+
+namespace OpenQA.Selenium.Tests.DevTools;
+
+[TestFixture]
+public class DevToolsDomainsTests : DevToolsTestFixture
+{
+    [Test]
+    [IgnoreBrowser(Browser.IE, "IE does not support Chrome DevTools Protocol")]
+    [IgnoreBrowser(Browser.Firefox, "Firefox does not support Chrome DevTools Protocol")]
+    [IgnoreBrowser(Browser.Safari, "Safari does not support Chrome DevTools Protocol")]
+    [IgnoreBrowser(Browser.Edge, "We run it in Chrome and Edge releases are usually late.")]
+    public async Task VerifyVersionSpecificDomainsAccessors()
+    {
+        var domains = ((DevToolsSession)session).Domains;
+
+        Assert.That(domains.Log, Is.SameAs(domains.Log));
+        Assert.That(domains.Network, Is.SameAs(domains.Network));
+        Assert.That(domains.Target, Is.SameAs(domains.Target));
+        Assert.That(domains.JavaScript, Is.SameAs(domains.JavaScript));
+    }
+}
PATCH

echo "Patch applied successfully"
