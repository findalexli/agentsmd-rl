# Fix Dangling Pointer Crash in Electron Session Shutdown

## Symptom

Electron crashes during shutdown when `Session` objects have live wrappers. The crash occurs because `Session::Dispose()` accesses `browser_context()` after the underlying `ElectronBrowserContext` has been destroyed — a use-after-free during the process exit path.

## Scope

The issue spans these files:
- `shell/browser/api/electron_api_session.h`
- `shell/browser/api/electron_api_session.cc`
- `shell/browser/api/electron_api_web_contents.cc`
- `shell/browser/electron_browser_main_parts.cc`
- `shell/common/api/electron_api_url_loader.cc`
- `spec/cpp-heap-spec.ts`

## Expected Behavior After Fix

### `electron_api_session.h`
- `browser_context_` uses a nullable pointer type
- `browser_context()` accessor returns the member directly

### `electron_api_session.cc`
- Constructor initializes `browser_context_` directly with the pointer value (not via a wrapping API)
- `Dispose()` captures `browser_context` locally, checks for null before use, and returns early if null
- `OnBeforeMicrotasksRunnerDispose()` nullifies `browser_context_` before `keep_alive_.Clear()` completes

### `electron_api_web_contents.cc`
- Captures `browser_context` from session in a local variable after obtaining from `session->browser_context()`
- Uses `DCHECK` to verify the captured pointer is not null

### `electron_api_url_loader.cc`
- After obtaining `browser_context` from session, uses `DCHECK` to verify it is not null

### `electron_browser_main_parts.cc`
- `PostMainMessageLoopRun()` resets `browser_` and `js_env_`

### `spec/cpp-heap-spec.ts`
- Contains a regression test verifying that a process with live session wrappers does not crash on exit
- Imports `once` from `node:events`

## Verification

Your fix will be verified by checking:
- `browser_context_` uses a nullable pointer type
- Null checks are present before accessing `browser_context` in `Dispose()`
- `browser_context_` is nullified during cleanup
- `DCHECK` assertions verify `browser_context` is not null when obtained from session
- The shutdown sequence resets browser and js_env resources
- The regression test exists and has the correct import