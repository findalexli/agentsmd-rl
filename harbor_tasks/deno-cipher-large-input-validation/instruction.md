# Cipher update crashes on very large input buffers

## Problem

When calling `Cipheriv.prototype.update` or `Decipheriv.prototype.update` with an input buffer whose length approaches or exceeds `2^31 - 1` bytes (the 32-bit signed integer maximum, INT_MAX), the operation proceeds without any size validation. In Node.js (and the underlying OpenSSL `EVP_EncryptUpdate`/`EVP_DecryptUpdate`), this input length is passed as a C `int`, which cannot represent values >= `INT_MAX`. Node.js throws a synchronous error in this case, but Deno's polyfill silently passes the oversized buffer through, leading to undefined behavior.

## Expected Behavior

Both `Cipheriv.prototype.update` and `Decipheriv.prototype.update` should validate the input buffer size and throw an error when the buffer length is >= `2^31 - 1` bytes, matching the Node.js/OpenSSL behavior. The process should remain alive after catching the error — it should be a normal JavaScript exception, not a crash.

Specifically:
- The validation must check `buf.length >= 2 ** 31 - 1` (or an equivalent expression for the same threshold)
- When the check fails, throw `Error("Trying to add data in unsupported state")` — the exact Node.js/OpenSSL error message
- The size check must be performed **before** calling the native crypto operation (`op_node_cipheriv_encrypt` for Cipheriv, `op_node_decipheriv_decrypt` for Decipheriv)

## Files to Look At

- `ext/node/polyfills/internal/crypto/cipher.ts` — Contains the `Cipheriv` and `Decipheriv` prototype implementations including their `update` methods
