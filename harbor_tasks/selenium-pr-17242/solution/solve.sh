#!/bin/bash
# Gold solution for selenium-node-command-interceptor task
# Applies the patch that adds NodeCommandInterceptor SPI

set -e

cd /workspace/selenium

# Check if already applied (idempotency)
if grep -q "NodeCommandInterceptor" java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/java/src/org/openqa/selenium/grid/BUILD.bazel b/java/src/org/openqa/selenium/grid/BUILD.bazel
index dcc5b7f0e2c82..b45a301439eeb 100644
--- a/java/src/org/openqa/selenium/grid/BUILD.bazel
+++ b/java/src/org/openqa/selenium/grid/BUILD.bazel
@@ -143,6 +143,7 @@ java_export(
         "org.openqa.selenium.remote.WebDriverInfo",
         "org.openqa.selenium.cli.CliCommand",
         "org.openqa.selenium.grid.config.HasRoles",
+        "org.openqa.selenium.grid.node.NodeCommandInterceptor",
         "org.openqa.selenium.grid.node.NodeSessionFactoryProvider",
         "org.openqa.selenium.remote.locators.CustomLocator",
         "org.openqa.selenium.remote.service.DriverService$Builder",
diff --git a/java/src/org/openqa/selenium/grid/node/BUILD.bazel b/java/src/org/openqa/selenium/grid/node/BUILD.bazel
index b258ca16a6ab6..5e63ebe73db7c 100644
--- a/java/src/org/openqa/selenium/grid/node/BUILD.bazel
+++ b/java/src/org/openqa/selenium/grid/node/BUILD.bazel
@@ -13,6 +13,7 @@ java_library(
     ],
     deps = [
         "//java/src/org/openqa/selenium:core",
+        "//java/src/org/openqa/selenium/events",
         "//java/src/org/openqa/selenium/grid/component",
         "//java/src/org/openqa/selenium/grid/config",
         "//java/src/org/openqa/selenium/grid/data",
diff --git a/java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java b/java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java
new file mode 100644
index 0000000000000..a153d4a666c7c
--- /dev/null
+++ b/java/src/org/openqa/selenium/grid/node/NodeCommandInterceptor.java
@@ -0,0 +1,90 @@
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
+
+package org.openqa.selenium.grid.node;
+
+import java.io.Closeable;
+import java.io.IOException;
+import java.util.concurrent.Callable;
+import org.openqa.selenium.events.EventBus;
+import org.openqa.selenium.grid.config.Config;
+import org.openqa.selenium.remote.SessionId;
+import org.openqa.selenium.remote.http.HttpRequest;
+import org.openqa.selenium.remote.http.HttpResponse;
+
+/**
+ * SPI for intercepting WebDriver commands executed through the Node. Implementations are discovered
+ * at runtime via {@link java.util.ServiceLoader} and may be provided at startup via {@code --ext}.
+ *
+ * <p>Interceptors are called in the order they are loaded. Each interceptor receives a {@code next}
+ * callable that, when invoked, advances to the next interceptor or executes the actual command.
+ *
+ * <p>The lifecycle of an enabled interceptor mirrors the {@code LocalNode} that hosts it: {@link
+ * #initialize} is called once at node startup and {@link #close} is called once when the node shuts
+ * down. Implementations that hold resources (thread pools, file handles, network connections)
+ * should release them in {@code close()}.
+ *
+ * <p>Typical usage — subscribe to session-lifecycle events in {@link #initialize} (via the {@code
+ * bus}), then annotate or observe each command in {@link #intercept}:
+ *
+ * <pre>{@code
+ * public void initialize(Config config, EventBus bus) {
+ *   bus.addListener(SessionCreatedEvent.listener(data -> onSessionStarted(data)));
+ *   bus.addListener(SessionClosedEvent.listener(data -> onSessionStopped(data)));
+ * }
+ *
+ * public HttpResponse intercept(SessionId id, HttpRequest req, Callable<HttpResponse> next)
+ *     throws Exception {
+ *   before(id, req);
+ *   HttpResponse response = next.call();
+ *   after(id, req, response);
+ *   return response;
+ * }
+ * }</pre>
+ */
+public interface NodeCommandInterceptor extends Closeable {
+
+  /** Returns {@code true} when this interceptor should be activated for the given config. */
+  boolean isEnabled(Config config);
+
+  /**
+   * Called once during node startup after {@link #isEnabled} returns {@code true}. Implementations
+   * should subscribe to session-lifecycle events on the {@code bus} here.
+   */
+  void initialize(Config config, EventBus bus);
+
+  /**
+   * Called once when the {@code LocalNode} shuts down. Implementations should release any resources
+   * acquired in {@link #initialize} (thread pools, open files, network connections).
+   *
+   * <p>The default implementation is a no-op; override only when cleanup is needed.
+   */
+  @Override
+  default void close() throws IOException {}
+
+  /**
+   * Wraps execution of a single WebDriver HTTP command. Implementations MUST call {@code
+   * next.call()} exactly once and return its result (possibly augmented).
+   *
+   * @param id the session ID extracted from the request URI
+   * @param req the incoming HTTP request
+   * @param next callable that advances to the next interceptor or executes the command
+   * @return the HTTP response to return to the caller
+   */
+  HttpResponse intercept(SessionId id, HttpRequest req, Callable<HttpResponse> next)
+      throws Exception;
+}
diff --git a/java/src/org/openqa/selenium/grid/node/local/LocalNode.java b/java/src/org/openqa/selenium/grid/node/local/LocalNode.java
index c2aaeaa1a0bb9..96dbf0b0ca60e 100644
--- a/java/src/org/openqa/selenium/grid/node/local/LocalNode.java
+++ b/java/src/org/openqa/selenium/grid/node/local/LocalNode.java
@@ -65,6 +65,7 @@
 import java.util.Optional;
 import java.util.Set;
 import java.util.UUID;
+import java.util.concurrent.Callable;
 import java.util.concurrent.Executors;
 import java.util.concurrent.ScheduledExecutorService;
 import java.util.concurrent.TimeUnit;
@@ -108,6 +109,7 @@
 import org.openqa.selenium.grid.node.ActiveSession;
 import org.openqa.selenium.grid.node.HealthCheck;
 import org.openqa.selenium.grid.node.Node;
+import org.openqa.selenium.grid.node.NodeCommandInterceptor;
 import org.openqa.selenium.grid.node.SessionFactory;
 import org.openqa.selenium.grid.node.config.NodeOptions;
 import org.openqa.selenium.grid.node.docker.DockerSession;
@@ -153,6 +155,7 @@ public class LocalNode extends Node implements Closeable {

   private final boolean bidiEnabled;
   private final boolean drainAfterSessions;
+  private final List<NodeCommandInterceptor> interceptors;
   private final List<SessionSlot> factories;
   private final Cache<SessionId, SessionSlot> currentSessions;
   private final Cache<SessionId, TemporaryFilesystem> uploadsTempFileSystem;
@@ -184,7 +187,8 @@ protected LocalNode(
       Secret registrationSecret,
       boolean managedDownloadsEnabled,
       int connectionLimitPerSession,
-      int nodeDownFailureThreshold) {
+      int nodeDownFailureThreshold,
+      List<NodeCommandInterceptor> interceptors) {
     super(
         tracer,
         new NodeId(UUID.randomUUID()),
@@ -210,6 +214,7 @@ protected LocalNode(
     this.connectionLimitPerSession = connectionLimitPerSession;
     // Use 0 to disable the failure threshold feature (unlimited retries)
     this.nodeDownFailureThreshold = nodeDownFailureThreshold;
+    this.interceptors = List.copyOf(interceptors);

     this.healthCheck =
         healthCheck == null
@@ -320,6 +325,18 @@ protected LocalNode(
           // ensure we do not leak running browsers
           currentSessions.invalidateAll();
           currentSessions.cleanUp();
+
+          // Give each interceptor a chance to release its resources.
+          for (NodeCommandInterceptor interceptor : interceptors) {
+            try {
+              interceptor.close();
+            } catch (Exception e) {
+              LOG.log(
+                  Level.WARNING,
+                  "Error closing interceptor " + interceptor.getClass().getName(),
+                  e);
+            }
+          }
         };

     Runtime.getRuntime()
@@ -827,13 +844,39 @@ public HttpResponse executeWebDriverCommand(HttpRequest req) {
       throw new NoSuchSessionException("Cannot find session with id: " + id);
     }

-    HttpResponse toReturn = slot.execute(req);
+    HttpResponse toReturn = executeWithInterceptors(id, req, () -> slot.execute(req));
     if (req.getMethod() == DELETE && req.getUri().equals("/session/" + id)) {
       stop(id);
     }
     return toReturn;
   }

+  private HttpResponse executeWithInterceptors(
+      SessionId id, HttpRequest req, Callable<HttpResponse> command) {
+    // Build interceptor chain from last to first so the first interceptor in the list is outermost.
+    Callable<HttpResponse> chain = command;
+    for (int i = interceptors.size() - 1; i >= 0; i--) {
+      final NodeCommandInterceptor interceptor = interceptors.get(i);
+      final Callable<HttpResponse> next = chain;
+      chain = () -> interceptor.intercept(id, req, next);
+    }
+    return callUnchecked(chain);
+  }
+
+  private static HttpResponse callUnchecked(Callable<HttpResponse> callable) {
+    try {
+      return callable.call();
+    } catch (RuntimeException e) {
+      throw e;
+    } catch (InterruptedException e) {
+      // Restore the interrupted status so callers and shutdown logic can observe it.
+      Thread.currentThread().interrupt();
+      throw new RuntimeException(e);
+    } catch (Exception e) {
+      throw new RuntimeException(e);
+    }
+  }
+
   @Override
   public HttpResponse downloadFile(HttpRequest req, SessionId id) {
     // When the session is running in a Docker container, the download file command
@@ -1373,6 +1416,7 @@ public static class Builder {
     private final URI gridUri;
     private final Secret registrationSecret;
     private final List<SessionSlot> factories;
+    private final List<NodeCommandInterceptor> interceptors = new ArrayList<>();
     private int maxSessions = NodeOptions.DEFAULT_MAX_SESSIONS;
     private int drainAfterSessionCount = NodeOptions.DEFAULT_DRAIN_AFTER_SESSION_COUNT;
     private boolean cdpEnabled = NodeOptions.DEFAULT_ENABLE_CDP;
@@ -1458,6 +1502,12 @@ public Builder nodeDownFailureThreshold(int threshold) {
       return this;
     }

+    public Builder addInterceptor(NodeCommandInterceptor interceptor) {
+      Require.nonNull("Command interceptor", interceptor);
+      interceptors.add(interceptor);
+      return this;
+    }
+
     public LocalNode build() {
       return new LocalNode(
           tracer,
@@ -1476,7 +1526,8 @@ public LocalNode build() {
           registrationSecret,
           managedDownloadsEnabled,
           connectionLimitPerSession,
-          nodeDownFailureThreshold);
+          nodeDownFailureThreshold,
+          List.copyOf(interceptors));
     }

     public Advanced advanced() {
diff --git a/java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java b/java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java
index 1c64091799bfb..25c7f816159a8 100644
--- a/java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java
+++ b/java/src/org/openqa/selenium/grid/node/local/LocalNodeFactory.java
@@ -32,6 +32,7 @@
 import org.openqa.selenium.grid.data.SlotMatcher;
 import org.openqa.selenium.grid.log.LoggingOptions;
 import org.openqa.selenium.grid.node.Node;
+import org.openqa.selenium.grid.node.NodeCommandInterceptor;
 import org.openqa.selenium.grid.node.NodeSessionFactoryProvider;
 import org.openqa.selenium.grid.node.SessionFactory;
 import org.openqa.selenium.grid.node.config.DriverServiceSessionFactory;
@@ -119,6 +120,22 @@ public static Node create(Config config) {
               }
             });

+    ServiceLoader.load(NodeCommandInterceptor.class)
+        .forEach(
+            interceptor -> {
+              String interceptorName = interceptor.getClass().getName();
+              if (interceptor.isEnabled(config)) {
+                LOG.info(String.format("Loading command interceptor from %s", interceptorName));
+                interceptor.initialize(config, eventOptions.getEventBus());
+                builder.addInterceptor(interceptor);
+              } else {
+                LOG.fine(
+                    String.format(
+                        "Interceptor %s is on the classpath but not enabled by configuration",
+                        interceptorName));
+              }
+            });
+
     if (config.getAll("relay", "configs").isPresent()) {
       new RelayOptions(config)
           .getSessionFactories(tracer, clientFactory, sessionTimeout)
diff --git a/java/test/org/openqa/selenium/grid/node/local/BUILD.bazel b/java/test/org/openqa/selenium/grid/node/local/BUILD.bazel
index 98a0f03219f32..6584c196646dd 100644
--- a/java/test/org/openqa/selenium/grid/node/local/BUILD.bazel
+++ b/java/test/org/openqa/selenium/grid/node/local/BUILD.bazel
@@ -8,6 +8,7 @@ java_test_suite(
     deps = [
         "//java/src/org/openqa/selenium/events",
         "//java/src/org/openqa/selenium/events/local",
+        "//java/src/org/openqa/selenium/grid/config",
         "//java/src/org/openqa/selenium/grid/data",
         "//java/src/org/openqa/selenium/grid/node",
         "//java/src/org/openqa/selenium/grid/node/local",
diff --git a/java/test/org/openqa/selenium/grid/node/local/LocalNodeTest.java b/java/test/org/openqa/selenium/grid/node/local/LocalNodeTest.java
index f6c6851760a75..0b8741ff1e7a4 100644
--- a/java/test/org/openqa/selenium/grid/node/local/LocalNodeTest.java
+++ b/java/test/org/openqa/selenium/grid/node/local/LocalNodeTest.java
@@ -427,6 +427,124 @@ void extractsFileNameFromRequestUri() {
         .isEqualTo("файл+with+tähtedega.png");
   }

+  @Test
+  void commandInterceptorIsCalledForEachWebDriverCommand() throws URISyntaxException {
+    Tracer tracer = DefaultTestTracer.createTracer();
+    EventBus bus = new GuavaEventBus();
+    URI uri = new URI("http://localhost:1234");
+    Capabilities stereotype = new ImmutableCapabilities("cheese", "brie");
+    List<String> interceptedCommands = new ArrayList<>();
+
+    LocalNode nodeWithInterceptor =
+        LocalNode.builder(tracer, bus, uri, uri, registrationSecret)
+            .add(
+                stereotype,
+                new TestSessionFactory(
+                    (id, caps) -> new Session(id, uri, stereotype, caps, Instant.now())))
+            .addInterceptor(
+                new org.openqa.selenium.grid.node.NodeCommandInterceptor() {
+                  @Override
+                  public boolean isEnabled(org.openqa.selenium.grid.config.Config config) {
+                    return true;
+                  }
+
+                  @Override
+                  public void initialize(
+                      org.openqa.selenium.grid.config.Config config, EventBus bus) {}
+
+                  @Override
+                  public HttpResponse intercept(
+                      SessionId id, HttpRequest req, Callable<HttpResponse> next) throws Exception {
+                    interceptedCommands.add(req.getMethod() + " " + req.getUri());
+                    return next.call();
+                  }
+                })
+            .build();
+
+    Either<WebDriverException, CreateSessionResponse> response =
+        nodeWithInterceptor.newSession(
+            new CreateSessionRequest(Set.of(W3C), stereotype, emptyMap()));
+    assertThat(response.isRight()).isTrue();
+
+    SessionId sessionId = response.right().getSession().getId();
+    nodeWithInterceptor.executeWebDriverCommand(
+        new HttpRequest(GET, "/session/" + sessionId + "/title"));
+
+    assertThat(interceptedCommands).hasSize(1);
+    assertThat(interceptedCommands.get(0)).contains("/title");
+  }
+
+  @Test
+  void multipleInterceptorsAreChainedOuterToInner() throws URISyntaxException {
+    Tracer tracer = DefaultTestTracer.createTracer();
+    EventBus bus = new GuavaEventBus();
+    URI uri = new URI("http://localhost:1234");
+    Capabilities stereotype = new ImmutableCapabilities("cheese", "brie");
+    List<String> callOrder = new ArrayList<>();
+
+    org.openqa.selenium.grid.node.NodeCommandInterceptor outer =
+        new org.openqa.selenium.grid.node.NodeCommandInterceptor() {
+          @Override
+          public boolean isEnabled(org.openqa.selenium.grid.config.Config config) {
+            return true;
+          }
+
+          @Override
+          public void initialize(org.openqa.selenium.grid.config.Config config, EventBus bus) {}
+
+          @Override
+          public HttpResponse intercept(SessionId id, HttpRequest req, Callable<HttpResponse> next)
+              throws Exception {
+            callOrder.add("outer-before");
+            HttpResponse resp = next.call();
+            callOrder.add("outer-after");
+            return resp;
+          }
+        };
+
+    org.openqa.selenium.grid.node.NodeCommandInterceptor inner =
+        new org.openqa.selenium.grid.node.NodeCommandInterceptor() {
+          @Override
+          public boolean isEnabled(org.openqa.selenium.grid.config.Config config) {
+            return true;
+          }
+
+          @Override
+          public void initialize(org.openqa.selenium.grid.config.Config config, EventBus bus) {}
+
+          @Override
+          public HttpResponse intercept(SessionId id, HttpRequest req, Callable<HttpResponse> next)
+              throws Exception {
+            callOrder.add("inner-before");
+            HttpResponse resp = next.call();
+            callOrder.add("inner-after");
+            return resp;
+          }
+        };
+
+    LocalNode nodeWithInterceptors =
+        LocalNode.builder(tracer, bus, uri, uri, registrationSecret)
+            .add(
+                stereotype,
+                new TestSessionFactory(
+                    (id, caps) -> new Session(id, uri, stereotype, caps, Instant.now())))
+            .addInterceptor(outer)
+            .addInterceptor(inner)
+            .build();
+
+    Either<WebDriverException, CreateSessionResponse> response =
+        nodeWithInterceptors.newSession(
+            new CreateSessionRequest(Set.of(W3C), stereotype, emptyMap()));
+    assertThat(response.isRight()).isTrue();
+    SessionId sessionId = response.right().getSession().getId();
+
+    nodeWithInterceptors.executeWebDriverCommand(
+        new HttpRequest(GET, "/session/" + sessionId + "/title"));
+
+    assertThat(callOrder)
+        .containsExactly("outer-before", "inner-before", "inner-after", "outer-after");
+  }
+
   private void waitUntilNodeStopped(SessionId sessionId) {
     long timeout = Duration.ofSeconds(5).toMillis();
PATCH

echo "Patch applied successfully"
