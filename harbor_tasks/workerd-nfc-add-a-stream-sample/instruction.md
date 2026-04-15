# Add a Web Streams Sample

## Problem

The `samples/` directory has examples for various workerd features (async context, durable objects, eventsource, extensions, etc.) but there is no sample demonstrating the Web Streams API. This is a gap for both users learning to use streams with workerd and for internal testing of streams-related improvements.

## What's Needed

Create a new `samples/web-streams/` directory with a complete working sample that demonstrates Web Streams API patterns using lorem ipsum-style text generation.

### Files to Create

- `samples/web-streams/streams-util.js` — stream factory functions (readable, byte, transform)
- `samples/web-streams/worker.js` — worker that routes requests to different stream demos
- `samples/web-streams/config.capnp` — workerd configuration declaring the modules
- `samples/web-streams/README.md` — documentation covering what the sample does, how to run it, and what endpoints are available

### Required Exports from `streams-util.js`

The module must export the following six functions using `export function` declarations:

- **`createSyncLoremStream(numChunks)`** — Creates a `ReadableStream` that generates lorem ipsum-style text synchronously. When called with `N`, it must yield exactly `N` chunks, each a non-empty `Uint8Array`. For example, `createSyncLoremStream(5)` must produce exactly 5 chunks with a total byte length greater than 100.

- **`createAsyncLoremStream(numChunks)`** — Same as `createSyncLoremStream` but uses an asynchronous `pull` callback (e.g., with `await` / promises).

- **`createSyncLoremByteStream(numChunks)`** — Creates a byte-type `ReadableStream` (constructed with `type: "bytes"`) that supports BYOB (Bring Your Own Buffer) reads via `reader.read(new Uint8Array(...))`. Calling with `N` must produce at least 1 chunk with total content exceeding 50 bytes for `N=3`.

- **`createAsyncLoremByteStream(numChunks)`** — Same as `createSyncLoremByteStream` but uses an asynchronous `pull` callback.

- **`createSyncUppercaseTransform()`** — Creates a `TransformStream` that converts all alphabetic characters to uppercase when a readable stream is piped through it via `pipeThrough()`. After transformation, the output must contain no lowercase letters (`/[a-z]/` must not match) and must contain uppercase letters (`/[A-Z]/` must match).

- **`createAsyncUppercaseTransform()`** — Same as `createSyncUppercaseTransform` but uses asynchronous `transform` and `flush` callbacks.

### `worker.js` Requirements

- Must be a valid ES module
- Must import from the `"streams-util"` module
- Must export a default object with an `async fetch(request)` handler
- Should route requests to different stream demo endpoints (e.g., `/sync`, `/async`, `/bytes/sync`, `/bytes/async`)

### `config.capnp` Requirements

- Must use the Workerd schema (i.e., `using Workerd = import "/workerd/workerd.capnp"`)
- Must declare both the `worker` and `streams-util` modules as ES modules

### `README.md` Requirements

- Must have a markdown title header (line starting with `#`)
- Must reference `config.capnp` in running instructions
- Should document the available endpoints and how to test them

## Files to Look At

- `samples/eventsource/` — a similar sample with README, config.capnp, and worker.js for reference on structure
- `CLAUDE.md` — project guidance mentioning sample configurations in `samples/` directory
