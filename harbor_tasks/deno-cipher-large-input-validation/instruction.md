# Cipher update crashes on very large input buffers

## Problem

When calling `Cipheriv.prototype.update` or `Decipheriv.prototype.update` in `ext/node/polyfills/internal/crypto/cipher.ts` with an input buffer whose length approaches or exceeds INT_MAX (2,147,483,647 bytes), the operation proceeds without any size validation. In Node.js, this triggers a synchronous error with a descriptive message like "Trying to add data in unsupported state". Deno's polyfill currently passes the oversized buffer through to the native layer, causing undefined behavior that can crash the process.

## Expected Behavior

Both `Cipheriv.prototype.update` and `Decipheriv.prototype.update` must validate input buffer sizes before calling native crypto operations. When a buffer exceeds INT_MAX (2,147,483,647 bytes), throw a catchable JavaScript error with a descriptive message (for example: "unsupported state", "INT_MAX", "too large", or similar wording that indicates the input is invalid). The error must be catchable via try/catch, not a process crash.

The validation must happen before the native encrypt/decrypt operation is invoked.
