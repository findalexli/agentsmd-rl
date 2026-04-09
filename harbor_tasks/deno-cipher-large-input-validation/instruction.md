# Cipher update crashes on very large input buffers

## Problem

When calling `Cipheriv.prototype.update` or `Decipheriv.prototype.update` with an input buffer whose length approaches or exceeds `2^31 - 1` bytes (the 32-bit signed integer maximum), the operation proceeds without any size validation. In Node.js (and the underlying OpenSSL `EVP_EncryptUpdate`/`EVP_DecryptUpdate`), this input length is passed as a C `int`, which cannot represent values >= `INT_MAX`. Node.js throws a synchronous error in this case, but Deno's polyfill silently passes the oversized buffer through, leading to undefined behavior.

## Expected Behavior

Both `Cipheriv.prototype.update` and `Decipheriv.prototype.update` should validate the input buffer size and throw an error when the buffer length is >= `2^31 - 1` bytes, matching the Node.js/OpenSSL behavior. The process should remain alive after catching the error — it should be a normal JavaScript exception, not a crash.

## Files to Look At

- `ext/node/polyfills/internal/crypto/cipher.ts` — Contains the `Cipheriv` and `Decipheriv` prototype implementations including their `update` methods
