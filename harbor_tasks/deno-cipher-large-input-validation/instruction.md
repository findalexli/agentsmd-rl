# Cipher update crashes on very large input buffers

## Problem

When calling `Cipheriv.prototype.update` or `Decipheriv.prototype.update` with an input buffer whose length approaches or exceeds INT_MAX (2,147,483,647 bytes), the operation proceeds without any size validation. In Node.js, this triggers a synchronous error with a descriptive message. Deno's polyfill currently passes the oversized buffer through to the native layer, causing undefined behavior that can crash the process.

## Expected Behavior

Both `Cipheriv.prototype.update` and `Decipheriv.prototype.update` must validate input buffer sizes before calling native crypto operations. When a buffer exceeds the safe limit, throw an error with a descriptive message matching Node.js/OpenSSL behavior. The error must be a catchable JavaScript exception, not a process crash.

The validation must happen before the native encrypt/decrypt operation is invoked.
