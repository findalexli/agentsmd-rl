import * as AiError from "@effect/ai/AiError"
import * as Headers from "@effect/platform/Headers"
import * as HttpClientError from "@effect/platform/HttpClientError"
import * as HttpClientRequest from "@effect/platform/HttpClientRequest"
import * as HttpClientResponse from "@effect/platform/HttpClientResponse"
import * as Effect from "effect/Effect"

const result: Record<string, unknown> = {}

async function main() {
  const inputReqHeaders = Headers.fromInput({
    "x-api-key": "secret-value",
    "content-type": "application/json"
  })
  result.input_is_headers = Headers.isHeaders(inputReqHeaders)

  const clientReq = HttpClientRequest.make("POST")(
    "https://api.example.com/v1/chat",
    { headers: inputReqHeaders }
  )

  const platformReqErr = new HttpClientError.RequestError({
    request: clientReq,
    reason: "Transport",
    description: "boom"
  })
  const aiReqErr = AiError.HttpRequestError.fromRequestError({
    module: "TestModule",
    method: "testMethod",
    error: platformReqErr
  })
  result.req_err_request_headers_is_headers = Headers.isHeaders(
    aiReqErr.request.headers
  )
  result.req_err_request_method = aiReqErr.request.method
  result.req_err_request_url = aiReqErr.request.url
  result.req_err_module = aiReqErr.module
  result.req_err_reason = aiReqErr.reason

  const fakeResp = HttpClientResponse.fromWeb(
    clientReq,
    new Response(JSON.stringify({ error: "rate limit" }), {
      status: 429,
      headers: {
        "content-type": "application/json",
        "x-rate-limit-remaining": "0"
      }
    })
  )
  const platformRespErr = new HttpClientError.ResponseError({
    request: clientReq,
    response: fakeResp,
    reason: "StatusCode",
    description: "rate limited"
  })
  const eff = AiError.HttpResponseError.fromResponseError({
    module: "TestModule",
    method: "testMethod",
    error: platformRespErr
  }) as unknown as Effect.Effect<never, AiError.HttpResponseError>
  const aiRespErr = await Effect.runPromise(Effect.flip(eff))

  result.resp_err_request_headers_is_headers = Headers.isHeaders(
    aiRespErr.request.headers
  )
  result.resp_err_response_headers_is_headers = Headers.isHeaders(
    aiRespErr.response.headers
  )
  result.resp_err_response_status = aiRespErr.response.status
  result.resp_err_module = aiRespErr.module
  result.resp_err_reason = aiRespErr.reason

  console.log("__JSON_BEGIN__")
  console.log(JSON.stringify(result))
  console.log("__JSON_END__")
}

main().catch((e) => {
  console.error("UNHANDLED:", e && (e as Error).stack ? (e as Error).stack : e)
  process.exit(2)
})
