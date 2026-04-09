# BiDi set-cookie test expectation is wrong for SameSite=None

## Problem

The test `should support set-cookie with SameSite and without Secure attribute over HTTP` in `tests/library/browsercontext-fetch.spec.ts` does not account for BiDi protocol behavior.

Firefox/BiDi (like Chromium) rejects cookies with `SameSite=None` when the `Secure` attribute is absent over plain HTTP. However, the test only checks `browserName === 'chromium'` when deciding whether to expect `SameSite=None` cookies to be absent — it does not factor in BiDi at all.

As a result, the test is listed as a known failure in the BiDi expectations file (`tests/bidi/expectations/moz-firefox-nightly-library.txt`), even though the correct fix is to update the test logic rather than mark it as permanently broken.

## Expected Behavior

The test should destructure the `isBidi` fixture and include it in the condition that checks whether `SameSite=None` cookies should be rejected. The BiDi expectations file should no longer list this test as failing.

## Files to Look At

- `tests/library/browsercontext-fetch.spec.ts` — the set-cookie test around the "SameSite" test function; its condition for `SameSite=None` cookie rejection
- `tests/bidi/expectations/moz-firefox-nightly-library.txt` — BiDi-specific test expectations that track known failures
