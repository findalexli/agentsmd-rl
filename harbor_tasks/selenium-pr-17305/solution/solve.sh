#!/bin/bash
# Gold solution for selenium-dotnet-cdp-lazy-init
set -e

cd /workspace/selenium

# Check if already applied (idempotency)
if grep -q "private readonly Lazy<V143Network> network;" dotnet/src/webdriver/DevTools/v143/V143Domains.cs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply patch to V143Domains.cs
patch -p1 <<'PATCH_V143'
--- a/dotnet/src/webdriver/DevTools/v143/V143Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v143/V143Domains.cs
@@ -24,6 +24,10 @@ namespace OpenQA.Selenium.DevTools.V143;
 public class V143Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V143Network> network;
+    private readonly Lazy<V143JavaScript> javaScript;
+    private readonly Lazy<V143Target> target;
+    private readonly Lazy<V143Log> log;

     /// <summary>
     /// Initializes a new instance of the V143Domains class.
@@ -33,6 +37,10 @@ public class V143Domains : DevToolsDomains
     public V143Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V143Network>(() => new V143Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V143JavaScript>(() => new V143JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V143Target>(() => new V143Target(domains.Target));
+        this.log = new Lazy<V143Log>(() => new V143Log(domains.Log));
     }

     /// <summary>
@@ -48,22 +56,22 @@ public class V143Domains : DevToolsDomains
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
PATCH_V143

# Apply patch to V144Domains.cs
patch -p1 <<'PATCH_V144'
--- a/dotnet/src/webdriver/DevTools/v144/V144Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v144/V144Domains.cs
@@ -24,6 +24,10 @@ namespace OpenQA.Selenium.DevTools.V144;
 public class V144Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V144Network> network;
+    private readonly Lazy<V144JavaScript> javaScript;
+    private readonly Lazy<V144Target> target;
+    private readonly Lazy<V144Log> log;

     /// <summary>
     /// Initializes a new instance of the V144Domains class.
@@ -33,6 +37,10 @@ public class V144Domains : DevToolsDomains
     public V144Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V144Network>(() => new V144Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V144JavaScript>(() => new V144JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V144Target>(() => new V144Target(domains.Target));
+        this.log = new Lazy<V144Log>(() => new V144Log(domains.Log));
     }

     /// <summary>
@@ -48,22 +56,22 @@ public class V144Domains : DevToolsDomains
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
PATCH_V144

# Apply patch to V145Domains.cs
patch -p1 <<'PATCH_V145'
--- a/dotnet/src/webdriver/DevTools/v145/V145Domains.cs
+++ b/dotnet/src/webdriver/DevTools/v145/V145Domains.cs
@@ -24,6 +24,10 @@ namespace OpenQA.Selenium.DevTools.V145;
 public class V145Domains : DevToolsDomains
 {
     private readonly DevToolsSessionDomains domains;
+    private readonly Lazy<V145Network> network;
+    private readonly Lazy<V145JavaScript> javaScript;
+    private readonly Lazy<V145Target> target;
+    private readonly Lazy<V145Log> log;

     /// <summary>
     /// Initializes a new instance of the V145Domains class.
@@ -33,6 +37,10 @@ public class V145Domains : DevToolsDomains
     public V145Domains(DevToolsSession session)
     {
         this.domains = new DevToolsSessionDomains(session ?? throw new ArgumentNullException(nameof(session)));
+        this.network = new Lazy<V145Network>(() => new V145Network(domains.Network, domains.Fetch));
+        this.javaScript = new Lazy<V145JavaScript>(() => new V145JavaScript(domains.Runtime, domains.Page));
+        this.target = new Lazy<V145Target>(() => new V145Target(domains.Target));
+        this.log = new Lazy<V145Log>(() => new V145Log(domains.Log));
     }

     /// <summary>
@@ -48,22 +56,22 @@ public class V145Domains : DevToolsDomains
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
PATCH_V145

echo "Gold patch applied successfully."
