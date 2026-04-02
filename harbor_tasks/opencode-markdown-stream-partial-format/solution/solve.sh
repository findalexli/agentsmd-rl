#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check: if markdown-stream.ts already exists, skip
if [ -f packages/ui/src/components/markdown-stream.ts ]; then
    echo "Patch already applied."
    exit 0
fi

# ── 1. Create packages/ui/src/components/markdown-stream.ts ──────────────────
cat > packages/ui/src/components/markdown-stream.ts <<'TSEOF'
import { marked, type Tokens } from "marked"
import remend from "remend"

export type Block = {
  raw: string
  src: string
  mode: "full" | "live"
}

function refs(text: string) {
  return /^\[[^\]]+\]:\s+\S+/m.test(text) || /^\[\^[^\]]+\]:\s+/m.test(text)
}

function open(raw: string) {
  const match = raw.match(/^[ \t]{0,3}(`{3,}|~{3,})/)
  if (!match) return false
  const mark = match[1]
  if (!mark) return false
  const char = mark[0]
  const size = mark.length
  const last = raw.trimEnd().split("\n").at(-1)?.trim() ?? ""
  return !new RegExp(`^[\\t ]{0,3}${char}{${size},}[\\t ]*$`).test(last)
}

function heal(text: string) {
  return remend(text, { linkMode: "text-only" })
}

export function stream(text: string, live: boolean) {
  if (!live) return [{ raw: text, src: text, mode: "full" }] satisfies Block[]
  const src = heal(text)
  if (refs(text)) return [{ raw: text, src, mode: "live" }] satisfies Block[]
  const tokens = marked.lexer(text)
  const tail = tokens.findLastIndex((token) => token.type !== "space")
  if (tail < 0) return [{ raw: text, src, mode: "live" }] satisfies Block[]
  const last = tokens[tail]
  if (!last || last.type !== "code") return [{ raw: text, src, mode: "live" }] satisfies Block[]
  const code = last as Tokens.Code
  if (!open(code.raw)) return [{ raw: text, src, mode: "live" }] satisfies Block[]
  const head = tokens
    .slice(0, tail)
    .map((token) => token.raw)
    .join("")
  if (!head) return [{ raw: code.raw, src: code.raw, mode: "live" }] satisfies Block[]
  return [
    { raw: head, src: heal(head), mode: "live" },
    { raw: code.raw, src: code.raw, mode: "live" },
  ] satisfies Block[]
}
TSEOF

# ── 2. Create packages/ui/src/components/markdown-stream.test.ts ─────────────
cat > packages/ui/src/components/markdown-stream.test.ts <<'TSEOF'
import { describe, expect, test } from "bun:test"
import { stream } from "./markdown-stream"

describe("markdown stream", () => {
  test("heals incomplete emphasis while streaming", () => {
    expect(stream("hello **world", true)).toEqual([{ raw: "hello **world", src: "hello **world**", mode: "live" }])
    expect(stream("say `code", true)).toEqual([{ raw: "say `code", src: "say `code`", mode: "live" }])
  })

  test("keeps incomplete links non-clickable until they finish", () => {
    expect(stream("see [docs](https://example.com/gu", true)).toEqual([
      { raw: "see [docs](https://example.com/gu", src: "see docs", mode: "live" },
    ])
  })

  test("splits an unfinished trailing code fence from stable content", () => {
    expect(stream("before\n\n```ts\nconst x = 1", true)).toEqual([
      { raw: "before\n\n", src: "before\n\n", mode: "live" },
      { raw: "```ts\nconst x = 1", src: "```ts\nconst x = 1", mode: "live" },
    ])
  })

  test("keeps reference-style markdown as one block", () => {
    expect(stream("[docs][1]\n\n[1]: https://example.com", true)).toEqual([
      {
        raw: "[docs][1]\n\n[1]: https://example.com",
        src: "[docs][1]\n\n[1]: https://example.com",
        mode: "live",
      },
    ])
  })
})
TSEOF

# ── 3. Patch markdown.tsx (source-only, no lock file changes) ─────────────────
git apply - <<'PATCH'
diff --git a/packages/ui/src/components/markdown.tsx b/packages/ui/src/components/markdown.tsx
index ce6bdb7e0d8b..ceab10df98ac 100644
--- a/packages/ui/src/components/markdown.tsx
+++ b/packages/ui/src/components/markdown.tsx
@@ -2,10 +2,10 @@ import { useMarked } from "../context/marked"
 import { useI18n } from "../context/i18n"
 import DOMPurify from "dompurify"
 import morphdom from "morphdom"
-import { marked, type Tokens } from "marked"
 import { checksum } from "@opencode-ai/util/encode"
 import { ComponentProps, createEffect, createResource, createSignal, onCleanup, splitProps } from "solid-js"
 import { isServer } from "solid-js/web"
+import { stream } from "./markdown-stream"

 type Entry = {
   hash: string
@@ -58,47 +58,6 @@ function fallback(markdown: string) {
   return escape(markdown).replace(/\r\n?/g, "\n").replace(/\n/g, "<br>")
 }

-type Block = {
-  raw: string
-  mode: "full" | "live"
-}
-
-function references(markdown: string) {
-  return /^\[[^\]]+\]:\s+\S+/m.test(markdown) || /^\[\^[^\]]+\]:\s+/m.test(markdown)
-}
-
-function incomplete(raw: string) {
-  const match = raw.match(/^[ \t]{0,3}(`{3,}|~{3,})/)
-  if (!match) return false
-  const mark = match[1]
-  if (!mark) return false
-  const char = mark[0]
-  const size = mark.length
-  const last = raw.trimEnd().split("\n").at(-1)?.trim() ?? ""
-  return !new RegExp(`^[\\t ]{0,3}${char}{${size},}[\\t ]*$`).test(last)
-}
-
-function blocks(markdown: string, streaming: boolean) {
-  if (!streaming || references(markdown)) return [{ raw: markdown, mode: "full" }] satisfies Block[]
-  const tokens = marked.lexer(markdown)
-  const last = tokens.findLast((token) => token.type !== "space")
-  if (!last || last.type !== "code") return [{ raw: markdown, mode: "full" }] satisfies Block[]
-  const code = last as Tokens.Code
-  if (!incomplete(code.raw)) return [{ raw: markdown, mode: "full" }] satisfies Block[]
-  const head = tokens
-    .slice(
-      0,
-      tokens.findLastIndex((token) => token.type !== "space"),
-    )
-    .map((token) => token.raw)
-    .join("")
-  if (!head) return [{ raw: code.raw, mode: "live" }] satisfies Block[]
-  return [
-    { raw: head, mode: "full" },
-    { raw: code.raw, mode: "live" },
-  ] satisfies Block[]
-}
-
 type CopyLabels = {
   copy: string
   copied: string
@@ -251,8 +210,6 @@ function setupCodeCopy(root: HTMLDivElement, getLabels: () => CopyLabels) {
     timeouts.set(button, timeout)
   }

-  decorate(root, getLabels())
-
   const buttons = Array.from(root.querySelectorAll('[data-slot="markdown-copy-button"]'))
   for (const button of buttons) {
     if (button instanceof HTMLButtonElement) updateLabel(button)
@@ -304,7 +261,7 @@ export function Markdown(

       const base = src.key ?? checksum(src.text)
       return Promise.all(
-        blocks(src.text, src.streaming).map(async (block, index) => {
+        stream(src.text, src.streaming).map(async (block, index) => {
           const hash = checksum(block.raw)
           const key = base ? `${base}:${index}:${block.mode}` : hash

@@ -316,7 +273,7 @@ export function Markdown(
             }
           }

-          const next = await Promise.resolve(marked.parse(block.raw))
+          const next = await Promise.resolve(marked.parse(block.src))
           const safe = sanitize(next)
           if (key && hash) touch(key, { hash, html: safe })
           return safe
PATCH

# ── 4. Install the remend dependency ─────────────────────────────────────────
# Use bun add to update packages/ui/package.json and bun.lock consistently,
# regardless of which bun version is installed in this image.
cd /workspace/opencode/packages/ui && bun add remend@1.3.0

echo "Patch applied successfully."
