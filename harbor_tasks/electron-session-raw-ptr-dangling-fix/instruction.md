# Fix Dangling Pointer Crash in Electron Session Shutdown

## Problem

Electron crashes during shutdown when `Session` objects have live wrappers. The crash is a use-after-free: during the process exit path, the underlying `ElectronBrowserContext` is destroyed while `Session` still holds a reference to it via a non-nullable reference wrapper (`raw_ref`). When `Session::Dispose()` later tries to access `browser_context()`, it dereferences a dangling pointer.

The core issue is that `raw_ref` cannot be nullified — it is a non-nullable reference — so once the pointed-to object is destroyed, any access through it is undefined behavior.

## Symptoms

- Process crashes during exit when session wrappers are still live
- Use-after-free when `Session::Dispose()` accesses `browser_context()` after the browser context has been destroyed
- The issue manifests when CppGC-traced references are accessed during the shutdown sequence

## Files Involved

The fix spans these files:

- `shell/browser/api/electron_api_session.h` — Session class header, where `browser_context_` is declared
- `shell/browser/api/electron_api_session.cc` — Session constructor, `Dispose()`, and `OnBeforeMicrotasksRunnerDispose()`
- `shell/browser/api/electron_api_web_contents.cc` — WebContents constructor, which obtains `browser_context` from a session
- `shell/browser/electron_browser_main_parts.cc` — `PostMainMessageLoopRun()` shutdown sequence for `browser_` and `js_env_`
- `shell/common/api/electron_api_url_loader.cc` — URL loader, which obtains `browser_context` from a session
- `spec/cpp-heap-spec.ts` — Where the regression test should be added

## Expected Code State After Fix

### `shell/browser/api/electron_api_session.h`

- The `#include "base/memory/raw_ref.h"` line should be removed since `raw_ref` is no longer used
- `browser_context_` should be declared as `raw_ptr<ElectronBrowserContext>` (the existing `const raw_ref<ElectronBrowserContext>` declaration should not be present)
- The `browser_context()` accessor should return `browser_context_` directly (not through `&browser_context_.get()`)

### `shell/browser/api/electron_api_session.cc`

- The constructor should initialize `browser_context_` as `browser_context_{browser_context}` — directly with the pointer argument, not via `raw_ref<ElectronBrowserContext>::from_ptr()`
- `Dispose()` should:
  - Capture `browser_context()` in a local variable declared as `ElectronBrowserContext* const browser_context = this->browser_context()`
  - Check `if (!browser_context)` and `return` early if null
  - Use the local `browser_context` variable for all subsequent access (not `browser_context()`)
- `OnBeforeMicrotasksRunnerDispose()` should set `browser_context_ = nullptr` before calling `keep_alive_.Clear()`

### `shell/browser/api/electron_api_web_contents.cc`

- The WebContents constructor should capture the session's browser context once in a local variable: `ElectronBrowserContext* const browser_context = session->browser_context()`
- Add `DCHECK(browser_context != nullptr)` after the capture
- Use the local `browser_context` variable consistently instead of calling `session->browser_context()` multiple times

### `shell/common/api/electron_api_url_loader.cc`

- In `SimpleURLLoaderWrapper::Create`, inside the `if (session)` block after `browser_context = session->browser_context()`, add `DCHECK(browser_context != nullptr)`

### `shell/browser/electron_browser_main_parts.cc`

- In `PostMainMessageLoopRun()`, add `browser_.reset()` and `js_env_.reset()` to ensure proper destruction order during shutdown

### `spec/cpp-heap-spec.ts`

- Add `import { once } from 'node:events';` at the top of the file
- Add a test case in the `describe('session module', ...)` block with the name `'does not crash on exit with live session wrappers'` that:
  - Creates multiple sessions (default session, a partition session, and a persist partition session)
  - Accesses `.cookies` on each session to ensure CppGC-managed objects are live
  - Stores session references in `globalThis` to prevent pre-shutdown garbage collection
  - Calls `app.quit()` via `setTimeout`
  - Waits for the process exit using `const [code] = await once(rc.process, 'exit')`
  - Asserts `expect(code).to.equal(0)` — the process should exit cleanly without crashing

## Testing

Your fix will be verified by checking that:
- The `raw_ref` type is replaced with `raw_ptr` for the `browser_context_` member
- Null checks are present in `Dispose()` before accessing the browser context
- `browser_context_` is nullified during cleanup in `OnBeforeMicrotasksRunnerDispose()`
- DCHECK assertions are added in `WebContents` and the URL loader when obtaining `browser_context` from a session
- The shutdown sequence properly resets `browser_` and `js_env_`
- The regression test is added to `cpp-heap-spec.ts` with the correct import and test structure
- All modified files remain syntactically valid (balanced braces, proper C++ structure, valid TypeScript)
