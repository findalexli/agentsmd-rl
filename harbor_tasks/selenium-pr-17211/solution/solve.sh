#!/bin/bash
# Applies the gold fix for Selenium PR #17211
# "[grid] Align Router-Node read timeout with session pageLoad capability"

set -e
cd /workspace/selenium

# Idempotency check - skip if already applied
if grep -q "READ_TIMEOUT_BUFFER" java/src/org/openqa/selenium/grid/router/HandleSession.java 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Write the fixed HandleSession.java
cat > java/src/org/openqa/selenium/grid/router/HandleSession.java <<'JAVAFILE'
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

package org.openqa.selenium.grid.router;

import static org.openqa.selenium.remote.HttpSessionId.getSessionId;
import static org.openqa.selenium.remote.RemoteTags.SESSION_ID;
import static org.openqa.selenium.remote.RemoteTags.SESSION_ID_EVENT;
import static org.openqa.selenium.remote.http.Contents.asJson;
import static org.openqa.selenium.remote.http.Contents.string;
import static org.openqa.selenium.remote.http.HttpMethod.GET;
import static org.openqa.selenium.remote.tracing.Tags.EXCEPTION;
import static org.openqa.selenium.remote.tracing.Tags.HTTP_REQUEST;
import static org.openqa.selenium.remote.tracing.Tags.HTTP_REQUEST_EVENT;
import static org.openqa.selenium.remote.tracing.Tags.HTTP_RESPONSE;

import java.io.Closeable;
import java.net.URI;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.openqa.selenium.Capabilities;
import org.openqa.selenium.NoSuchSessionException;
import org.openqa.selenium.concurrent.ExecutorServices;
import org.openqa.selenium.concurrent.GuardedRunnable;
import org.openqa.selenium.grid.data.NodeStatus;
import org.openqa.selenium.grid.data.Session;
import org.openqa.selenium.grid.sessionmap.SessionMap;
import org.openqa.selenium.grid.web.ReverseProxyHandler;
import org.openqa.selenium.internal.Require;
import org.openqa.selenium.json.Json;
import org.openqa.selenium.remote.ErrorCodec;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.ClientConfig;
import org.openqa.selenium.remote.http.HttpClient;
import org.openqa.selenium.remote.http.HttpHandler;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.tracing.AttributeKey;
import org.openqa.selenium.remote.tracing.AttributeMap;
import org.openqa.selenium.remote.tracing.HttpTracing;
import org.openqa.selenium.remote.tracing.Span;
import org.openqa.selenium.remote.tracing.Status;
import org.openqa.selenium.remote.tracing.Tracer;

class HandleSession implements HttpHandler, Closeable {

  private static final Logger LOG = Logger.getLogger(HandleSession.class.getName());

  static final Duration READ_TIMEOUT_BUFFER = Duration.ofSeconds(30);

  /**
   * Cache key combining the Node URI and the effective read-timeout. Sessions that target the same
   * Node and have the same effective timeout share a connection-pooled {@link HttpClient}, while
   * sessions with a longer {@code pageLoad} timeout get their own client so the Router never cuts
   * off a legitimate long-running navigation.
   */
  private static final class NodeClientKey {
    private final URI uri;
    private final Duration readTimeout;

    NodeClientKey(URI uri, Duration readTimeout) {
      this.uri = uri;
      this.readTimeout = readTimeout;
    }

    @Override
    public boolean equals(Object o) {
      if (!(o instanceof NodeClientKey)) return false;
      NodeClientKey k = (NodeClientKey) o;
      return Objects.equals(uri, k.uri) && Objects.equals(readTimeout, k.readTimeout);
    }

    @Override
    public int hashCode() {
      return Objects.hash(uri, readTimeout);
    }
  }

  private static class CacheEntry {
    private final HttpClient httpClient;
    private final AtomicLong inUse;
    // volatile as the ConcurrentMap will not take care of synchronization
    private volatile Instant lastUse;

    public CacheEntry(HttpClient httpClient, long initialUsage) {
      this.httpClient = httpClient;
      this.inUse = new AtomicLong(initialUsage);
      this.lastUse = Instant.now();
    }
  }

  private static class UsageCountingReverseProxyHandler extends ReverseProxyHandler
      implements Closeable {
    private final CacheEntry entry;

    public UsageCountingReverseProxyHandler(
        Tracer tracer, HttpClient httpClient, CacheEntry entry) {
      super(tracer, httpClient);

      this.entry = entry;
    }

    @Override
    public void close() {
      // must not call super.close() here, to ensure the HttpClient stays alive
      // set the last use here, to ensure we have to calculate the real inactivity of the client
      entry.lastUse = Instant.now();
      entry.inUse.decrementAndGet();
    }
  }

  private final Tracer tracer;
  private final HttpClient.Factory httpClientFactory;
  private final SessionMap sessions;
  // Caches the Node's own session-timeout (from /se/grid/node/status) so the HTTP
  // call is made at most once per Node URI rather than once per session.
  private final ConcurrentMap<URI, Duration> nodeTimeoutCache;
  // Keyed by (nodeUri, effectiveReadTimeout) so sessions with the same timeout on
  // the same Node share a pooled HttpClient while sessions with a longer pageLoad
  // timeout get a client sized to their actual value.
  private final ConcurrentMap<NodeClientKey, CacheEntry> httpClients;
  private final ScheduledExecutorService cleanUpHttpClientsCacheService;

  HandleSession(Tracer tracer, HttpClient.Factory httpClientFactory, SessionMap sessions) {
    this.tracer = Require.nonNull("Tracer", tracer);
    this.httpClientFactory = Require.nonNull("HTTP client factory", httpClientFactory);
    this.sessions = Require.nonNull("Sessions", sessions);

    this.nodeTimeoutCache = new ConcurrentHashMap<>();
    this.httpClients = new ConcurrentHashMap<>();

    Runnable cleanUpHttpClients =
        () -> {
          Instant staleBefore = Instant.now().minus(2, ChronoUnit.MINUTES);

          // Use removeIf for safe and efficient removal from ConcurrentHashMap
          httpClients
              .entrySet()
              .removeIf(
                  entry -> {
                    CacheEntry cacheEntry = entry.getValue();
                    if (cacheEntry.inUse.get() != 0) {
                      // the client is currently in use
                      return false;
                    }
                    if (!cacheEntry.lastUse.isBefore(staleBefore)) {
                      // the client was recently used
                      return false;
                    }
                    // the client has not been used for a while, close and remove it
                    try {
                      cacheEntry.httpClient.close();
                    } catch (Exception ex) {
                      LOG.log(Level.WARNING, "failed to close a stale httpclient", ex);
                    }
                    return true;
                  });
        };

    this.cleanUpHttpClientsCacheService =
        Executors.newSingleThreadScheduledExecutor(
            r -> {
              Thread thread = new Thread(r);
              thread.setDaemon(true);
              thread.setName("HandleSession - Clean up http clients cache");
              return thread;
            });
    cleanUpHttpClientsCacheService.scheduleAtFixedRate(
        GuardedRunnable.guard(cleanUpHttpClients), 1, 1, TimeUnit.MINUTES);
  }

  @Override
  public HttpResponse execute(HttpRequest req) {
    try (Span span = HttpTracing.newSpanAsChildOf(tracer, req, "router.handle_session")) {
      AttributeMap attributeMap = tracer.createAttributeMap();
      attributeMap.put(AttributeKey.HTTP_HANDLER_CLASS.getKey(), getClass().getName());

      HTTP_REQUEST.accept(span, req);
      HTTP_REQUEST_EVENT.accept(attributeMap, req);

      SessionId id =
          getSessionId(req.getUri())
              .map(SessionId::new)
              .orElseThrow(
                  () -> {
                    NoSuchSessionException exception =
                        new NoSuchSessionException("Cannot find session: " + req);
                    EXCEPTION.accept(attributeMap, exception);
                    attributeMap.put(
                        AttributeKey.EXCEPTION_MESSAGE.getKey(),
                        "Unable to execute request for an existing session: "
                            + exception.getMessage());
                    span.addEvent(AttributeKey.EXCEPTION_EVENT.getKey(), attributeMap);
                    return exception;
                  });

      SESSION_ID.accept(span, id);
      SESSION_ID_EVENT.accept(attributeMap, id);

      try {
        HttpTracing.inject(tracer, span, req);
        HttpResponse res;
        try (UsageCountingReverseProxyHandler handler = loadSessionId(tracer, span, id).call()) {
          res = handler.execute(req);
        }

        HTTP_RESPONSE.accept(span, res);

        return res;
      } catch (Exception e) {
        span.setAttribute(AttributeKey.ERROR.getKey(), true);
        span.setStatus(Status.CANCELLED);

        String errorMessage =
            "Unable to execute request for an existing session: " + e.getMessage();
        EXCEPTION.accept(attributeMap, e);
        attributeMap.put(AttributeKey.EXCEPTION_MESSAGE.getKey(), errorMessage);
        span.addEvent(AttributeKey.EXCEPTION_EVENT.getKey(), attributeMap);

        if (e instanceof NoSuchSessionException) {
          HttpResponse response = new HttpResponse();
          response.setStatus(404);
          response.setContent(asJson(ErrorCodec.createDefault().encode(e)));
          return response;
        }

        Throwable cause = e.getCause();
        if (cause instanceof RuntimeException) {
          throw (RuntimeException) cause;
        } else if (cause != null) {
          throw new RuntimeException(errorMessage, cause);
        } else if (e instanceof RuntimeException) {
          throw (RuntimeException) e;
        }
        throw new RuntimeException(errorMessage, e);
      }
    }
  }

  private Callable<UsageCountingReverseProxyHandler> loadSessionId(
      Tracer tracer, Span span, SessionId id) {
    return span.wrap(
        () -> {
          // Retrieve the full Session so we can read the WebDriver timeouts from capabilities.
          // SessionMap.get() is the same call that getUri() delegates to internally, so there is
          // no extra network round-trip compared to the previous getUri()-only approach.
          Session session = sessions.get(id);
          URI sessionUri = session.getUri();

          // Use the pageLoad timeout (plus a buffer) so the Router never cuts off a legitimate
          // long-running navigation. Fall back to the Node's own sessionTimeout when it is larger,
          // as it represents the Grid operator's upper bound for command duration.
          Duration pageLoadTimeout = sessionReadTimeout(session.getCapabilities());
          // Only cache successful fetches so that a transient error on the first command
          // does not permanently lock in the fallback default for the node's timeout.
          // computeIfAbsent skips storing when the mapping function returns null, so a
          // failed fetch is retried on the next command rather than cached forever.
          Duration fetchedNodeTimeout =
              nodeTimeoutCache.computeIfAbsent(
                  sessionUri, uri -> fetchNodeTimeout(uri).orElse(null));
          Duration nodeTimeout =
              fetchedNodeTimeout != null
                  ? fetchedNodeTimeout
                  : ClientConfig.defaultConfig().readTimeout();
          Duration base =
              pageLoadTimeout.compareTo(nodeTimeout) >= 0 ? pageLoadTimeout : nodeTimeout;
          Duration effectiveTimeout = base.plus(READ_TIMEOUT_BUFFER);

          LOG.fine(
              () ->
                  String.format(
                      "Session %s: pageLoad=%ds, node=%ds → read timeout=%ds",
                      id,
                      pageLoadTimeout.toSeconds(),
                      nodeTimeout.toSeconds(),
                      effectiveTimeout.toSeconds()));

          NodeClientKey key = new NodeClientKey(sessionUri, effectiveTimeout);
          CacheEntry cacheEntry =
              httpClients.compute(
                  key,
                  (k, entry) -> {
                    if (entry != null) {
                      entry.inUse.incrementAndGet();
                      return entry;
                    }

                    ClientConfig config =
                        ClientConfig.defaultConfig()
                            .baseUri(sessionUri)
                            .readTimeout(effectiveTimeout)
                            .withRetries();
                    return new CacheEntry(httpClientFactory.createClient(config), 1);
                  });

          try {
            return new UsageCountingReverseProxyHandler(tracer, cacheEntry.httpClient, cacheEntry);
          } catch (Throwable t) {
            // ensure we do not keep the http client when an unexpected throwable is raised
            cacheEntry.inUse.decrementAndGet();
            throw t;
          }
        });
  }

  /**
   * Returns the effective read-timeout derived from the session's WebDriver timeouts. Only {@code
   * pageLoad} (navigation) is considered — it is the command type that can block the Router for
   * extended periods. Falls back to {@link ClientConfig#defaultConfig()}'s read timeout when the
   * value is absent.
   */
  static Duration sessionReadTimeout(Capabilities caps) {
    Object timeoutsObj = caps.getCapability("timeouts");
    if (timeoutsObj instanceof Map) {
      Map<?, ?> timeouts = (Map<?, ?>) timeoutsObj;
      long pageLoadMs = longFrom(timeouts.get("pageLoad"));
      if (pageLoadMs > 0) {
        return Duration.ofMillis(pageLoadMs);
      }
    }
    return ClientConfig.defaultConfig().readTimeout();
  }

  private static long longFrom(Object value) {
    if (value instanceof Long) return (Long) value;
    if (value instanceof Number) return ((Number) value).longValue();
    return 0L;
  }

  /**
   * Fetches the Node's own session-timeout from {@code /se/grid/node/status}. Returns empty on any
   * failure so the caller can skip caching and retry on the next command.
   */
  private Optional<Duration> fetchNodeTimeout(URI uri) {
    ClientConfig config = ClientConfig.defaultConfig().baseUri(uri);
    try (HttpClient httpClient = httpClientFactory.createClient(config)) {
      HttpResponse res = httpClient.execute(new HttpRequest(GET, "/se/grid/node/status"));
      NodeStatus nodeStatus = new Json().toType(string(res), NodeStatus.class);
      if (nodeStatus != null) {
        return Optional.of(nodeStatus.getSessionTimeout());
      }
    } catch (Exception e) {
      LOG.fine("Unable to fetch node status for " + uri);
    }
    return Optional.empty();
  }

  @Override
  public void close() {
    ExecutorServices.shutdownGracefully(
        "HandleSession - Clean up http clients cache", cleanUpHttpClientsCacheService);
    httpClients
        .values()
        .removeIf(
            (entry) -> {
              entry.httpClient.close();
              return true;
            });
  }
}
JAVAFILE

# Create the test file directory
mkdir -p java/test/org/openqa/selenium/grid/router

# Create the test file
cat > java/test/org/openqa/selenium/grid/router/HandleSessionReadTimeoutTest.java <<'TESTFILE'
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

package org.openqa.selenium.grid.router;

import static org.assertj.core.api.Assertions.assertThat;
import static org.openqa.selenium.remote.http.HttpMethod.GET;

import java.net.URI;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.Capabilities;
import org.openqa.selenium.ImmutableCapabilities;
import org.openqa.selenium.events.local.GuavaEventBus;
import org.openqa.selenium.grid.data.Session;
import org.openqa.selenium.grid.sessionmap.local.LocalSessionMap;
import org.openqa.selenium.json.Json;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.ClientConfig;
import org.openqa.selenium.remote.http.Contents;
import org.openqa.selenium.remote.http.HttpClient;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.http.WebSocket;
import org.openqa.selenium.remote.tracing.DefaultTestTracer;
import org.openqa.selenium.remote.tracing.Tracer;

/**
 * Unit and integration tests for {@link HandleSession}'s per-session read-timeout logic.
 *
 * <p>The Router's read timeout must be at least as long as the WebDriver {@code pageLoad} timeout
 * reported in the session capabilities so that the Router never cuts off a legitimate long-running
 * command before the Node has had time to return the timeout error.
 */
class HandleSessionReadTimeoutTest {

  // ---------------------------------------------------------------------------
  // sessionReadTimeout() unit tests — no Grid infrastructure needed
  // ---------------------------------------------------------------------------

  @Test
  void noTimeoutCapability_yieldsDefaultReadTimeout() {
    assertThat(HandleSession.sessionReadTimeout(new ImmutableCapabilities()))
        .isEqualTo(ClientConfig.defaultConfig().readTimeout());
  }

  @Test
  void pageLoadTimeout_usedAsReadTimeout() {
    Capabilities caps = new ImmutableCapabilities("timeouts", Map.of("pageLoad", 600_000L));
    assertThat(HandleSession.sessionReadTimeout(caps)).isEqualTo(Duration.ofMillis(600_000));
  }

  @Test
  void integerValues_acceptedInTimeoutsMap() {
    // Some JSON deserializers produce Integer rather than Long for small numbers.
    Capabilities caps = new ImmutableCapabilities("timeouts", Map.of("pageLoad", 300_000));
    assertThat(HandleSession.sessionReadTimeout(caps)).isEqualTo(Duration.ofMillis(300_000));
  }

  @Test
  void capabilitiesDeserializedFromJson_pageLoadExtracted() {
    // Simulate the wire-protocol path: the Grid reads session capabilities from JSON
    // (e.g. from SessionMap storage or Node response). Verify that whatever numeric
    // type Selenium's Json deserializer produces for the pageLoad value is handled correctly.
    String json = "{\"timeouts\":{\"implicit\":0,\"pageLoad\":300000,\"script\":30000}}";
    Map<String, Object> capsMap = new Json().toType(json, Json.MAP_TYPE);
    Capabilities caps = new ImmutableCapabilities(capsMap);
    assertThat(HandleSession.sessionReadTimeout(caps)).isEqualTo(Duration.ofMillis(300_000));
  }

  // ---------------------------------------------------------------------------
  // Integration tests — verify the effective read timeout applied to HttpClient
  // ---------------------------------------------------------------------------

  /**
   * When the session's {@code pageLoad} timeout (10 min) exceeds the Node's own {@code
   * sessionTimeout} (5 min), the Router must use the longer value so it does not cut off the
   * connection before the browser can time out and return a WebDriver error response.
   */
  @Test
  void longerPageLoadTimeout_overridesNodeSessionTimeout() throws Exception {
    URI nodeUri = new URI("http://localhost:4444");

    // Session was created with pageLoad = 10 min (600 s).
    Capabilities caps = new ImmutableCapabilities("timeouts", Map.of("pageLoad", 600_000L));

    // The Node reports sessionTimeout = 5 min (300 s) via /se/grid/node/status.
    long nodeSessionTimeoutMs = 300_000L;

    AtomicReference<Duration> capturedTimeout = new AtomicReference<>();
    HttpClient.Factory factory =
        config -> {
          Duration rt = config.readTimeout();
          // The session-command client is the one whose timeout differs from the default;
          // capture it so we can assert the correct value below.
          if (!rt.equals(ClientConfig.defaultConfig().readTimeout())) {
            capturedTimeout.set(rt);
          }
          return stubClientFor(nodeSessionTimeoutMs);
        };

    runSingleRequest(factory, nodeUri, caps);

    // effective = max(600 s, 300 s) + 30 s buffer = 630 s
    assertThat(capturedTimeout.get())
        .as("read timeout should be pageLoad + buffer when pageLoad > nodeSessionTimeout")
        .isEqualTo(Duration.ofSeconds(630));
  }

  /**
   * When the Node's {@code sessionTimeout} (10 min) exceeds the session's {@code pageLoad} (5 min),
   * the Router uses the larger Node timeout as the lower-bound floor, because the Grid operator has
   * explicitly configured a longer window.
   */
  @Test
  void longerNodeTimeout_usedAsFloor() throws Exception {
    URI nodeUri = new URI("http://localhost:4445");

    // Session was created with pageLoad = 5 min (300 s).
    Capabilities caps = new ImmutableCapabilities("timeouts", Map.of("pageLoad", 300_000L));

    // Node reports a 10-min (600 s) session timeout — operator has extended it.
    long nodeSessionTimeoutMs = 600_000L;

    AtomicReference<Duration> capturedTimeout = new AtomicReference<>();
    HttpClient.Factory factory =
        config -> {
          Duration rt = config.readTimeout();
          if (!rt.equals(ClientConfig.defaultConfig().readTimeout())) {
            capturedTimeout.set(rt);
          }
          return stubClientFor(nodeSessionTimeoutMs);
        };

    runSingleRequest(factory, nodeUri, caps);

    // effective = max(300 s, 600 s) + 30 s buffer = 630 s
    assertThat(capturedTimeout.get())
        .as("read timeout should be nodeSessionTimeout + buffer when node timeout > pageLoad")
        .isEqualTo(Duration.ofSeconds(630));
  }

  /**
   * When the session has no {@code pageLoad} capability, {@link HandleSession#sessionReadTimeout}
   * returns the {@link ClientConfig} default. The Router must still honour the Node's own {@code
   * sessionTimeout} as a floor, so the effective timeout is {@code nodeTimeout + buffer} rather
   * than just the bare ClientConfig default.
   */
  @Test
  void noPageLoadCapability_nodeTimeoutUsedAsFloor() throws Exception {
    URI nodeUri = new URI("http://localhost:4446");

    // Session has no pageLoad capability — sessionReadTimeout() returns the ClientConfig default.
    Capabilities caps = new ImmutableCapabilities();

    // Node reports a 10-min (600 s) session timeout.
    long nodeSessionTimeoutMs = 600_000L;

    AtomicReference<Duration> capturedTimeout = new AtomicReference<>();
    HttpClient.Factory factory =
        config -> {
          Duration rt = config.readTimeout();
          if (!rt.equals(ClientConfig.defaultConfig().readTimeout())) {
            capturedTimeout.set(rt);
          }
          return stubClientFor(nodeSessionTimeoutMs);
        };

    runSingleRequest(factory, nodeUri, caps);

    // effective = max(clientConfigDefault, 600 s) + 30 s buffer = 630 s
    assertThat(capturedTimeout.get())
        .as("read timeout should be nodeSessionTimeout + buffer when pageLoad is absent")
        .isEqualTo(Duration.ofSeconds(630));
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  /**
   * Registers a session in a local SessionMap and executes one GET command through HandleSession.
   */
  private void runSingleRequest(HttpClient.Factory factory, URI nodeUri, Capabilities caps)
      throws Exception {
    Tracer tracer = DefaultTestTracer.createTracer();
    LocalSessionMap sessions = new LocalSessionMap(tracer, new GuavaEventBus());

    SessionId id = new SessionId(UUID.randomUUID());
    sessions.add(new Session(id, nodeUri, new ImmutableCapabilities(), caps, Instant.now()));

    try (HandleSession handler = new HandleSession(tracer, factory, sessions)) {
      handler.execute(new HttpRequest(GET, "/session/" + id + "/url"));
    }
  }

  /**
   * Returns a stub {@link HttpClient} that:
   *
   * <ul>
   *   <li>responds to {@code GET /se/grid/node/status} with a fake {@link
   *       org.openqa.selenium.grid.data.NodeStatus} JSON carrying {@code nodeSessionTimeoutMs};
   *   <li>responds to all other requests with {@code 200 OK}.
   * </ul>
   */
  private static HttpClient stubClientFor(long nodeSessionTimeoutMs) {
    return new HttpClient() {
      @Override
      public HttpResponse execute(HttpRequest req) {
        if (req.getUri().contains("/se/grid/node/status")) {
          String json =
              String.format(
                  "{\"sessionTimeout\":%d,\"availability\":\"UP\","
                      + "\"externalUri\":\"http://localhost:4444\","
                      + "\"nodeId\":\"%s\","
                      + "\"slots\":[],\"maxSessions\":1,\"version\":\"test\","
                      + "\"osInfo\":{}}",
                  nodeSessionTimeoutMs, UUID.randomUUID());
          return new HttpResponse().setContent(Contents.utf8String(json));
        }
        return new HttpResponse();
      }

      @Override
      public WebSocket openSocket(HttpRequest request, WebSocket.Listener listener) {
        throw new UnsupportedOperationException("not used in tests");
      }

      @Override
      public <T>
          java.util.concurrent.CompletableFuture<java.net.http.HttpResponse<T>> sendAsyncNative(
              java.net.http.HttpRequest request,
              java.net.http.HttpResponse.BodyHandler<T> handler) {
        throw new UnsupportedOperationException("not used in tests");
      }

      @Override
      public <T> java.net.http.HttpResponse<T> sendNative(
          java.net.http.HttpRequest request, java.net.http.HttpResponse.BodyHandler<T> handler) {
        throw new UnsupportedOperationException("not used in tests");
      }

      @Override
      public void close() {}
    };
  }
}
TESTFILE

echo "Gold patch applied successfully."
