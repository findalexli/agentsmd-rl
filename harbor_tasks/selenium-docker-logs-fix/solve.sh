#!/bin/bash
set -e

cd /workspace/selenium

# Apply the fix for docker logs parsing
cat <<'PATCH' | git apply -
diff --git a/java/src/org/openqa/selenium/docker/Container.java b/java/src/org/openqa/selenium/docker/Container.java
index 6d03663e45206..1407e0f90dbfe 100644
--- a/java/src/org/openqa/selenium/docker/Container.java
+++ b/java/src/org/openqa/selenium/docker/Container.java
@@ -18,10 +18,10 @@
 package org.openqa.selenium.docker;

 import java.time.Duration;
-import java.util.ArrayList;
 import java.util.logging.Level;
 import java.util.logging.Logger;
 import org.openqa.selenium.internal.Require;
+import org.openqa.selenium.remote.http.Contents;

 public class Container {

@@ -72,6 +72,10 @@ public ContainerLogs getLogs() {
       LOG.info("Getting logs " + getId());
       return protocol.getContainerLogs(getId());
     }
-    return new ContainerLogs(getId(), new ArrayList<>());
+    return new ContainerLogs(getId(), Contents.empty());
+  }
+
+  public boolean isRunning() {
+    return running;
   }
 }
diff --git a/java/src/org/openqa/selenium/docker/ContainerLogs.java b/java/src/org/openqa/selenium/docker/ContainerLogs.java
index 6a66837579e52..2e099c19e6e16 100644
--- a/java/src/org/openqa/selenium/docker/ContainerLogs.java
+++ b/java/src/org/openqa/selenium/docker/ContainerLogs.java
@@ -17,21 +17,39 @@

 package org.openqa.selenium.docker;

+import static java.nio.charset.StandardCharsets.UTF_8;
+
+import java.io.BufferedReader;
+import java.io.IOException;
+import java.io.InputStream;
+import java.io.InputStreamReader;
+import java.io.UncheckedIOException;
 import java.util.List;
+import java.util.stream.Collectors;
 import org.openqa.selenium.internal.Require;
+import org.openqa.selenium.remote.http.Contents;

 public class ContainerLogs {

-  private final List<String> logLines;
+  private final Contents.Supplier contents;
   private final ContainerId id;

-  public ContainerLogs(ContainerId id, List<String> logLines) {
-    this.logLines = Require.nonNull("Container logs", logLines);
+  public ContainerLogs(ContainerId id, Contents.Supplier contents) {
+    this.contents = Require.nonNull("Container logs", contents);
     this.id = Require.nonNull("Container id", id);
   }

+  /**
+   * @deprecated List of container logs might be very long. If you need to write down the logs, use
+   *     {@link #getLogs()} to avoid reading the whole content to memory.
+   */
+  @Deprecated
   public List<String> getLogLines() {
-    return logLines;
+    try (BufferedReader in = new BufferedReader(new InputStreamReader(contents.get(), UTF_8))) {
+      return in.lines().collect(Collectors.toList());
+    } catch (IOException e) {
+      throw new UncheckedIOException(e);
+    }
   }

   public ContainerId getId() {
@@ -40,6 +58,10 @@ public ContainerId getId() {

   @Override
   public String toString() {
-    return String.format("ContainerInfo{containerLogs=%s, id=%s}", logLines, id);
+    return String.format("ContainerInfo{id=%s,size=%s}", id, contents.length());
+  }
+
+  public InputStream getLogs() {
+    return contents.get();
   }
 }
diff --git a/java/src/org/openqa/selenium/docker/client/GetContainerLogs.java b/java/src/org/openqa/selenium/docker/client/GetContainerLogs.java
index 81fb12b4889ef..84c74fb94fbcd 100644
--- a/java/src/org/openqa/selenium/docker/client/GetContainerLogs.java
+++ b/java/src/org/openqa/selenium/docker/client/GetContainerLogs.java
@@ -20,12 +20,10 @@
 import static java.net.HttpURLConnection.HTTP_OK;
 import static org.openqa.selenium.remote.http.HttpMethod.GET;

-import java.util.List;
 import java.util.logging.Logger;
 import org.openqa.selenium.docker.ContainerId;
 import org.openqa.selenium.docker.ContainerLogs;
 import org.openqa.selenium.internal.Require;
-import org.openqa.selenium.remote.http.Contents;
 import org.openqa.selenium.remote.http.HttpHandler;
 import org.openqa.selenium.remote.http.HttpRequest;
 import org.openqa.selenium.remote.http.HttpResponse;
@@ -47,12 +45,11 @@ public ContainerLogs apply(ContainerId id) {
     String requestUrl =
         String.format("/v%s/containers/%s/logs?stdout=true&stderr=true", apiVersion, id);

-    HttpResponse res =
-        client.execute(new HttpRequest(GET, requestUrl).addHeader("Content-Type", "text/plain"));
+    HttpResponse res = client.execute(new HttpRequest(GET, requestUrl));
     if (res.getStatus() != HTTP_OK) {
-      LOG.warning("Unable to inspect container " + id);
+      LOG.warning(() -> "Unable to inspect container " + id);
     }
-    List<String> logLines = List.of(Contents.string(res).split("\\n"));
-    return new ContainerLogs(id, logLines);
+
+    return new ContainerLogs(id, res.getContent());
   }
 }
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java b/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
index 464be03e5ab5d..f7a554c4849c0 100644
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
@@ -17,17 +17,26 @@

 package org.openqa.selenium.grid.node.docker;

+import static java.util.logging.Level.FINE;
+
+import java.io.BufferedInputStream;
+import java.io.BufferedOutputStream;
+import java.io.DataInputStream;
+import java.io.EOFException;
+import java.io.File;
+import java.io.FileOutputStream;
+import java.io.IOException;
+import java.io.InputStream;
+import java.io.OutputStream;
 import java.net.URL;
-import java.nio.file.Files;
-import java.nio.file.Paths;
 import java.time.Duration;
 import java.time.Instant;
-import java.util.List;
 import java.util.logging.Level;
 import java.util.logging.Logger;
 import org.jspecify.annotations.Nullable;
 import org.openqa.selenium.Capabilities;
 import org.openqa.selenium.docker.Container;
+import org.openqa.selenium.docker.ContainerLogs;
 import org.openqa.selenium.grid.node.DefaultActiveSession;
 import org.openqa.selenium.internal.Require;
 import org.openqa.selenium.remote.Dialect;
@@ -72,13 +81,41 @@ public void stop() {
   }

   private void saveLogs() {
+    if (!container.isRunning()) {
+      LOG.log(
+          FINE, () -> "Skip saving logs because container is not running: " + container.getId());
+      return;
+    }
+
     String sessionAssetsPath = assetsPath.getContainerPath(getId());
-    String seleniumServerLog = String.format("%s/selenium-server.log", sessionAssetsPath);
-    try {
-      List<String> logs = container.getLogs().getLogLines();
-      Files.write(Paths.get(seleniumServerLog), logs);
-    } catch (Exception e) {
+    File seleniumServerLog = new File(sessionAssetsPath, "selenium-server.log");
+    ContainerLogs containerLogs = container.getLogs();
+
+    try (OutputStream out = new BufferedOutputStream(new FileOutputStream(seleniumServerLog))) {
+      parseMultiplexedStream(containerLogs.getLogs(), out);
+      LOG.log(
+          FINE,
+          () ->
+              String.format(
+                  "Saved container %s logs to file %s", container.getId(), seleniumServerLog));
+    } catch (IOException e) {
       LOG.log(Level.WARNING, "Error saving logs", e);
     }
   }
+
+  @SuppressWarnings("InfiniteLoopStatement")
+  private void parseMultiplexedStream(InputStream stream, OutputStream out) throws IOException {
+    try (DataInputStream in = new DataInputStream(new BufferedInputStream(stream))) {
+      while (true) {
+        in.skipBytes(1); // Skip "stream type" byte (1 = stdout, 2 = stderr)
+        in.skipBytes(3); // Skip the 3 empty padding bytes
+        int payloadSize = in.readInt(); // Read the 4-byte payload size
+        byte[] payload = new byte[payloadSize];
+        in.readFully(payload);
+        out.write(payload);
+      }
+    } catch (EOFException done) {
+      LOG.log(FINE, () -> "Finished reading multiplexed stream: " + done);
+    }
+  }
 }
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java b/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
index 189275b166240..af81f42b675c0 100644
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
@@ -466,7 +466,7 @@ private TimeZone getTimeZone(Capabilities sessionRequestCapabilities) {
       }
     }
     String envTz = System.getenv("TZ");
-    if (List.of(TimeZone.getAvailableIDs()).contains(envTz)) {
+    if (envTz != null && List.of(TimeZone.getAvailableIDs()).contains(envTz)) {
       return TimeZone.getTimeZone(envTz);
     }
     return null;
diff --git a/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java b/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java
index 921f746874ccc..21fafceac7af8 100644
--- a/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java
+++ b/java/src/org/openqa/selenium/remote/http/jdk/JdkHttpMessages.java
@@ -181,7 +181,7 @@ private Contents.Supplier extractContent(java.net.http.HttpResponse<InputStream>
         response
             .headers()
             .firstValue("Content-Type")
-            .map(contentType -> contentType.equalsIgnoreCase(MediaType.OCTET_STREAM.toString()))
+            .map(contentType -> isBinaryStream(contentType))
             .orElse(false);

     if (isBinaryStream) {
@@ -193,6 +193,12 @@ private Contents.Supplier extractContent(java.net.http.HttpResponse<InputStream>
     }
   }

+  private static boolean isBinaryStream(String contentType) {
+    return MediaType.OCTET_STREAM.toString().equalsIgnoreCase(contentType)
+        || "application/vnd.docker.multiplexed-stream".equalsIgnoreCase(contentType)
+        || "application/vnd.docker.raw-stream".equalsIgnoreCase(contentType);
+  }
+
   private byte[] readResponseBody(java.net.http.HttpResponse<InputStream> response) {
     try (InputStream in = response.body()) {
       return Read.toByteArray(in);
PATCH

# Verify the patch was applied by checking for a distinctive line
if git diff --name-only | grep -q "DockerSession.java"; then
    echo "Patch applied successfully"
else
    echo "Patch may not have applied correctly"
    exit 1
fi
