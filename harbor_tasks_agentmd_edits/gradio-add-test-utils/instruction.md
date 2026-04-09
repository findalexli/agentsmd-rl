# Add file upload/download test utilities to @gradio/tootils

## Problem

The `@gradio/tootils` package (`js/tootils/`) provides unit testing utilities for Gradio Svelte components, but it's missing critical functionality for testing file-related interactions:

1. **No way to test file downloads.** Components like `File`, `DownloadButton`, `Gallery`, and `Code` trigger real browser downloads, but there's no utility to capture and verify the downloaded content in tests.

2. **No way to test file uploads or drag-and-drop.** Components accept files via `<input type="file">` or drag-and-drop, but there's no helper to set files on inputs or simulate drops with real file data.

3. **The `listen` helper has a race condition.** Events dispatched during component mount (before `listen()` is called) are silently lost. There's no way to capture mount-time events.

4. **No `mock_client` helper.** Components that use the Gradio client for uploads need a mock client, but each test has to create its own.

5. **No test fixtures.** Tests that need file data (images, text, audio, video, PDF) have to construct `FileData` objects manually every time.

Additionally, the `js/tootils/README.md` is completely wrong — it describes `@gradio/button` instead of the actual tootils package, and contains no useful API documentation.

## Expected Behavior

1. **`download_file(selector)`** — A utility that clicks an element and captures the resulting file download, returning the suggested filename and text content. Should use Vitest browser commands running server-side with Playwright access.

2. **`upload_file(files, selector?)`** — Sets files on a file input using Playwright's `setInputFiles()` under the hood. Accepts `FileData` fixtures.

3. **`drop_file(files, selector)`** — Simulates drag-and-drop by reading fixture files from disk, constructing a `DataTransfer` with `File` objects, and dispatching `dragenter`/`dragover`/`drop` events.

4. **Event buffering in `render`** — The dispatcher should buffer all events from mount time. `listen(event, { retrospective: true })` should replay buffered events onto the mock.

5. **`mock_client()`** — Returns a mock client with upload (echo-back) and stream (no-op) methods.

6. **Test fixtures** — Pre-built `FileData` instances for common file types (text, image, audio, video, PDF) pointing to existing files in `test/test_files/`.

7. **Browser commands must be registered** in `js/spa/vite.config.ts` so the server-side commands are available to tests.

8. **The package.json** should export the new `./download-command` entry point.

9. **The README** should be completely rewritten to accurately document `@gradio/tootils` — covering `render`, `listen` (including retrospective mode), `cleanup`, `fireEvent`, `download_file`, `upload_file`, `drop_file`, `mock_client`, test fixtures, and re-exports.

## Files to Look At

- `js/tootils/src/render.ts` — Main render utility; needs event buffering, retrospective listen, mock_client, and re-exports
- `js/tootils/src/` — Add new modules here: download.ts, download-command.ts, fixtures.ts
- `js/tootils/package.json` — Needs new export entry
- `js/spa/vite.config.ts` — Register browser commands
- `js/tootils/README.md` — Rewrite with accurate, comprehensive API documentation
