# Server Action Payload Security Hardening

## Problem

The React Server Actions payload deserialization has a security gap in how Blob references are handled. When processing Server Action responses, the system allows `$B` references in the parsed model to retrieve backing entries from FormData without validating their actual type.

Since `FormData.get()` returns either a string or a File/Blob object, a malformed payload could store a large string value in a FormData slot and reference it via `$B`. While this doesn't produce memory amplification on its own (strings don't expand like nested arrays), it represents a defense-in-depth gap where the type contract is not enforced at the deserialization boundary.

## What Needs to Change

The fix should add type validation to ensure that when a `$B` reference is resolved, the backing entry is actually a Blob instance. If the backing entry is not a Blob (e.g., it's a string), the deserializer should throw a descriptive error rather than returning the invalid value.

The error message should clearly indicate that the referenced Blob is not actually a Blob.

## Relevant Areas

- Server Action reply deserialization logic
- `ReactFlightDOMReply-test.js` for test coverage

## Expected Behavior

After the fix:
- Valid Blob references continue to work normally
- String values referenced via `$B` throw an error with the message "Referenced Blob is not a Blob."
- The error handling integrates with React's existing error code system
