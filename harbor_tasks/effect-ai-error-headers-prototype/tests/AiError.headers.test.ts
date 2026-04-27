import { describe, it } from "@effect/vitest"
import { strictEqual } from "node:assert"
import * as Effect from "effect/Effect"
import * as Headers from "@effect/platform/Headers"
import * as HttpClientRequest from "@effect/platform/HttpClientRequest"
import * as HttpClientResponse from "@effect/platform/HttpClientResponse"
import * as HttpClientError from "@effect/platform/HttpClientError"
import { AiError } from "@effect/ai"

describe("AiError.HttpRequestError.fromRequestError", () => {
  it("preserves the Headers prototype on the request", () => {
    const headers = Headers.fromInput({ "x-custom": "value", "authorization": "Bearer secret" })
    const request = HttpClientRequest.get("https://api.example.com/v1/resource").pipe(
      HttpClientRequest.setHeaders(headers)
    )
    const requestError = new HttpClientError.RequestError({
      request,
      reason: "Transport"
    })
    const aiError = AiError.HttpRequestError.fromRequestError({
      module: "TestModule",
      method: "doSomething",
      error: requestError
    })
    strictEqual(
      Headers.isHeaders(aiError.request.headers),
      true,
      "aiError.request.headers should still satisfy Headers.isHeaders"
    )
  })
})

describe("AiError.HttpResponseError.fromResponseError", () => {
  it.effect("preserves the Headers prototype on the request", () =>
    Effect.gen(function* () {
      const reqHeaders = Headers.fromInput({ "x-req": "v1" })
      const request = HttpClientRequest.get("https://api.example.com/v1/resource").pipe(
        HttpClientRequest.setHeaders(reqHeaders)
      )
      const response = HttpClientResponse.fromWeb(
        request,
        new Response("body", {
          status: 500,
          headers: { "content-type": "text/plain", "x-resp": "v2" }
        })
      )
      const respError = new HttpClientError.ResponseError({
        request,
        response,
        reason: "Decode"
      })
      const aiError = yield* Effect.flip(
        AiError.HttpResponseError.fromResponseError({
          module: "TestModule",
          method: "doSomething",
          error: respError
        })
      )
      strictEqual(
        Headers.isHeaders(aiError.request.headers),
        true,
        "aiError.request.headers should still satisfy Headers.isHeaders"
      )
    }))

  it.effect("preserves the Headers prototype on the response", () =>
    Effect.gen(function* () {
      const reqHeaders = Headers.fromInput({ "x-req": "v1" })
      const request = HttpClientRequest.get("https://api.example.com/v1/resource").pipe(
        HttpClientRequest.setHeaders(reqHeaders)
      )
      const response = HttpClientResponse.fromWeb(
        request,
        new Response("body", {
          status: 500,
          headers: { "content-type": "text/plain", "x-resp": "v2" }
        })
      )
      const respError = new HttpClientError.ResponseError({
        request,
        response,
        reason: "Decode"
      })
      const aiError = yield* Effect.flip(
        AiError.HttpResponseError.fromResponseError({
          module: "TestModule",
          method: "doSomething",
          error: respError
        })
      )
      strictEqual(
        Headers.isHeaders(aiError.response.headers),
        true,
        "aiError.response.headers should still satisfy Headers.isHeaders"
      )
    }))
})
