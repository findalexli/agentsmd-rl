# Selenium Grid Router Timeout Issue

## Problem

The Selenium Grid Router is prematurely closing connections when sessions have long `pageLoad` timeouts configured in their WebDriver capabilities.

When a browser session is created with a high pageLoad timeout (e.g., 10 minutes for slow-loading pages), the Router should wait at least that long before timing out the HTTP connection. Currently, the Router ignores the session's pageLoad capability when determining its read timeout, causing legitimate long-running navigations to be cut off.

## Observed Behavior

1. User creates a WebDriver session with `timeouts.pageLoad = 600000` (10 minutes)
2. User navigates to a slow-loading page that takes 8 minutes to load
3. After approximately 3 minutes (the default timeout), the Router closes the connection
4. The browser navigation succeeds, but the client receives a connection timeout error

## Expected Behavior

Modify `java/src/org/openqa/selenium/grid/router/HandleSession.java` to correctly align the Router-Node read timeout with the session's `pageLoad` capability. Specifically:

### 1. `sessionReadTimeout` method

Add a `static Duration sessionReadTimeout(Capabilities caps)` method that:
- Reads the `"timeouts"` capability using `getCapability("timeouts")`
- Extracts the `"pageLoad"` value from the timeouts map
- Returns the corresponding `Duration`

### 2. `longFrom` helper method

Add a `longFrom` helper method to safely convert capability values to `long`. It must handle values that are `instanceof Long` or `instanceof Number` (JSON deserializers may produce either type for numeric capability values).

### 3. `READ_TIMEOUT_BUFFER` constant

Add a constant named `READ_TIMEOUT_BUFFER` set to `Duration.ofSeconds(30)`. This buffer ensures the node has time to return a timeout error before the Router gives up on the connection.

### 4. `fetchNodeTimeout` method

Rename/refactor the existing node timeout fetching logic into a method named `fetchNodeTimeout` that returns `Optional<Duration>`. Returning an `Optional` allows the caller to skip caching on a failed fetch, so the next command will retry rather than permanently caching a fallback value. The method should return `Optional.of(...)` on success and `Optional.empty()` on failure.

### 5. `nodeTimeoutCache` field

Add a field named `nodeTimeoutCache` of type `ConcurrentMap<URI, Duration>` to cache the node's configured session timeout fetched from `/se/grid/node/status`. This reduces redundant status calls.

### 6. Effective timeout calculation

Compute the effective read timeout as:

```
max(sessionReadTimeout, nodeTimeout) + READ_TIMEOUT_BUFFER
```

Use `.compareTo(nodeTimeout)` to compare durations and `.plus(READ_TIMEOUT_BUFFER)` to add the buffer.

### 7. `NodeClientKey` inner class

Add an inner class named `NodeClientKey` that acts as the cache key for HTTP clients. It must have:
- `private final URI uri`
- `private final Duration readTimeout`
- `public boolean equals(Object ...)` implementation
- `public int hashCode()` implementation

### 8. `httpClients` map type change

Change the `httpClients` map type from `ConcurrentMap<URI, CacheEntry>` to `ConcurrentMap<NodeClientKey, CacheEntry>` so sessions with different pageLoad timeouts get separate HTTP clients.

## Constraints

- The solution must compile and pass Bazel build for `//java/src/org/openqa/selenium/grid/router:router`
- Code must be formatted with google-java-format
- `HandleSession` must continue to implement `HttpHandler` and `Closeable` and expose `public HttpResponse execute(HttpRequest req)`
- `cleanUpHttpClientsCacheService` must remain present for cache cleanup
