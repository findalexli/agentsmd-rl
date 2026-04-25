#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if already patched
if grep -q "resourceAsString(Class<?> resourceOwner, String resource)" java/src/org/openqa/selenium/io/Read.java 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java b/java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java
index a5afd71fc5fe3..99f65811c96be 100644
--- a/java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java
+++ b/java/src/org/openqa/selenium/devtools/events/CdpEventTypes.java
@@ -66,7 +66,9 @@ public void initializeListener(WebDriver webDriver) {
   public static EventType<Void> domMutation(Consumer<@Nullable DomMutationEvent> handler) {
     Require.nonNull("Handler", handler);

-    String script = Read.resourceAsString("/org/openqa/selenium/devtools/mutation-listener.js");
+    String script =
+        Read.resourceAsString(
+            CdpEventTypes.class, "/org/openqa/selenium/devtools/mutation-listener.js");

     return new EventType<>() {
       @Override
diff --git a/java/src/org/openqa/selenium/io/Read.java b/java/src/org/openqa/selenium/io/Read.java
index 389c916959051..82fab487c91d3 100644
--- a/java/src/org/openqa/selenium/io/Read.java
+++ b/java/src/org/openqa/selenium/io/Read.java
@@ -18,6 +18,7 @@
 package org.openqa.selenium.io;

 import static java.nio.charset.StandardCharsets.UTF_8;
+import static java.util.Objects.requireNonNull;

 import java.io.ByteArrayOutputStream;
 import java.io.IOException;
@@ -53,8 +54,19 @@ public static String toString(InputStream in) throws IOException {
     return new String(toByteArray(in), UTF_8);
   }

+  /**
+   * This method might not work in OSGI environment.
+   *
+   * @deprecated Use {@link #resourceAsString(Class, String)} instead
+   */
+  @Deprecated
   public static String resourceAsString(String resource) {
-    try (InputStream stream = Read.class.getResourceAsStream(resource)) {
+    return resourceAsString(Read.class, resource);
+  }
+
+  public static String resourceAsString(Class<?> resourceOwner, String resource) {
+    Class<?> clazz = requireNonNull(resourceOwner, "Class owning the resource");
+    try (InputStream stream = clazz.getResourceAsStream(resource)) {
       if (stream == null) {
         throw new IllegalArgumentException("Resource not found: " + resource);
       }
diff --git a/java/src/org/openqa/selenium/remote/RemoteScript.java b/java/src/org/openqa/selenium/remote/RemoteScript.java
index 797492791651d..0a513147f5d8a 100644
--- a/java/src/org/openqa/selenium/remote/RemoteScript.java
+++ b/java/src/org/openqa/selenium/remote/RemoteScript.java
@@ -84,7 +84,7 @@ public void removeJavaScriptErrorHandler(long id) {
   @Override
   public long addDomMutationHandler(Consumer<DomMutation> consumer) {
     String scriptValue =
-        Read.resourceAsString("/org/openqa/selenium/remote/bidi-mutation-listener.js");
+        Read.resourceAsString(getClass(), "/org/openqa/selenium/remote/bidi-mutation-listener.js");

     this.script.addPreloadScript(scriptValue, List.of(new ChannelValue("channel_name")));

diff --git a/java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java b/java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java
index b28399c11d1c4..0a02eb79e6878 100644
--- a/java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java
+++ b/java/src/org/openqa/selenium/remote/codec/w3c/W3CHttpCommandCodec.java
@@ -363,7 +363,7 @@ private List<String> stringToUtf8Array(String toConvert) {
               atomFileName,
               (fileName) -> {
                 String rawFunction =
-                    resourceAsString("/org/openqa/selenium/remote/" + atomFileName);
+                    resourceAsString(getClass(), "/org/openqa/selenium/remote/" + atomFileName);
                 String atomName = fileName.replace(".js", "");
                 return String.format(
                     "/* %s */return (%s).apply(null, arguments);", atomName, rawFunction);
diff --git a/java/test/org/openqa/selenium/io/ReadTest.java b/java/test/org/openqa/selenium/io/ReadTest.java
index 46a6bfbd7fa94..89b1a8449caf8 100644
--- a/java/test/org/openqa/selenium/io/ReadTest.java
+++ b/java/test/org/openqa/selenium/io/ReadTest.java
@@ -42,7 +42,7 @@ void canReadInputStreamToString() throws IOException {

   @Test
   void canReadResourceFromClasspath() {
-    String script = Read.resourceAsString("/org/openqa/selenium/remote/isDisplayed.js");
+    String script = Read.resourceAsString(Read.class, "/org/openqa/selenium/remote/isDisplayed.js");
     assertThat(script).isNotBlank().contains("function(){");
   }
 }
PATCH

echo "Patch applied successfully"
