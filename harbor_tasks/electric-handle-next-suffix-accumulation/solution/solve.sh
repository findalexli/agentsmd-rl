#!/bin/bash
# Gold solution: applies the upstream PR-3961 fix.
# Resets the syncState handle to undefined when a 409 lacks the shape-handle
# header and tags the next request with a random cache-buster query param,
# instead of mutating the handle by appending -next.
set -euo pipefail

cd /workspace/electric

# Idempotency check: if the patch has already been applied, exit cleanly.
if grep -q '^function createCacheBuster' packages/typescript-client/src/client.ts 2>/dev/null; then
  echo "[solve.sh] patch already applied; skipping"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-handle-next-accumulation.md b/.changeset/fix-handle-next-accumulation.md
new file mode 100644
index 0000000000..318faf2521
--- /dev/null
+++ b/.changeset/fix-handle-next-accumulation.md
@@ -0,0 +1,5 @@
+---
+'@electric-sql/client': patch
+---
+
+Fix unbounded URL growth on 409 retries when a proxy strips the handle header. Instead of appending `-next` to the handle (which grew indefinitely), the client now uses a random `cache-buster` query param to ensure unique retry URLs. Also warns when this fallback fires.
diff --git a/AGENTS.md b/AGENTS.md
index ec160f1ee6..4ca48120dd 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -215,6 +215,10 @@ const bootstrapTodoListAction = createOptimisticAction<string>({
 })
 ```
 
+## Working on the TypeScript client
+
+Before making changes to `packages/typescript-client`, **always read `packages/typescript-client/SPEC.md` first**. It is the single source of truth for the ShapeStream state machine — invariants, constraints, state transitions, and how they're enforced. Design fixes and features around the spec's invariants rather than patching symptoms ad-hoc.
+
 ## Testing
 
 ### Unit testing (mocked)
diff --git a/packages/typescript-client/src/client.ts b/packages/typescript-client/src/client.ts
index edb1991b3a..29675a692b 100644
--- a/packages/typescript-client/src/client.ts
+++ b/packages/typescript-client/src/client.ts
@@ -96,6 +96,10 @@ const RESERVED_PARAMS: Set<ReservedParamKeys> = new Set([
 
 const TROUBLESHOOTING_URL = `https://electric-sql.com/docs/guides/troubleshooting`
 
+function createCacheBuster(): string {
+  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
+}
+
 type Replica = `full` | `default`
 export type LogMode = `changes_only` | `full`
 
@@ -617,6 +621,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
   #fastLoopBackoffMaxMs = 5_000
   #fastLoopConsecutiveCount = 0
   #fastLoopMaxCount = 5
+  #refetchCacheBuster?: string
 
   constructor(options: ShapeStreamOptions<GetExtensions<T>>) {
     this.options = { subscribe: true, ...options }
@@ -875,10 +880,10 @@ export class ShapeStream<T extends Row<unknown> = Row>
       if (!(e instanceof FetchError)) throw e // should never happen
 
       if (e.status == 409) {
-        // Upon receiving a 409, we should start from scratch
-        // with the newly provided shape handle, or a fallback
-        // pseudo-handle based on the current one to act as a
-        // consistent cache buster
+        // Upon receiving a 409, start from scratch with the newly
+        // provided shape handle. If the header is missing (e.g. proxy
+        // stripped it), reset without a handle and use a random
+        // cache-buster query param to ensure the retry URL is unique.
 
         // Store the current shape URL as expired to avoid future 409s
         if (this.#syncState.handle) {
@@ -886,8 +891,14 @@ export class ShapeStream<T extends Row<unknown> = Row>
           expiredShapesCache.markExpired(shapeKey, this.#syncState.handle)
         }
 
-        const newShapeHandle =
-          e.headers[SHAPE_HANDLE_HEADER] || `${this.#syncState.handle!}-next`
+        const newShapeHandle = e.headers[SHAPE_HANDLE_HEADER]
+        if (!newShapeHandle) {
+          console.warn(
+            `[Electric] Received 409 response without a shape handle header. ` +
+              `This likely indicates a proxy or CDN stripping required headers.`
+          )
+          this.#refetchCacheBuster = createCacheBuster()
+        }
         this.#reset(newShapeHandle)
 
         // must refetch control message might be in a list or not depending
@@ -1144,6 +1155,16 @@ export class ShapeStream<T extends Row<unknown> = Row>
       fetchUrl.searchParams.set(EXPIRED_HANDLE_QUERY_PARAM, expiredHandle)
     }
 
+    // Add one-shot cache buster when a 409 response lacked a handle header
+    // (e.g. proxy stripped it). Ensures each retry has a unique URL.
+    if (this.#refetchCacheBuster) {
+      fetchUrl.searchParams.set(
+        CACHE_BUSTER_QUERY_PARAM,
+        this.#refetchCacheBuster
+      )
+      this.#refetchCacheBuster = undefined
+    }
+
     // sort query params in-place for stable URLs and improved cache hits
     fetchUrl.searchParams.sort()
 
@@ -1199,8 +1220,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
       expiredHandle,
       now: Date.now(),
       maxStaleCacheRetries: this.#maxStaleCacheRetries,
-      createCacheBuster: () =>
-        `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
+      createCacheBuster,
     })
 
     this.#syncState = transition.state
@@ -1786,8 +1806,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
           expiredHandle: null,
           now: Date.now(),
           maxStaleCacheRetries: this.#maxStaleCacheRetries,
-          createCacheBuster: () =>
-            `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
+          createCacheBuster,
         })
         if (transition.action === `accepted`) {
           this.#syncState = transition.state
@@ -1869,9 +1888,16 @@ export class ShapeStream<T extends Row<unknown> = Row>
 
         // For snapshot 409s, only update the handle — don't reset offset/schema/etc.
         // The main stream is paused and should not be disturbed.
-        const nextHandle =
-          e.headers[SHAPE_HANDLE_HEADER] || `${usedHandle ?? `handle`}-next`
-        this.#syncState = this.#syncState.withHandle(nextHandle)
+        const nextHandle = e.headers[SHAPE_HANDLE_HEADER]
+        if (nextHandle) {
+          this.#syncState = this.#syncState.withHandle(nextHandle)
+        } else {
+          console.warn(
+            `[Electric] Received 409 response without a shape handle header. ` +
+              `This likely indicates a proxy or CDN stripping required headers.`
+          )
+          this.#refetchCacheBuster = createCacheBuster()
+        }
 
         return this.fetchSnapshot(opts)
       }
diff --git a/packages/typescript-client/test/expired-shapes-cache.test.ts b/packages/typescript-client/test/expired-shapes-cache.test.ts
index 087dab3cdb..dad9b77f13 100644
--- a/packages/typescript-client/test/expired-shapes-cache.test.ts
+++ b/packages/typescript-client/test/expired-shapes-cache.test.ts
@@ -726,4 +726,144 @@ describe(`ExpiredShapesCache`, () => {
     expect(errors).toHaveLength(0)
     expect(fetchCount).toBeGreaterThan(1) // should keep fetching, not crash
   })
+
+  it(`should use cache buster instead of handle mutation on 409 without handle header`, async () => {
+    // Regression test for ELECTRIC-4GV: When a proxy strips the handle header
+    // from 409 responses, the client must use a random cache-buster query param
+    // to ensure unique URLs on retries, rather than mutating the handle.
+
+    let requestCount = 0
+    const capturedUrls: string[] = []
+    const maxRequests = 10
+
+    fetchMock.mockImplementation((input: RequestInfo | URL) => {
+      requestCount++
+      capturedUrls.push(input.toString())
+
+      if (requestCount >= maxRequests) {
+        aborter.abort()
+        return Promise.resolve(
+          new Response(JSON.stringify([]), {
+            status: 200,
+            headers: {
+              'electric-handle': `final-handle`,
+              'electric-offset': `0_0`,
+              'electric-schema': `{}`,
+              'electric-cursor': `cursor-1`,
+            },
+          })
+        )
+      }
+
+      // Return 409 WITHOUT a handle header — simulating a proxy that strips it
+      return Promise.resolve(
+        new Response(`[]`, {
+          status: 409,
+        })
+      )
+    })
+
+    const stream = new ShapeStream({
+      url: shapeUrl,
+      params: { table: `test` },
+      handle: `original-handle`,
+      signal: aborter.signal,
+      fetchClient: fetchMock,
+      subscribe: false,
+    })
+
+    stream.subscribe(() => {})
+
+    await new Promise((resolve) => setTimeout(resolve, 500))
+
+    // Invariant: no URL should contain "-next" in any parameter
+    for (const urlStr of capturedUrls) {
+      expect(urlStr, `URL contains "-next": ${urlStr}`).not.toContain(`-next`)
+    }
+
+    // Invariant: after the first 409, retries should include a cache-buster param
+    const urlsAfterFirst = capturedUrls.slice(1)
+    for (const urlStr of urlsAfterFirst) {
+      const url = new URL(urlStr)
+      const hasCacheBuster = url.searchParams.has(`cache-buster`)
+      const hasExpiredHandle = url.searchParams.has(`expired_handle`)
+      // URL uniqueness comes from either cache-buster or expired_handle
+      expect(
+        hasCacheBuster || hasExpiredHandle,
+        `Retry URL lacks cache-buster and expired_handle: ${urlStr}`
+      ).toBe(true)
+    }
+
+    // Invariant: all retry URLs must be unique (no identical URLs)
+    const uniqueUrls = new Set(capturedUrls)
+    expect(
+      uniqueUrls.size,
+      `Expected ${capturedUrls.length} unique URLs but got ${uniqueUrls.size}`
+    ).toBe(capturedUrls.length)
+  })
+
+  it(`should use cache buster on 409 without handle header when initial handle is undefined`, async () => {
+    // Regression test for ELECTRIC-4GV Pattern A: client never received a
+    // valid handle. Previously produced "undefined-next-next-next..." because
+    // the non-null assertion stringified undefined.
+
+    let requestCount = 0
+    const capturedUrls: string[] = []
+    const maxRequests = 10
+
+    fetchMock.mockImplementation((input: RequestInfo | URL) => {
+      requestCount++
+      capturedUrls.push(input.toString())
+
+      if (requestCount >= maxRequests) {
+        aborter.abort()
+        return Promise.resolve(
+          new Response(JSON.stringify([]), {
+            status: 200,
+            headers: {
+              'electric-handle': `final-handle`,
+              'electric-offset': `0_0`,
+              'electric-schema': `{}`,
+              'electric-cursor': `cursor-1`,
+            },
+          })
+        )
+      }
+
+      // Return 409 WITHOUT a handle header
+      return Promise.resolve(
+        new Response(`[]`, {
+          status: 409,
+        })
+      )
+    })
+
+    // No handle provided — simulates a client that never received one
+    const stream = new ShapeStream({
+      url: shapeUrl,
+      params: { table: `test` },
+      signal: aborter.signal,
+      fetchClient: fetchMock,
+      subscribe: false,
+    })
+
+    stream.subscribe(() => {})
+
+    await new Promise((resolve) => setTimeout(resolve, 500))
+
+    // Invariant: no URL should contain "undefined" or "-next"
+    for (const urlStr of capturedUrls) {
+      expect(urlStr, `URL contains "undefined": ${urlStr}`).not.toContain(
+        `undefined`
+      )
+      expect(urlStr, `URL contains "-next": ${urlStr}`).not.toContain(`-next`)
+    }
+
+    // Invariant: all retry URLs must be unique
+    const uniqueUrls = new Set(capturedUrls)
+    expect(
+      uniqueUrls.size,
+      `Expected ${capturedUrls.length} unique URLs but got ${uniqueUrls.size}`
+    ).toBe(capturedUrls.length)
+  })
 })
diff --git a/packages/typescript-client/test/shape-stream-state.test.ts b/packages/typescript-client/test/shape-stream-state.test.ts
index a2c716019b..865ea8bec5 100644
--- a/packages/typescript-client/test/shape-stream-state.test.ts
+++ b/packages/typescript-client/test/shape-stream-state.test.ts
@@ -398,6 +398,38 @@ describe(`shape stream state machine`, () => {
     expect(state.isUpToDate).toBe(false)
   })
 
+  // 22b. markMustRefetch without handle (409 with missing header)
+  it(`markMustRefetch without handle resets to InitialState with undefined handle`, () => {
+    const { state } = scenario()
+      .response({ responseHandle: `h1`, now: 12345 })
+      .expectKind(`syncing`)
+      .messages({ now: 12345 })
+      .expectKind(`live`)
+      .markMustRefetch()
+      .expectKind(`initial`)
+      .expectOffset(`-1`)
+      .done()
+
+    expect(state.handle).toBeUndefined()
+    expect(state.liveCacheBuster).toBe(``)
+    expect(state.lastSyncedAt).toBe(12345)
+    expect(state.schema).toBe(undefined)
+  })
+
+  // 22c. InitialState from markMustRefetch(undefined) omits handle in URL params
+  it(`InitialState without handle omits handle from URL params`, () => {
+    const { state } = scenario()
+      .response({ responseHandle: `h1` })
+      .expectKind(`syncing`)
+      .markMustRefetch()
+      .expectKind(`initial`)
+      .done()
+
+    const params = applyAndGetParams(state)
+    expect(params.has(SHAPE_HANDLE_QUERY_PARAM)).toBe(false)
+    expect(params.get(OFFSET_QUERY_PARAM)).toBe(`-1`)
+  })
+
   // 23. StaleRetryState → SyncingState on successful response
   it(`StaleRetryState → SyncingState on successful response`, () => {
     const { state } = scenario()
@@ -1193,6 +1225,17 @@ describe(`algebraic properties`, () => {
     }
   )
 
+  it.each(allStates)(
+    `markMustRefetch(undefined) produces InitialState with no handle ($kind)`,
+    ({ state }) => {
+      const fresh = state.markMustRefetch()
+      assertStateInvariants(fresh)
+      expect(fresh).toBeInstanceOf(InitialState)
+      expect(fresh.offset).toBe(`-1`)
+      expect(fresh.handle).toBeUndefined()
+    }
+  )
+
   it.each(allStates)(
     `PausedState.pause() is idempotent ($kind)`,
     ({ state }) => {
PATCH

echo "[solve.sh] gold patch applied"
