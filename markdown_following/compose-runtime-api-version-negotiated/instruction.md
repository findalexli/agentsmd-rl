# Use the negotiated Docker API version for request shaping

## Background

`pkg/compose/` contains a helper that looks up the Docker daemon's API version
once and caches it for subsequent calls. The current implementation has three
related problems that surface when Compose builds container-create payloads:

1. **It returns the wrong version.** The helper currently calls
   `apiClient().ServerVersion(ctx, ...)` and returns the daemon's *raw maximum*
   API version. But the Docker client SDK negotiates an *effective* API
   version with the daemon (it may be lower than the server's maximum, e.g.
   when the SDK is older than the daemon). Request shaping — for example,
   the `mount.TypeImage` validation in `buildContainerVolumes`, and the
   container-create payload in `getCreateConfigs` — must follow the
   *negotiated* version, because that's what the daemon uses to validate
   incoming requests on the wire. Today, with the server reporting a higher
   API version than the SDK negotiated, Compose composes payloads that the
   daemon rejects.

2. **Errors poison the cache forever.** The cache is built on `sync.Once`,
   so if the very first lookup fails (e.g., a transient `context deadline
   exceeded`), every subsequent call returns the same cached error and never
   retries — even with a fresh, healthy context. Errors must NOT be cached;
   only successful lookups should be.

3. **The cache is process-global, not per-service.** It lives on a
   package-level `var runtimeVersion runtimeVersionCache`. Two
   `composeService` instances configured against different daemons would
   incorrectly share the cached version. The cache must live on each
   `composeService` instance.

## What you need to deliver

Reshape the runtime-version helper so that, when Compose decides how to
shape a request to the daemon, it looks up and caches **the negotiated client
API version** rather than the server's raw maximum.

### Contract

Add (or replace the existing helper with) a method on `*composeService`
with this exact signature:

```go
func (s *composeService) RuntimeAPIVersion(ctx context.Context) (string, error)
```

(The exported name `RuntimeAPIVersion` matters — it's the name request-shaping
callers will use, and it's the name pre-existing callers in the package must
be updated to call.)

### Behavior the method must satisfy

- It obtains the version by triggering API negotiation through the Docker
  SDK — i.e. `apiClient.Ping(ctx, client.PingOptions{NegotiateAPIVersion: true})` —
  and then reads `apiClient.ClientVersion()`. It must NOT use
  `ServerVersion(...).APIVersion`. If `ClientVersion()` returns the empty
  string after a successful negotiated ping, the helper must return an
  error rather than caching an empty value.
- The successful negotiated value must be cached so that subsequent calls
  return the cached string without re-pinging the daemon.
- Errors must not be cached: a transient failure (e.g. a Ping that returns
  `context.DeadlineExceeded`) followed by a successful retry on a fresh
  context must succeed and cache the new value.
- The cache must be a field on `composeService`, not a package-level variable.
  Two distinct `composeService` instances must negotiate independently.
- Existing call sites in `pkg/compose/` that previously read the daemon's
  raw API version for *request shaping* must be updated to call this helper.
- Concurrency: concurrent calls to the method on the same service must be
  safe (no torn writes to the cached value, no double-negotiation race
  that would cache a stale value).

## Constraints

- The Docker SDK's `client.Client` exposes `Ping(ctx, opts)` and
  `ClientVersion()`. Use these — do NOT add a new dependency.

## Code Style Requirements

The repo enforces several style rules via `golangci-lint v2` (config in
`.golangci.yml`). Code that does not meet them will fail
`go vet ./pkg/compose/...`:

- **Pointer receivers when the struct embeds a mutex.** If you add a
  `sync.Mutex` (directly or via an embedded cache type) to `composeService`,
  every method on `composeService` — not just the new ones — must use a
  pointer receiver. Value receivers on a struct containing a mutex are
  flagged by `go vet` (`copylocks`). This affects more files in
  `pkg/compose/` than just the file you change to add the helper.
- **No banned imports.** Do not import `io/ioutil`, `github.com/pkg/errors`,
  `gopkg.in/yaml.v2`, `golang.org/x/exp/maps`, or `golang.org/x/exp/slices`.
  Use `github.com/containerd/errdefs` rather than
  `github.com/docker/docker/errdefs`.
- **Tests use `t.Context()`** instead of `context.Background()` or
  `context.TODO()`.
- **Formatting** is enforced by `gofumpt` + `gci` (stdlib, third-party,
  local module import groups).

## Definition of done

- `go build ./pkg/compose/...` succeeds.
- `go vet ./pkg/compose/...` is clean.
- The helper's behavior matches the four properties above (negotiated
  version returned, success cached, error not cached, per-instance cache).
- Existing tests in the package continue to pass. If any pre-existing
  test seeds the old helper through its mock setup, update that mock
  setup to match the new negotiation path.
