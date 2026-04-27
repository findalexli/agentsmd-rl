import { ReasoningDetailText } from "@effect/ai-openrouter/Generated"
import {
  ChatStreamingChoice,
  ChatStreamingMessageChunk,
  ChatStreamingResponseChunk
} from "@effect/ai-openrouter/OpenRouterClient"
import { makeStreamResponse } from "@effect/ai-openrouter/OpenRouterLanguageModel"
import { assert, describe, it } from "@effect/vitest"
import * as DateTime from "effect/DateTime"
import * as Effect from "effect/Effect"
import * as Stream from "effect/Stream"

const reasoningTextDetail = (text: string) => new ReasoningDetailText({ type: "reasoning.text", text })

const makeChunk = (delta: {
  readonly reasoning?: string
  readonly reasoning_details?: ReadonlyArray<any>
  readonly content?: string
}): ChatStreamingResponseChunk => {
  const chunkFields: any = { role: "assistant" }
  if (delta.content !== undefined) chunkFields.content = delta.content
  if (delta.reasoning !== undefined) chunkFields.reasoning = delta.reasoning
  if (delta.reasoning_details !== undefined) chunkFields.reasoning_details = delta.reasoning_details
  return new ChatStreamingResponseChunk({
    id: "chunk-1",
    model: "openrouter/auto",
    created: DateTime.unsafeMake(0),
    choices: [
      new ChatStreamingChoice({
        index: 0,
        delta: new ChatStreamingMessageChunk(chunkFields)
      })
    ]
  })
}

const collectParts = (chunks: ReadonlyArray<ChatStreamingResponseChunk>) =>
  Effect.gen(function*() {
    const stream = yield* makeStreamResponse(Stream.fromIterable(chunks))
    const collected = yield* Stream.runCollect(stream)
    return Array.from(collected)
  })

describe("OpenRouter streaming reasoning dedup (PR #6060)", () => {
  it.effect("does NOT emit reasoning twice when both `reasoning` and `reasoning_details` are present", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({
          reasoning: "Hello there",
          reasoning_details: [
            reasoningTextDetail("Hello there")
          ]
        })
      ])

      const reasoningDeltas = parts.filter((p) => p.type === "reasoning-delta")
      assert.strictEqual(
        reasoningDeltas.length,
        1,
        `expected exactly one reasoning-delta, got ${reasoningDeltas.length}: ${JSON.stringify(parts)}`
      )
      assert.strictEqual((reasoningDeltas[0] as any).delta, "Hello there")
    }))

  it.effect("falls back to `reasoning` when `reasoning_details` is absent", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({ reasoning: "fallback only" })
      ])

      const reasoningDeltas = parts.filter((p) => p.type === "reasoning-delta")
      assert.strictEqual(reasoningDeltas.length, 1)
      assert.strictEqual((reasoningDeltas[0] as any).delta, "fallback only")
    }))

  it.effect("falls back to `reasoning` when `reasoning_details` is an empty array", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({ reasoning: "still works", reasoning_details: [] })
      ])

      const reasoningDeltas = parts.filter((p) => p.type === "reasoning-delta")
      assert.strictEqual(reasoningDeltas.length, 1)
      assert.strictEqual((reasoningDeltas[0] as any).delta, "still works")
    }))

  it.effect("uses `reasoning_details` only when both are present (different content)", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({
          reasoning: "from-plain-field",
          reasoning_details: [reasoningTextDetail("from-details")]
        })
      ])

      const reasoningDeltas = parts
        .filter((p) => p.type === "reasoning-delta")
        .map((p) => (p as any).delta)
      assert.deepStrictEqual(reasoningDeltas, ["from-details"])
    }))

  it.effect("does not emit reasoning at all when both fields are absent", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({ content: "just text" })
      ])

      const reasoningParts = parts.filter((p) =>
        p.type === "reasoning-delta" || p.type === "reasoning-start" || p.type === "reasoning-end"
      )
      assert.strictEqual(reasoningParts.length, 0)
    }))

  it.effect("dedups across multiple consecutive deltas that all carry both fields", () =>
    Effect.gen(function*() {
      const parts = yield* collectParts([
        makeChunk({
          reasoning: "tok1",
          reasoning_details: [reasoningTextDetail("tok1")]
        }),
        makeChunk({
          reasoning: "tok2",
          reasoning_details: [reasoningTextDetail("tok2")]
        }),
        makeChunk({
          reasoning: "tok3",
          reasoning_details: [reasoningTextDetail("tok3")]
        })
      ])

      const reasoningDeltas = parts
        .filter((p) => p.type === "reasoning-delta")
        .map((p) => (p as any).delta)
      assert.deepStrictEqual(reasoningDeltas, ["tok1", "tok2", "tok3"])
    }))
})
