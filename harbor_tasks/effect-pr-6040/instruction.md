# Fix Stream.decodeText for multi-byte UTF-8 chunk boundaries

## Symptom

`Stream.decodeText` produces incorrect output when decoding multi-byte UTF-8 characters that are split across two or more Stream chunks.

For example, given a Stream that yields chunks containing the bytes of a multi-byte character like the 🌍 emoji (4 bytes: `F0 9F 8C 8D`):

```ts
const bytes = new TextEncoder().encode("🌍");
const stream = Stream.fromChunks(
  Chunk.of(bytes.slice(0, 2)),  // first half: F0 9F
  Chunk.of(bytes.slice(2, 4))   // second half: 8C 8D
);
const result = pipe(stream, Stream.decodeText(), Stream.mkString);
// Expected: "🌍"
// Actual (buggy): wrong characters or replacement symbols
```

The same issue affects any mix of ASCII and multi-byte content where a character boundary falls across chunks, e.g. `"Hello 🌍!"` split mid-character.

## Task

Find and fix `Stream.decodeText` so that multi-byte UTF-8 sequences split across chunks are decoded correctly. The fix should be in `packages/effect/src/internal/stream.ts`.

## Verification

After fixing, verify that:
1. A 4-byte emoji split into two 2-byte chunks decodes correctly to the single character
2. Mixed ASCII and multi-byte content with boundaries at chunk edges decodes correctly
3. The existing `pnpm check` (type checking) and `pnpm lint` still pass