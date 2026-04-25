# BiDi set-cookie test expectation is wrong for SameSite=None

## Problem

The test `should support set-cookie with SameSite and without Secure attribute over HTTP` in `tests/library/browsercontext-fetch.spec.ts` does not account for BiDi protocol behavior.

Both Chromium and Firefox reject cookies with `SameSite=None` when the `Secure` attribute is absent over plain HTTP. The test currently only checks for Chromium when deciding whether to expect `SameSite=None` cookies to be absent — it does not account for the BiDi protocol case.

As a result, the test is listed as a known failure in the BiDi expectations file (`tests/bidi/expectations/moz-firefox-nightly-library.txt`), even though the correct fix is to update the test logic rather than mark it as permanently broken.

## Expected Behavior

The test should correctly handle the case where cookies with `SameSite=None` and no `Secure` attribute are rejected when running under the BiDi protocol. The BiDi expectations file should no longer list this test as failing.

## Files to Look At

- `tests/library/browsercontext-fetch.spec.ts` — the set-cookie test around line 1155 in the `SameSite` test function
- `tests/bidi/expectations/moz-firefox-nightly-library.txt` — BiDi-specific test expectations that track known failures

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
