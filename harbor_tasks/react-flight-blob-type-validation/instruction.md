# Server Action Payload: Missing Type Validation for Blob References

## Problem

React's Server Actions deserialization (`decodeReply`) has a gap in how Blob references are handled in the flight protocol. When decoding reply payloads from FormData, the system allows Blob references to resolve to non-Blob values (such as plain strings) without any validation. Since `FormData.get()` returns either a string or a File/Blob object, a malformed payload can contain a string value where a Blob is expected, and the deserializer silently accepts it, violating the type contract.

## Expected Behavior

After the fix:

- When a Blob reference in a Server Action payload resolves to something that is not actually a Blob, `decodeReply` should throw an error with the message: **"Referenced Blob is not a Blob."**
- Valid Blob references (e.g., FormData containing actual Blob/File objects) must continue to work normally.
- A new test named **"cannot deserialize a Blob reference backed by a string"** should be added to the `ReactFlightDOMReply-test` test suite and must pass.
- The new error message must be registered in `scripts/error-codes/codes.json` by running `yarn extract-errors`.
- All existing tests (including lint, Flow typecheck, and the full ReactFlightDOMReply test suite) must continue to pass.
