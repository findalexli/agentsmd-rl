#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch
cat << 'PATCH' | git apply -
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
PATCH

# Verify the patch was applied by checking for distinctive line
if ! grep -q "Always propagate VNC capabilities from the stereotype" java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java; then
    echo "ERROR: Patch not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
