# Reject string-backed `$B` references in the Flight Reply decoder

You are working in a checkout of `facebook/react` at a single commit on
`main`. The repo has been built with `yarn install --frozen-lockfile`,
so `yarn test`, `yarn lint`, and `yarn linc` work out of the box.

## Background

The React Server Components "Flight Reply" wire format encodes a Server
Action payload as a `FormData` instance.  Each entry has a key — a
prefix character followed by a small integer id — and the entry value
is either a UTF-8 string or a `File` / `Blob`.

Inside the encoded `JSON` body, references to non-string entries are
serialised as short tokens.  In particular, a `Blob` backing entry is
referenced as `"$B<id>"` (e.g. `"$B1"`), and the decoder is expected to
look that id up in the underlying `FormData` and return the original
`Blob` object.

The decoder lives in the `react-server` package and dispatches on the
prefix character; the `'B'` branch is the one that handles `$B`
references.

## The bug

A malicious client can construct a `FormData` whose slot at id `N`
holds **a string**, while the encoded JSON references that slot via
`"$BN"`.  `FormData.get()` returns either a string or a `File` / `Blob`,
so the current decoder happily returns whatever it gets back — meaning
`decodeReply` silently produces a string in a position the caller will
treat as a `Blob`.

That bypasses the size guard (`bumpArrayCount`) that normally limits how
much string data a Reply payload can hold, because that guard is only
applied to entries the decoder *already classified* as strings.  A
correctly-typed Reply must never return a non-`Blob` value for a `$B`
reference; doing so is a defense-in-depth concern flagged for hardening.

You can reproduce the bug like this:

```js
const formData = new FormData();
formData.set('1', '-'.repeat(50000));   // string in a Blob slot
formData.set('0', JSON.stringify(['$B1']));
const result = await ReactServerDOMServer.decodeReply(
  formData,
  webpackServerMap,
);
// result[0] is currently the 50 000-character string.
// Expected: decodeReply rejects this payload.
```

## What to fix

Make `decodeReply` reject any Reply whose `$B` reference resolves to
something that is not a `Blob`.  The rejection must be observable as a
thrown `Error` from the call to `decodeReply` (or from awaiting its
returned promise) — silently returning `undefined`, returning the
string, or coercing it to a Blob is not acceptable.

Constraints:

* A `$B` reference whose backing entry **is** a real `Blob` (or a
  `File`, which is a `Blob` subclass) must continue to resolve
  successfully and return that `Blob`.
* Do not weaken any other validation or input handling in the decoder.
* The thrown `Error` must have a non-empty string message.  React's
  convention for security-relevant rejections is a short, descriptive
  message.

## Code Style Requirements

The repo enforces lint via `yarn linc` (lints files changed against
`main`).  Your edits must pass that check — in particular:

* Use single quotes, not double quotes, for string literals.
* No `console.log` / `console.error` in production code paths.
* No unused locals.

Run `yarn linc` before considering the task done.

## How your work is graded

A behavioral test suite invokes `decodeReply` through Jest:

* It builds a `FormData` with a string in a `$B` slot and asserts the
  call throws an `Error` with a non-empty `message`.
* It repeats the check with a 50 000-character string to confirm the
  rejection is independent of payload size.
* It builds a `FormData` with a real `Blob` in the `$B` slot and asserts
  the call still resolves to a `Blob`.
* The full existing `ReactFlightDOMReply-test` Jest suite must continue
  to pass (no regressions in valid Reply decoding).
* `yarn linc` must pass on the file you edit.
