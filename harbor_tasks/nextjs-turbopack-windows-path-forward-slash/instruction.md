# TURBOPACK: Windows paths with forward slashes not recognized

## Problem

Turbopack's request parser fails to recognize Windows absolute paths that use forward slashes as the path separator. A path like:

```
C:/Users/demo/src/index.ts
```

is not detected as a Windows filesystem path, even though Windows accepts both forward and backward slashes in absolute paths (e.g. `C:\Users\...` and `C:/Users/...` are equivalent).

Additionally, the UNC path detection (`\\server\share`) is not properly anchored — it can match double-backslash sequences that appear in the middle of a string rather than only at the start.

## Expected Behavior

- `C:/Users/demo/src/index.ts` should be parsed as a Windows path (just like `C:\Users\demo\src\index.ts`)
- UNC paths (`\\server\share`) should only match at the beginning of the request string

## Files to Look At

- `turbopack/crates/turbopack-core/src/resolve/parse.rs` — contains the `WINDOWS_PATH` regex used to detect Windows-style paths during request parsing
