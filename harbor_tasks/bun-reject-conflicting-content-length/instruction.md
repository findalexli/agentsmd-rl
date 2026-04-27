# Reject conflicting duplicate `Content-Length` headers in `bun-uws`

The HTTP request parser in `packages/bun-uws/src/HttpParser.h` is exposed to a
**HTTP request-smuggling** vulnerability: it accepts requests that carry
multiple `Content-Length` header fields whose values disagree, and it accepts
requests where one of those `Content-Length` fields has an empty value. Both
cases are explicitly forbidden by RFC 9112 §6.3 and RFC 9110 §8.6, because the
parser must not be allowed to disagree with downstream proxies / clients about
where one request ends and the next begins.

You need to harden the parser so that a single, well-defined Content-Length
value is the only thing the rest of the parser ever sees.

## Behavior the parser must implement

For each parsed request, after the headers have been read but before
`Content-Length` is interpreted as a body length:

1. **No Content-Length headers** — accept (unchanged behavior).

2. **Exactly one Content-Length header** — accept it (unchanged behavior).

3. **Multiple Content-Length headers, all with the same value** — accept the
   request and treat the value as if a single header had been sent. RFC 9112
   §6.3 explicitly permits this case.

4. **Multiple Content-Length headers with at least one differing value** —
   reject the request with HTTP `400 Bad Request` and the parser-level error
   code `HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH`. The check must be
   byte-for-byte: `"5"` and `"05"` count as different. Ordering of the
   headers must not matter.

5. **A `Content-Length` header whose value is the empty string** — reject the
   request with HTTP `400 Bad Request` and parser-level error
   `HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH`. This case must be rejected
   *even if* a later, well-formed `Content-Length` header would otherwise
   make the request unambiguous, because accepting the empty value first
   would let an attacker smuggle a second request inside the body that the
   real Content-Length header advertises.

The pre-existing rejection of "Transfer-Encoding **and** Content-Length on the
same request" must continue to hold.

## Where the bug lives

`HttpParser.h` only inspects the *first* matching header value via
`req->getHeader("content-length")` after request line + header parsing has
finished. A second header with a different value is silently dropped on the
floor, and an empty first value resolves to a zero-length body that lets the
attacker smuggle the next request straight into the byte stream.

The fix needs to walk every `Content-Length` header that was actually parsed
out of the request, not just the first one. The repo already maintains a
bloom filter of seen header names on `req->bf` — use it to keep the
no-Content-Length fast path zero-cost.

## How your fix will be evaluated

The graders compile a small C++ driver that links against your modified
`HttpParser.h` and feeds it raw HTTP byte streams. A passing fix:

- returns `HttpParserResult::error(HTTP_ERROR_400_BAD_REQUEST, HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH)`
  for a request with `Content-Length: 6` followed by `Content-Length: 5`,
- returns the same error for a request whose first `Content-Length` value is
  empty and whose second `Content-Length` advertises a body containing a
  smuggled `GET /admin HTTP/1.1` request,
- accepts a request with two identical `Content-Length: 5` headers and
  delivers exactly one request callback with the body `Hello`,
- accepts a request with a single `Content-Length` header (the common case)
  and one with no `Content-Length` at all,
- accepts a chunked `Transfer-Encoding` request that has no `Content-Length`,
- continues to reject a request that carries both `Transfer-Encoding:
  chunked` and `Content-Length: 5`.

The code must continue to compile cleanly under `g++ -std=c++20 -Wall`.

## Constraints

- Your change must live in `packages/bun-uws/src/HttpParser.h`. No other file
  in the repo should be modified to fix this issue.
- Do not change the public signature of `consumePostPadded` /
  `fenceAndConsumePostPadded` or the layout of `HttpRequest` /
  `HttpParserResult`.
- Follow the surrounding C++ style of the file: 4-space indentation, brace
  on the same line as `if`/`for`, RFC-citation block comments, and use the
  existing `HttpParserResult::error(...)` factory rather than constructing
  results inline.

## Code Style Requirements

- The grader compiles your change with `g++ -std=c++20 -Wall` (a few low-noise
  warning categories — `unused-parameter`, `unused-variable` — are silenced
  because they fire on parts of `HttpParser.h` that you should not be
  modifying). Your change must produce no new warnings under those flags.
- Match the existing formatting in `HttpParser.h`: 4-space indentation, no
  tabs, `if (...)` (not `if(...)`), and an opening brace on the same line as
  the control statement.
