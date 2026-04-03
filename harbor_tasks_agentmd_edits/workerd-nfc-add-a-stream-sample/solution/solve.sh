#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if [ -f samples/web-streams/streams-util.js ]; then
    echo "Patch already applied."
    exit 0
fi

mkdir -p samples/web-streams

cat > samples/web-streams/README.md <<'READMEOF'
# Web Streams Example

Demonstrates Web Streams API features including custom ReadableStream, TransformStream,
and byte streams.

## Endpoints

- `/sync` - Default stream with uppercase transform (synchronous)
- `/async` - Default stream with uppercase transform (with delays)
- `/bytes/sync` - Byte stream, no transform (synchronous)
- `/bytes/async` - Byte stream, no transform (with delays)

## Running

```sh
$ bazel run //src/workerd/server:workerd -- serve $(pwd)/samples/web-streams/config.capnp
```

Or with a local workerd binary:

```sh
$ ./workerd serve config.capnp
```

## Testing

```sh
$ curl http://localhost:8080/sync
$ curl http://localhost:8080/async
$ curl http://localhost:8080/bytes/sync
$ curl http://localhost:8080/bytes/async
```
READMEOF

cat > samples/web-streams/config.capnp <<'CAPNPEOF'
# Copyright (c) 2017-2026 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at:
#     https://opensource.org/licenses/Apache-2.0

using Workerd = import "/workerd/workerd.capnp";

const webStreamsExample :Workerd.Config = (
  services = [ (name = "main", worker = .webStreams) ],
  sockets = [ ( name = "http", address = "*:8080", http = (), service = "main" ) ]
);

const webStreams :Workerd.Worker = (
  modules = [
    (name = "worker", esModule = embed "worker.js"),
    (name = "streams-util", esModule = embed "streams-util.js")
  ],
  compatibilityDate = "2025-12-31",
);
CAPNPEOF

cat > samples/web-streams/streams-util.js <<'JSEOF'
// Copyright (c) 2017-2024 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

// Future work: Additional stream patterns to demonstrate
// - Tee: Split a stream with readable.tee()
// - Chained transforms: Multiple TransformStreams piped together
// - Built-in streams: CompressionStream, TextEncoderStream/TextDecoderStream
// - Request body consumption: Pipe incoming POST body through transforms
// - BYOB reading: Demonstrate "bring your own buffer" with byte streams

// Sample words for generating lorem ipsum-style text
const WORDS = [
  "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
  "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
  "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
  "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
  "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
  "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
  "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
  "deserunt", "mollit", "anim", "id", "est", "laborum"
];

const enc = new TextEncoder();

function generateChunk() {
  const wordsPerChunk = 50 + Math.floor(Math.random() * 50);
  const words = [];
  for (let i = 0; i < wordsPerChunk; i++) {
    words.push(WORDS[Math.floor(Math.random() * WORDS.length)]);
  }
  return enc.encode(words.join(" ") + "\n\n");
}

// Creates a ReadableStream that generates random lorem ipsum-style text synchronously
export function createSyncLoremStream(numChunks) {
  let chunksRemaining = numChunks;

  return new ReadableStream({
    pull(controller) {
      if (chunksRemaining <= 0) {
        controller.close();
        return;
      }
      controller.enqueue(generateChunk());
      chunksRemaining--;
    }
  }, { highWaterMark: 16 });
}

// Creates a ReadableStream that generates random lorem ipsum-style text asynchronously
export function createAsyncLoremStream(numChunks) {
  let chunksRemaining = numChunks;

  return new ReadableStream({
    async pull(controller) {
      if (chunksRemaining <= 0) {
        controller.close();
        return;
      }
      await scheduler.wait(10);
      controller.enqueue(generateChunk());
      chunksRemaining--;
    }
  }, { highWaterMark: 16 });
}

// Creates a byte ReadableStream that generates random lorem ipsum-style text synchronously
export function createSyncLoremByteStream(numChunks) {
  let chunksRemaining = numChunks;

  return new ReadableStream({
    type: "bytes",
    pull(controller) {
      if (chunksRemaining <= 0) {
        controller.close();
        return;
      }
      controller.enqueue(generateChunk());
      chunksRemaining--;
    }
  }, { highWaterMark: 16 * 1024 });
}

// Creates a byte ReadableStream that generates random lorem ipsum-style text asynchronously
export function createAsyncLoremByteStream(numChunks) {
  let chunksRemaining = numChunks;

  return new ReadableStream({
    type: "bytes",
    async pull(controller) {
      if (chunksRemaining <= 0) {
        controller.close();
        return;
      }
      await scheduler.wait(10);
      controller.enqueue(generateChunk());
      chunksRemaining--;
    }
  }, { highWaterMark: 16 * 1024 });
}

// Creates a TransformStream that converts text to uppercase synchronously
export function createSyncUppercaseTransform() {
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();

  return new TransformStream({
    transform(chunk, controller) {
      const text = decoder.decode(chunk, { stream: true });
      controller.enqueue(encoder.encode(text.toUpperCase()));
    },
    flush(controller) {
      const remaining = decoder.decode();
      if (remaining) {
        controller.enqueue(encoder.encode(remaining.toUpperCase()));
      }
    }
  });
}

// Creates a TransformStream that converts text to uppercase asynchronously
export function createAsyncUppercaseTransform() {
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();

  return new TransformStream({
    async transform(chunk, controller) {
      await scheduler.wait(10);
      const text = decoder.decode(chunk, { stream: true });
      controller.enqueue(encoder.encode(text.toUpperCase()));
    },
    async flush(controller) {
      await scheduler.wait(10);
      const remaining = decoder.decode();
      if (remaining) {
        controller.enqueue(encoder.encode(remaining.toUpperCase()));
      }
    }
  });
}
JSEOF

cat > samples/web-streams/worker.js <<'WORKEREOF'
// Copyright (c) 2017-2024 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0

import {
  createSyncLoremStream,
  createAsyncLoremStream,
  createSyncLoremByteStream,
  createAsyncLoremByteStream,
  createSyncUppercaseTransform,
  createAsyncUppercaseTransform
} from "streams-util";

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Byte stream variants (no transform, returned directly)
    if (url.pathname === "/bytes/sync") {
      return new Response(createSyncLoremByteStream(20), {
        headers: { "Content-Type": "text/plain; charset=utf-8" }
      });
    }
    if (url.pathname === "/bytes/async") {
      return new Response(createAsyncLoremByteStream(20), {
        headers: { "Content-Type": "text/plain; charset=utf-8" }
      });
    }

    // Default stream variants with uppercase transform
    let loremStream;
    let transform;
    if (url.pathname === "/sync") {
      loremStream = createSyncLoremStream(20);
      transform = createSyncUppercaseTransform();
    } else if (url.pathname === "/async") {
      loremStream = createAsyncLoremStream(20);
      transform = createAsyncUppercaseTransform();
    } else {
      return new Response("Use /sync, /async, /bytes/sync, or /bytes/async\n", { status: 404 });
    }

    const transformedStream = loremStream.pipeThrough(transform);

    return new Response(transformedStream, {
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
};
WORKEREOF

echo "Patch applied successfully."
