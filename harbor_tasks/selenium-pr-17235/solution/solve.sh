#!/bin/bash
# Gold solution for SeleniumHQ/selenium#17235
# Fix VNC caps not propagated for sessions without browserName

set -e

cd /workspace/selenium

# Idempotency check - skip if already applied
if grep -q "Always propagate VNC capabilities from the stereotype" java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java b/java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java
index 89fcf5c58b017..cdecb5f5e1667 100644
--- a/java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java
+++ b/java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java
@@ -46,10 +46,9 @@ public SessionCapabilitiesMutator(Capabilities slotStereotype) {

   @Override
   public Capabilities apply(Capabilities capabilities) {
-    if (!Objects.equals(slotStereotype.getBrowserName(), capabilities.getBrowserName())) {
-      return capabilities;
-    }
-
+    // Always propagate VNC capabilities from the stereotype, regardless of whether the session
+    // request included a browserName. Requests without browserName (e.g. proxy-only caps) are
+    // still routed to a slot that has VNC enabled, so the VNC address must be present.
     Object vncEnabled = slotStereotype.getCapability(SE_VNC_ENABLED);
     if (vncEnabled != null) {
       Object vncPort = slotStereotype.getCapability(SE_NO_VNC_PORT);
@@ -59,6 +58,10 @@ public Capabilities apply(Capabilities capabilities) {
               .setCapability(SE_NO_VNC_PORT, Require.nonNull(SE_NO_VNC_PORT, vncPort));
     }

+    if (!Objects.equals(slotStereotype.getBrowserName(), capabilities.getBrowserName())) {
+      return capabilities;
+    }
+
     String browserName = capabilities.getBrowserName().toLowerCase(Locale.ENGLISH);

     if ("internet explorer".equalsIgnoreCase(browserName)) {
diff --git a/java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java b/java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java
index b1e3a808b296f..9f22c65b2d0f5 100644
--- a/java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java
+++ b/java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java
@@ -343,6 +343,26 @@ void shouldMergeTopLevelStereotypeAndCaps() {
     assertThat(modifiedCapabilities.get("pageLoadStrategy")).isEqualTo("normal");
   }

+  @Test
+  void shouldPropagateVncCapsWhenRequestHasNoBrowserName() {
+    // Requests without browserName (e.g. proxy-only caps) are still routed to a VNC-enabled slot;
+    // the VNC address must be present in the merged capabilities.
+    Capabilities stereotype =
+        new ImmutableCapabilities(
+            "browserName", "chrome", "se:vncEnabled", true, "se:noVncPort", 7900);
+
+    SessionCapabilitiesMutator sessionCapabilitiesMutator =
+        new SessionCapabilitiesMutator(stereotype);
+
+    Capabilities capabilities = new ImmutableCapabilities("proxy", Map.of("proxyType", "direct"));
+
+    Map<String, Object> modifiedCapabilities =
+        sessionCapabilitiesMutator.apply(capabilities).asMap();
+
+    assertThat(modifiedCapabilities.get("se:vncEnabled")).isEqualTo(true);
+    assertThat(modifiedCapabilities.get("se:noVncPort")).isEqualTo(7900);
+  }
+
   @Test
   void shouldAllowUnknownBrowserNames() {
     Capabilities stereotype = new ImmutableCapabilities("browserName", "safari");
PATCH

echo "Patch applied successfully."
