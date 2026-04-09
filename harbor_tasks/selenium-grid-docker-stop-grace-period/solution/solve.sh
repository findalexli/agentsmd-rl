#!/bin/bash
set -e

cd /workspace/selenium

# Check if already patched (idempotency check)
if grep -q "try {" java/src/org/openqa/selenium/grid/node/docker/DockerSession.java 2>/dev/null && \
   grep -q "containerStopTimeout" java/src/org/openqa/selenium/grid/node/docker/DockerSession.java 2>/dev/null; then
  echo "Already patched"
  exit 0
fi

# Patch DockerFlags.java
patch -p1 java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java <<'DOCKERFLAGS'
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java
@@ -144,6 +144,17 @@ public class DockerFlags implements HasRoles {
       example = "\"" + DockerOptions.DEFAULT_ASSETS_PATH + "\"")
   private String assetsPath;

+  @Parameter(
+      names = {"--docker-stop-grace-period"},
+      description =
+          "Grace period (in seconds) to wait for browser and video containers to stop gracefully"
+              + " before they are forcibly terminated.")
+  @ConfigValue(
+      section = DockerOptions.DOCKER_SECTION,
+      name = "stop-grace-period",
+      example = "" + DockerOptions.DEFAULT_STOP_GRACE_PERIOD)
+  private Integer stopGracePeriod;
+
   @Override
   public Set<Role> getRoles() {
     return Collections.singleton(NODE_ROLE);
DOCKERFLAGS

# Patch DockerOptions.java
patch -p1 java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java <<'DOCKEROPTIONS'
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java
@@ -66,6 +66,7 @@ public class DockerOptions {
   static final String DEFAULT_VIDEO_IMAGE = "false";
   static final int DEFAULT_MAX_SESSIONS = Runtime.getRuntime().availableProcessors();
   static final int DEFAULT_SERVER_START_TIMEOUT = 60;
+  static final int DEFAULT_STOP_GRACE_PERIOD = 60;
   private static final String DEFAULT_DOCKER_NETWORK = "bridge";
   private static final Logger LOG = Logger.getLogger(DockerOptions.class.getName());
   private static final Json JSON = new Json();
@@ -116,6 +117,16 @@ private Duration getServerStartTimeout() {
         config.getInt(DOCKER_SECTION, "server-start-timeout").orElse(DEFAULT_SERVER_START_TIMEOUT));
   }

+  private Duration getStopGracePeriod() {
+    int seconds =
+        config.getInt(DOCKER_SECTION, "stop-grace-period").orElse(DEFAULT_STOP_GRACE_PERIOD);
+    if (seconds < 0) {
+      throw new ConfigException(
+          "stop-grace-period must be a non-negative integer, but was: " + seconds);
+    }
+    return Duration.ofSeconds(seconds);
+  }
+
   @Nullable
   private String getApiVersion() {
     return config.get(DOCKER_SECTION, "api-version").orElse(null);
@@ -189,6 +200,7 @@ public Map<Capabilities, Collection<SessionFactory>> getDockerSessionFactories(
             config.getInt("node", "max-sessions").orElse(DEFAULT_MAX_SESSIONS),
             DEFAULT_MAX_SESSIONS);
     Multimap<Capabilities, SessionFactory> factories = new Multimap<>();
+    Duration stopGracePeriod = getStopGracePeriod();
     kinds.forEach(
         (name, caps) -> {
           Image image = docker.getImage(name);
@@ -212,7 +224,8 @@ public Map<Capabilities, Collection<SessionFactory>> getDockerSessionFactories(
                     capabilities -> options.getSlotMatcher().matches(caps, capabilities),
                     hostConfig,
                     hostConfigKeys,
-                    groupingLabels));
+                    groupingLabels,
+                    stopGracePeriod));
           }
           LOG.info(
               String.format(
DOCKEROPTIONS

# Patch DockerSession.java
patch -p1 java/src/org/openqa/selenium/grid/node/docker/DockerSession.java <<'DOCKERSESSION'
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
@@ -50,6 +50,8 @@ public class DockerSession extends DefaultActiveSession {
   private final Container container;
   private final @Nullable Container videoContainer;
   private final DockerAssetsPath assetsPath;
+  private final Duration containerStopTimeout;
+  private final Duration videoContainerStopTimeout;

   DockerSession(
       Container container,
@@ -63,21 +65,29 @@ public class DockerSession extends DefaultActiveSession {
       Dialect downstream,
       Dialect upstream,
       Instant startTime,
-      DockerAssetsPath assetsPath) {
+      DockerAssetsPath assetsPath,
+      Duration containerStopTimeout,
+      Duration videoContainerStopTimeout) {
     super(tracer, client, id, url, downstream, upstream, stereotype, capabilities, startTime);
     this.container = Require.nonNull("Container", container);
     this.videoContainer = videoContainer;
     this.assetsPath = Require.nonNull("Assets path", assetsPath);
+    this.containerStopTimeout = Require.nonNull("Container stop timeout", containerStopTimeout);
+    this.videoContainerStopTimeout =
+        Require.nonNull("Video container stop timeout", videoContainerStopTimeout);
   }

   @Override
   public void stop() {
-    if (videoContainer != null) {
-      videoContainer.stop(Duration.ofSeconds(10));
+    try {
+      if (videoContainer != null) {
+        videoContainer.stop(videoContainerStopTimeout);
+      }
+      saveLogs();
+    } finally {
+      container.stop(containerStopTimeout);
+      super.stop();
     }
-    saveLogs();
-    container.stop(Duration.ofMinutes(1));
-    super.stop();
   }

   private void saveLogs() {
@@ -107,8 +117,8 @@ private void saveLogs() {
   private void parseMultiplexedStream(InputStream stream, OutputStream out) throws IOException {
     try (DataInputStream in = new DataInputStream(new BufferedInputStream(stream))) {
       while (true) {
-        in.skipBytes(1); // Skip "stream type" byte (1 = stdout, 2 = stderr)
-        in.skipBytes(3); // Skip the 3 empty padding bytes
+        in.readFully(new byte[1]); // Skip "stream type" byte (1 = stdout, 2 = stderr)
+        in.readFully(new byte[3]); // Skip the 3 empty padding bytes
         int payloadSize = in.readInt(); // Read the 4-byte payload size
         byte[] payload = new byte[payloadSize];
         in.readFully(payload);
DOCKERSESSION

# Patch DockerSessionFactory.java
patch -p1 java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java <<'DOCKERFACTORY'
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
@@ -106,6 +106,7 @@ public class DockerSessionFactory implements SessionFactory {
   private final Map<String, Object> hostConfig;
   private final List<String> hostConfigKeys;
   private final Map<String, String> groupingLabels;
+  private final Duration stopGracePeriod;

   public DockerSessionFactory(
       Tracer tracer,
@@ -124,7 +125,8 @@ public class DockerSessionFactory implements SessionFactory {
       Predicate<Capabilities> predicate,
       Map<String, Object> hostConfig,
       List<String> hostConfigKeys,
-      Map<String, String> groupingLabels) {
+      Map<String, String> groupingLabels,
+      Duration stopGracePeriod) {
     this.tracer = Require.nonNull("Tracer", tracer);
     this.clientFactory = Require.nonNull("HTTP client", clientFactory);
     this.sessionTimeout = Require.nonNull("Session timeout", sessionTimeout);
@@ -142,6 +144,7 @@ public class DockerSessionFactory implements SessionFactory {
     this.hostConfig = Require.nonNull("Container host config", hostConfig);
     this.hostConfigKeys = Require.nonNull("Browser container host config keys", hostConfigKeys);
     this.groupingLabels = Require.nonNull("Container grouping labels", groupingLabels);
+    this.stopGracePeriod = Require.nonNull("Container stop grace period", stopGracePeriod);
   }

   @Override
@@ -289,7 +292,9 @@ public Either<WebDriverException, ActiveSession> apply(CreateSessionRequest sess
               downstream,
               result.getDialect(),
               Instant.now(),
-              assetsPath));
+              assetsPath,
+              stopGracePeriod,
+              stopGracePeriod));
     }
   }
DOCKERFACTORY

# Patch Debug.java
patch -p1 java/src/org/openqa/selenium/internal/Debug.java <<'DEBUGPATCH'
--- a/java/src/org/openqa/selenium/internal/Debug.java
+++ b/java/src/org/openqa/selenium/internal/Debug.java
@@ -28,6 +28,7 @@ public class Debug {

   private static final boolean IS_DEBUG;
   private static final AtomicBoolean DEBUG_WARNING_LOGGED = new AtomicBoolean(false);
+  private static final Logger SELENIUM_LOGGER = Logger.getLogger("org.openqa.selenium");
   private static boolean loggerConfigured = false;

   static {
@@ -63,12 +64,11 @@ public static void configureLogger() {
       return;
     }

-    Logger seleniumLogger = Logger.getLogger("org.openqa.selenium");
-    seleniumLogger.setLevel(Level.FINE);
+    SELENIUM_LOGGER.setLevel(Level.FINE);

     StreamHandler handler = new StreamHandler(System.err, new SimpleFormatter());
     handler.setLevel(Level.FINE);
-    seleniumLogger.addHandler(handler);
+    SELENIUM_LOGGER.addHandler(handler);
     loggerConfigured = true;
   }
 }
DEBUGPATCH

# Patch BUILD.bazel files
patch -p1 java/test/org/openqa/selenium/grid/distributor/BUILD.bazel <<'DISTPATCH'
--- a/java/test/org/openqa/selenium/grid/distributor/BUILD.bazel
+++ b/java/test/org/openqa/selenium/grid/distributor/BUILD.bazel
@@ -81,5 +81,6 @@ java_test_suite(
         artifact("org.junit.jupiter:junit-jupiter-api"),
         artifact("org.assertj:assertj-core"),
         artifact("org.zeromq:jeromq"),
+        artifact("org.jspecify:jspecify"),
     ] + JUNIT5_DEPS,
 )
DISTPATCH

patch -p1 java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel <<'DOCKERBUILD'
--- a/java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel
+++ b/java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel
@@ -10,9 +10,11 @@ java_test_suite(
     ],
     deps = [
+        "//java/src/org/openqa/selenium:core",
         "//java/src/org/openqa/selenium/docker",
         "//java/src/org/openqa/selenium/grid/config",
         "//java/src/org/openqa/selenium/grid/node/docker",
+        "//java/src/org/openqa/selenium/remote",
         artifact("com.google.guava:guava"),
         artifact("io.opentelemetry:opentelemetry-api"),
         artifact("org.junit.jupiter:junit-jupiter-api"),
DOCKERBUILD

patch -p1 java/test/org/openqa/selenium/grid/router/BUILD.bazel <<'ROUTERBUILD'
--- a/java/test/org/openqa/selenium/grid/router/BUILD.bazel
+++ b/java/test/org/openqa/selenium/grid/router/BUILD.bazel
@@ -116,6 +116,7 @@ java_selenium_test_suite(
         "//java/src/org/openqa/selenium/bidi/log",
         "//java/src/org/openqa/selenium/bidi/module",
         "//java/src/org/openqa/selenium/firefox",
+        "//java/src/org/openqa/selenium/grid",
         "//java/src/org/openqa/selenium/grid/config",
         "//java/src/org/openqa/selenium/remote",
         "//java/test/org/openqa/selenium/environment",
ROUTERBUILD

# Create the DockerSessionTest.java file
cat > java/test/org/openqa/selenium/grid/node/docker/DockerSessionTest.java <<'TESTFILE'
// Licensed to the Software Freedom Conservancy (SFC) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The SFC licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package org.openqa.selenium.grid.node.docker;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.io.ByteArrayInputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.InOrder;
import org.openqa.selenium.ImmutableCapabilities;
import org.openqa.selenium.docker.Container;
import org.openqa.selenium.docker.ContainerId;
import org.openqa.selenium.docker.ContainerLogs;
import org.openqa.selenium.remote.Dialect;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.Contents;
import org.openqa.selenium.remote.http.HttpClient;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.tracing.Tracer;

@Tag("UnitTests")
class DockerSessionTest {

  @TempDir Path tempDir;

  private Container browserContainer;
  private Container videoContainer;
  private Tracer tracer;
  private HttpClient httpClient;
  private SessionId sessionId;
  private DockerAssetsPath assetsPath;

  @BeforeEach
  void setUp() throws Exception {
    browserContainer = mock(Container.class);
    videoContainer = mock(Container.class);
    tracer = mock(Tracer.class);
    httpClient = mock(HttpClient.class);

    when(httpClient.execute(any(HttpRequest.class))).thenReturn(new HttpResponse());
    when(browserContainer.isRunning()).thenReturn(true);

    sessionId = new SessionId("test-session-id");
    assetsPath = new DockerAssetsPath(tempDir.toString(), tempDir.toString());

    when(browserContainer.getLogs())
        .thenReturn(new ContainerLogs(new ContainerId("browser-id"), Contents.empty()));
  }

  private DockerSession createSession(Container video) throws Exception {
    return createSession(video, Duration.ofMinutes(1), Duration.ofSeconds(10));
  }

  private DockerSession createSession(
      Container video, Duration containerStopTimeout, Duration videoContainerStopTimeout)
      throws Exception {
    return new DockerSession(
        browserContainer,
        video,
        tracer,
        httpClient,
        sessionId,
        new URL("http://localhost:4444"),
        new ImmutableCapabilities(),
        new ImmutableCapabilities(),
        Dialect.W3C,
        Dialect.W3C,
        Instant.now(),
        assetsPath,
        containerStopTimeout,
        videoContainerStopTimeout);
  }

  @Test
  void stopWithVideo_videoContainerStoppedBeforeLogs() throws Exception {
    DockerSession session = createSession(videoContainer);

    InOrder order = inOrder(videoContainer, browserContainer);
    session.stop();

    order.verify(videoContainer).stop(any(Duration.class));
    order.verify(browserContainer).getLogs();
    order.verify(browserContainer).stop(any(Duration.class));
  }

  @Test
  void stopWithoutVideo_logsAndBrowserContainerStopped() throws Exception {
    DockerSession session = createSession(null);

    session.stop();

    verify(videoContainer, never()).stop(any(Duration.class));
    verify(browserContainer).getLogs();
    verify(browserContainer).stop(any(Duration.class));
  }

  @Test
  void stop_logsWrittenBeforeBrowserContainerStopped() throws Exception {
    byte[] logBytes = "INFO: Session started\nINFO: Session ended\n".getBytes();
    when(browserContainer.getLogs())
        .thenReturn(
            new ContainerLogs(
                new ContainerId("browser-id"),
                Contents.fromStream(new ByteArrayInputStream(logBytes), logBytes.length)));

    Path sessionDir = tempDir.resolve(sessionId.toString());
    Files.createDirectories(sessionDir);

    DockerSession session = createSession(null);
    session.stop();

    assertThat(sessionDir.resolve("selenium-server.log")).exists();
  }

  @Test
  void stop_browserContainerAlwaysStoppedEvenIfVideoStopFails() throws Exception {
    doThrow(new RuntimeException("video stop failed")).when(videoContainer).stop(any());

    DockerSession session = createSession(videoContainer);

    try {
      session.stop();
    } catch (RuntimeException ignored) {
    }

    verify(browserContainer).stop(any(Duration.class));
  }

  @Test
  void stop_browserContainerStoppedEvenIfLogFetchThrows() throws Exception {
    when(browserContainer.getLogs()).thenThrow(new RuntimeException("log fetch failed"));

    DockerSession session = createSession(null);

    try {
      session.stop();
    } catch (RuntimeException ignored) {
    }

    verify(browserContainer).stop(any(Duration.class));
  }

  @Test
  void stop_configuredStopGracePeriodIsPassedToBothContainers() throws Exception {
    Duration gracePeriod = Duration.ofSeconds(42);
    DockerSession session = createSession(videoContainer, gracePeriod, gracePeriod);

    session.stop();

    verify(videoContainer).stop(gracePeriod);
    verify(browserContainer).stop(gracePeriod);
  }
}
TESTFILE

echo "Patch and test file applied successfully"
