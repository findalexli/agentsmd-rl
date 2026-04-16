# Add file upload/download test utilities to @gradio/tootils

## Problem

The `@gradio/tootils` package (`js/tootils/`) provides unit testing utilities for Gradio Svelte components, but it's missing critical functionality for testing file-related interactions:

1. **No way to test file downloads.** Components like `File`, `DownloadButton`, `Gallery`, and `Code` trigger real browser downloads, but there's no utility to capture and verify the downloaded content in tests.

2. **No way to test file uploads or drag-and-drop.** Components accept files via `<input type="file">` or drag-and-drop, but there's no helper to set files on inputs or simulate drops with real file data.

3. **The `listen` helper has a race condition.** Events dispatched during component mount (before `listen()` is called) are silently lost. There's no mechanism to capture and replay mount-time events.

4. **No `mock_client` helper.** Components that use the Gradio client for uploads need a mock client, but each test has to create its own.

5. **No test fixtures.** Tests that need file data (images, text, audio, video, PDF) have to construct `FileData` objects manually every time.

6. **Missing Vitest browser commands.** No browser-mode commands exist for the three file operations (capturing downloads, setting file inputs, simulating drag-and-drop).

7. **Documentation is incorrect.** The README describes the wrong package entirely and lacks API documentation.

## Required Implementation

### Test Fixtures

Create a file at `js/tootils/src/fixtures.ts` exporting test fixture constants named exactly:
- `TEST_TXT`
- `TEST_JPG`
- `TEST_PNG`
- `TEST_MP4`
- `TEST_WAV`
- `TEST_PDF`

Each should be a `FileData` instance pointing to files in `test/test_files/`.

### File Operation Utilities

Create a file at `js/tootils/src/download.ts` implementing three async utilities:
- `download_file` - clicks an element and captures the resulting file download, returning the suggested filename and text content
- `upload_file` - sets files on a file input using Playwright's `setInputFiles()`
- `drop_file` - simulates drag-and-drop by constructing a `DataTransfer` with `File` objects and dispatching `dragenter`/`dragover`/`drop` events

### Browser Commands

Register these Vitest browser command names in `js/spa/vite.config.ts`:
- `expect_download`
- `set_file_inputs`
- `drop_files`

### Event Buffering

In `js/tootils/src/render.ts`, implement event buffering using an array named `event_buffer` to store all dispatched events from mount time. The `listen` helper must accept a `retrospective` option that replays buffered events onto the mock when enabled.

The `event_buffer.push` method must be used to add events to the buffer.

### Mock Client

In `js/tootils/src/render.ts`, create a `mock_client` function that returns an object with:
- `upload` method (echo-back behavior)
- `stream` method (no-op)

### Package Configuration

The package at `js/tootils/package.json` must include an export entry for `./download-command`.

### Documentation

Completely rewrite `js/tootils/README.md` to accurately document `@gradio/tootils`, covering:
- `render` function and its parameters (Component, props)
- `listen` helper with the `retrospective` option for replaying buffered events
- `cleanup`, `fireEvent`
- `download_file`, `upload_file`, `drop_file` utilities
- `mock_client` helper
- Test fixtures (`TEST_TXT`, `TEST_JPG`, `TEST_PNG`, `TEST_MP4`, `TEST_WAV`, `TEST_PDF`)
- Reference to the `test/test_files/` directory where fixture files live
- Re-exports from testing-library

The README must reference `@gradio/tootils` as the package name and must NOT reference `@gradio/button`.
