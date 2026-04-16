#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if already patched
if grep -q "stopGracePeriod" java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java b/java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java
index 04b44008b42cf..18d65b497facb 100644
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
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java b/java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java
index ce422300835a2..29062fedd0a0d 100644
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
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java b/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java
index f7a554c4849c0..986ca70cb71ba 100644
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
diff --git a/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java b/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
index af81f42b675c0..028796fde54ed 100644
--- a/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
+++ b/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java
@@ -106,6 +106,7 @@ public class DockerSessionFactory implements SessionFactory {
   private final Map<String, Object> hostConfig;
   private final List<String> hostConfigKeys;
   private final Map<String, String> groupingLabels;
+  private final Duration stopGracePeriod;

   public DockerSessionFactory(
       Tracer tracer,
@@ -124,7 +125,8 @@ public DockerSessionFactory(
       Predicate<Capabilities> predicate,
       Map<String, Object> hostConfig,
       List<String> hostConfigKeys,
-      Map<String, String> groupingLabels) {
+      Map<String, String> groupingLabels,
+      Duration stopGracePeriod) {
     this.tracer = Require.nonNull("Tracer", tracer);
     this.clientFactory = Require.nonNull("HTTP client", clientFactory);
     this.sessionTimeout = Require.nonNull("Session timeout", sessionTimeout);
@@ -142,6 +144,7 @@ public DockerSessionFactory(
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

diff --git a/java/src/org/openqa/selenium/internal/Debug.java b/java/src/org/openqa/selenium/internal/Debug.java
index c7786ccb7ff8d..0b012f180f59e 100644
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
PATCH

echo "Gold patch applied successfully."
