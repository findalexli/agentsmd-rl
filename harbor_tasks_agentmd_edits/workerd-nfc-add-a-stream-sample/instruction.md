# Add a Web Streams Sample

## Problem

The `samples/` directory has examples for various workerd features (async context, durable objects, eventsource, extensions, etc.) but there is no sample demonstrating the Web Streams API. This is a gap for both users learning to use streams with workerd and for internal testing of streams-related improvements.

## What's Needed

Create a new `samples/web-streams/` directory with a complete working sample that demonstrates:

1. **ReadableStream** — generating text content with both synchronous and asynchronous `pull` callbacks
2. **Byte streams** — using `type: "bytes"` for ReadableStream with BYOB support
3. **TransformStream** — piping a readable stream through a transform (e.g., uppercase conversion)
4. **Sync vs async variants** — showing how both synchronous and asynchronous stream sources/transforms work

The sample should expose these as different HTTP endpoints so users can `curl` each variant.

## Files to Create

- `samples/web-streams/streams-util.js` — stream factory functions (readable, byte, transform)
- `samples/web-streams/worker.js` — worker that routes requests to different stream demos
- `samples/web-streams/config.capnp` — workerd configuration declaring the modules
- `samples/web-streams/README.md` — documentation covering what the sample does, how to run it, and what endpoints are available

After creating the code files, make sure to document the sample thoroughly in a README. The project's CLAUDE.md notes that README.md files provide package/directory-level information, so the README should describe the endpoints, how to run the sample, and how to test it.

## Files to Look At

- `samples/eventsource/` — a similar sample with README, config.capnp, and worker.js for reference on structure
- `CLAUDE.md` — project guidance mentioning sample configurations in `samples/` directory
