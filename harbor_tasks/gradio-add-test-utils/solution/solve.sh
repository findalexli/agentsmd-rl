#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'event_buffer' js/tootils/src/render.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- New file: js/tootils/src/fixtures.ts ---
cat > js/tootils/src/fixtures.ts <<'FIXTURES_EOF'
import { FileData } from "@gradio/client";

const BASE = "/test/test_files";

function fixture(filename: string, mime_type: string, size: number): FileData {
	const url = `${BASE}/${filename}`;
	return new FileData({
		path: url,
		url,
		orig_name: filename,
		size,
		mime_type
	});
}

export const TEST_TXT = fixture("alphabet.txt", "text/plain", 26);
export const TEST_JPG = fixture("cheetah1.jpg", "image/jpeg", 20552);
export const TEST_PNG = fixture("bus.png", "image/png", 1951);
export const TEST_MP4 = fixture("video_sample.mp4", "video/mp4", 261179);
export const TEST_WAV = fixture("audio_sample.wav", "audio/wav", 16136);
export const TEST_PDF = fixture("sample_file.pdf", "application/pdf", 10558);
FIXTURES_EOF

# --- New file: js/tootils/src/download.ts ---
cat > js/tootils/src/download.ts <<'DOWNLOAD_EOF'
import { commands } from "vitest/browser";
import type { FileData } from "@gradio/client";

export interface DownloadResult {
	suggested_filename: string;
	content: string | null;
}

/**
 * Clicks an element and captures the resulting file download.
 *
 * Uses a real browser download via Playwright under the hood —
 * the file is actually downloaded and its content is readable.
 *
 * @param selector - CSS selector for the element to click
 * @param options - Optional timeout (default 5000ms)
 * @returns The downloaded file's suggested filename and text content
 *
 * @example
 * ```ts
 * const { suggested_filename, content } = await download_file("a.download-link");
 * expect(suggested_filename).toBe("data.csv");
 * expect(content).toContain("col1,col2");
 * ```
 */
export async function download_file(
	selector: string,
	options?: { timeout?: number }
): Promise<DownloadResult> {
	return (commands as any).expect_download(selector, options);
}

/**
 * Sets files on an `<input type="file">` element using real file fixtures.
 *
 * Accepts one or more FileData fixtures (e.g. TEST_JPG, TEST_PNG) and
 * sets them on the file input, triggering the browser's native change event.
 *
 * @param files - One or more FileData fixtures to upload
 * @param selector - CSS selector for the file input (default: 'input[type="file"]')
 *
 * @example
 * ```ts
 * import { render, upload_file, TEST_JPG } from "@self/tootils/render";
 *
 * const { listen } = await render(ImageUpload, { interactive: true });
 * const upload = listen("upload");
 *
 * await upload_file(TEST_JPG);
 *
 * expect(upload).toHaveBeenCalled();
 * ```
 */
export async function upload_file(
	files: FileData | FileData[],
	selector?: string
): Promise<void> {
	const file_list = Array.isArray(files) ? files : [files];
	const urls = file_list.map((f) => f.url ?? f.path);
	return (commands as any).set_file_inputs(urls, selector);
}

/**
 * Simulates dragging and dropping files onto an element.
 *
 * Reads the fixture files from disk, constructs a real DataTransfer
 * with File objects, and dispatches dragenter, dragover, and drop events
 * on the target element.
 *
 * @param files - One or more FileData fixtures to drop
 * @param selector - CSS selector for the drop target element
 *
 * @example
 * ```ts
 * import { render, drop_file, TEST_JPG } from "@self/tootils/render";
 *
 * const { listen } = await render(ImageUpload, { interactive: true });
 * const upload = listen("upload");
 *
 * await drop_file(TEST_JPG, "[aria-label='Click to upload or drop files']");
 *
 * await vi.waitFor(() => expect(upload).toHaveBeenCalled());
 * ```
 */
export async function drop_file(
	files: FileData | FileData[],
	selector: string
): Promise<void> {
	const file_list = Array.isArray(files) ? files : [files];
	const urls = file_list.map((f) => f.url ?? f.path);
	return (commands as any).drop_files(urls, selector);
}
DOWNLOAD_EOF

# --- New file: js/tootils/src/download-command.ts ---
cat > js/tootils/src/download-command.ts <<'DLCMD_EOF'
import type { BrowserCommand } from "vitest/node";
import { resolve } from "path";
import { readFile } from "fs/promises";

/**
 * Vitest browser command that captures a real file download triggered by
 * clicking an element. Runs server-side with access to the Playwright page.
 *
 * Sets up page.waitForEvent("download") BEFORE clicking, so the download
 * event is never missed.
 */
export const expect_download: BrowserCommand<
	[selector: string, options?: { timeout?: number }],
	{ suggested_filename: string; content: string | null }
> = async (context, selector, options) => {
	const timeout = options?.timeout ?? 5000;
	const provider = context.provider as any;
	const page = provider.getPage(context.sessionId);
	// Tests run inside an iframe; use the iframe locator to click
	// but listen for the download event on the parent page.
	const iframe = (context as any).iframe;

	const [download] = await Promise.all([
		page.waitForEvent("download", { timeout }),
		iframe.locator(selector).click()
	]);

	const suggested_filename = download.suggestedFilename();
	const path = await download.path();

	let content: string | null = null;
	if (path) {
		const fs = await import("fs/promises");
		content = await fs.readFile(path, "utf-8");
	}

	return {
		suggested_filename,
		content
	};
};

/**
 * Vitest browser command that sets files on an <input type="file"> element.
 * Resolves fixture URL paths (e.g. "/test/test_files/bus.png") to absolute
 * disk paths and uses Playwright's setInputFiles().
 */
export const set_file_inputs: BrowserCommand<
	[file_urls: string[], selector?: string]
> = async (context, file_urls, selector) => {
	const root = context.project.config.root;
	const iframe = (context as any).iframe;

	const paths = file_urls.map((url) => resolve(root, url.replace(/^\//, "")));

	await iframe
		.locator(selector ?? 'input[type="file"]')
		.first()
		.setInputFiles(paths);
};

interface Drop_file_spec {
	data: string; // base64
	name: string;
	mime_type: string;
}

/**
 * Vitest browser command that simulates dropping files onto an element.
 * Reads files from disk, transfers them as base64 into the browser context,
 * and dispatches dragenter, dragover, and drop events with a real DataTransfer.
 */
export const drop_files: BrowserCommand<
	[file_urls: string[], selector: string]
> = async (context, file_urls, selector) => {
	const root = context.project.config.root;

	const files: Drop_file_spec[] = await Promise.all(
		file_urls.map(async (url) => {
			const abs = resolve(root, url.replace(/^\//, ""));
			const data = (await readFile(abs)).toString("base64");
			const name = abs.split("/").pop()!;
			const ext = name.split(".").pop()!.toLowerCase();
			const mime_type = MIME_TYPES[ext] || "application/octet-stream";
			return { data, name, mime_type };
		})
	);

	const iframe = (context as any).iframe;
	await iframe
		.locator(selector)
		.first()
		.evaluate((target: Element, files: Drop_file_spec[]) => {
			const dt = new DataTransfer();
			for (const f of files) {
				const bytes = Uint8Array.from(atob(f.data), (c) => c.charCodeAt(0));
				dt.items.add(new File([bytes], f.name, { type: f.mime_type }));
			}

			target.dispatchEvent(
				new DragEvent("dragenter", {
					dataTransfer: dt,
					bubbles: true
				})
			);
			target.dispatchEvent(
				new DragEvent("dragover", {
					dataTransfer: dt,
					bubbles: true
				})
			);
			target.dispatchEvent(
				new DragEvent("drop", { dataTransfer: dt, bubbles: true })
			);
		}, files);
};

const MIME_TYPES: Record<string, string> = {
	txt: "text/plain",
	csv: "text/csv",
	json: "application/json",
	pdf: "application/pdf",
	jpg: "image/jpeg",
	jpeg: "image/jpeg",
	png: "image/png",
	gif: "image/gif",
	webp: "image/webp",
	svg: "image/svg+xml",
	mp4: "video/mp4",
	webm: "video/webm",
	ogg: "video/ogg",
	avi: "video/x-msvideo",
	wav: "audio/wav",
	mp3: "audio/mpeg",
	flac: "audio/flac"
};
DLCMD_EOF

# --- Modify js/tootils/package.json: add download-command export ---
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('js/tootils/package.json', 'utf8'));
pkg.exports['./download-command'] = './src/download-command.ts';
fs.writeFileSync('js/tootils/package.json', JSON.stringify(pkg, null, '\t') + '\n');
"

# --- Modify js/tootils/src/render.ts: add event buffer, retrospective listen, mock_client, re-exports ---
git apply --whitespace=fix - <<'RENDER_PATCH'
diff --git a/js/tootils/src/render.ts b/js/tootils/src/render.ts
index 6a13767251..af0bd590df 100644
--- a/js/tootils/src/render.ts
+++ b/js/tootils/src/render.ts
@@ -58,19 +58,21 @@ export async function render<
 	props?: Omit<Props, "gradio" | "loading_status"> & {
 		loading_status?: LoadingStatus;
 	},
-	_container?: HTMLElement
+	options?: {
+		container?: HTMLElement;
+	}
 ): Promise<
 	RenderResult<T> & {
-		listen: (event_name: string) => Mock;
+		listen: (event_name: string, opts?: { retrospective?: boolean }) => Mock;
 		set_data: (data: Record<string, any>) => Promise<void>;
 		get_data: () => Promise<Record<string, any>>;
 	}
 > {
 	let container: HTMLElement;
-	if (!_container) {
+	if (!options?.container) {
 		container = document.body;
 	} else {
-		container = _container;
+		container = options.container;
 	}

 	const target = container.appendChild(document.createElement("div"));
@@ -94,6 +96,7 @@ export async function render<
 	};

 	const event_listeners = new Map<string, Set<(data: any) => void>>();
+	const event_buffer: Array<{ event: string; data: any }> = [];

 	function notify_listeners(event: string, data: any): void {
 		const listeners = event_listeners.get(event);
@@ -105,15 +108,28 @@ export async function render<
 	}

 	const dispatcher = (_id: number, event: string, data: any): void => {
+		event_buffer.push({ event, data });
 		notify_listeners(event, data);
 	};

-	function listen(event_name: string): Mock {
+	function listen(
+		event_name: string,
+		opts?: { retrospective?: boolean }
+	): Mock {
 		const fn = vi.fn();
 		if (!event_listeners.has(event_name)) {
 			event_listeners.set(event_name, new Set());
 		}
 		event_listeners.get(event_name)!.add(fn);
+
+		if (opts?.retrospective) {
+			for (const entry of event_buffer) {
+				if (entry.event === event_name) {
+					fn(entry.data);
+				}
+			}
+		}
+
 		return fn;
 	}

@@ -242,4 +258,24 @@ export type FireFunction = (
 	event: Event
 ) => Promise<boolean>;

+export { download_file, upload_file, drop_file } from "./download.js";
+
+/**
+ * Creates a mock client suitable for components that use file uploads.
+ * The upload mock echoes back the input FileData unchanged.
+ */
+export function mock_client(): Record<string, any> {
+	return {
+		upload: async (file_data: any[]) => file_data,
+		stream: async () => ({ onmessage: null, close: () => {} })
+	};
+}
+export {
+	TEST_TXT,
+	TEST_JPG,
+	TEST_PNG,
+	TEST_MP4,
+	TEST_WAV,
+	TEST_PDF
+} from "./fixtures.js";
 export * from "@testing-library/dom";

RENDER_PATCH

# --- Modify js/spa/vite.config.ts: register browser commands ---
git apply --whitespace=fix - <<'VITE_PATCH'
diff --git a/js/spa/vite.config.ts b/js/spa/vite.config.ts
index 144b00e9df..6b20c53cdc 100644
--- a/js/spa/vite.config.ts
+++ b/js/spa/vite.config.ts
@@ -13,6 +13,11 @@ import prefixer from "postcss-prefix-selector";
 import { readFileSync } from "fs";
 import { resolve } from "path";
 import { playwright } from "@vitest/browser-playwright";
+import {
+	expect_download,
+	set_file_inputs,
+	drop_files
+} from "@self/tootils/download-command";

 /// <reference types="@vitest/browser/providers/playwright" />

@@ -156,6 +161,7 @@ export default defineConfig(({ mode, isSsrBuild }) => {
 		test: {
 			setupFiles: [resolve(__dirname, "../../.config/setup_vite_tests.ts")],
 			environment: TEST_MODE,
+
 			include:
 				TEST_MODE === "node"
 					? ["**/*.node-test.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"]
@@ -172,6 +178,12 @@ export default defineConfig(({ mode, isSsrBuild }) => {
 			},
 			browser: {
 				enabled: true,
+				headless: !!process.env.CI,
+				commands: {
+					expect_download,
+					set_file_inputs,
+					drop_files
+				},
 				provider: playwright({
 					contextOptions: {
 						permissions: [

VITE_PATCH

# --- Replace js/tootils/README.md ---
cat > js/tootils/README.md <<'README_EOF'
# `@gradio/tootils`

Unit testing utilities for Gradio Svelte components. Built on top of `@testing-library/dom` and `vitest`.

## `render`

Mounts a Gradio component into the DOM with all required shared props (dispatcher, i18n, theme, etc.) pre-configured. Returns query helpers, event utilities, and lifecycle controls.

```ts
import { render } from "@self/tootils";
import MyComponent from "./Index.svelte";

const result = await render(MyComponent, {
  value: "hello",
  label: "My input"
});
```

### Signature

```ts
function render(
  Component,
  props?,
  options?: { container?: HTMLElement }
): Promise<RenderResult>
```

#### `Component`

The Svelte component to mount. Accepts either a component constructor directly or a module with a `default` export.

#### `props`

Component props, excluding `gradio` and `loading_status` (which are provided automatically). You can override `loading_status` if needed:

```ts
await render(MyComponent, {
  value: "hello",
  loading_status: { status: "pending", /* ... */ }
});
```

Props listed in `allowed_shared_props` (from `@gradio/utils`) are separated out and passed via `shared_props`. All other props are passed as component-level props.

#### `options.container`

The parent DOM element to mount into. Defaults to `document.body`.

### Return value

`render` returns a promise that resolves to an object combining `@testing-library/dom` query helpers with Gradio-specific utilities:

#### DOM queries

All `@testing-library/dom` query functions are bound to the container and available directly on the result:

```ts
const { getByText, getByLabelText, queryByRole } = await render(MyComponent, {
  label: "Name"
});

const input = getByLabelText("Name");
```

See the [@testing-library/dom docs](https://testing-library.com/docs/queries/about) for the full list.

#### `container`

The root DOM element the component was mounted into.

#### `component`

The mounted Svelte component instance.

#### `listen`

Creates a `vi.fn()` mock that records all dispatched events for a given event name.

```ts
const { listen } = await render(MyComponent, { value: "" });

const change = listen("change");

// interact with the component...

expect(change).toHaveBeenCalledTimes(1);
expect(change).toHaveBeenCalledWith("new value");
```

##### Retrospective mode

By default, `listen` only captures events dispatched **after** it is called. If a component emits events during mount (before `listen` can be called), pass `{ retrospective: true }` to replay all buffered events onto the mock:

```ts
const { listen } = await render(MyComponent, { value: "hi" });

// "change" may have fired during mount — retrospective replays it
const change = listen("change", { retrospective: true });

expect(change).toHaveBeenCalledWith("hi");
```

All dispatched events are buffered from the moment the dispatcher is created (before mount), so retrospective mode has access to the complete event history.

#### `set_data`

Simulates the Gradio server sending new data to the component (as if via a backend update). Waits for two Svelte ticks to allow all reactive updates and side-effect events to settle before returning:

```ts
const { set_data, listen } = await render(MyComponent, { value: "" });

const change = listen("change");
await set_data({ value: "updated" });

expect(change).toHaveBeenCalledWith("updated");
```

#### `get_data`

Retrieves the component's current data as reported by its internal `get_data` handler:

```ts
const { get_data } = await render(MyComponent, { value: "hello" });

const data = await get_data();
expect(data.value).toBe("hello");
```

#### `debug`

Prints a pretty-formatted DOM tree of the container (or a specific element) to the console. Useful for debugging test failures:

```ts
const result = await render(MyComponent, { value: "hello" });

result.debug(); // prints full container
result.debug(someElement); // prints specific element
```

#### `unmount`

Removes the component from the DOM:

```ts
const { unmount } = await render(MyComponent, { value: "hello" });

// ...assertions...

unmount();
```

## `cleanup`

Unmounts all components mounted via `render` and removes their DOM nodes. Call this in an `afterEach` hook to prevent test pollution:

```ts
import { cleanup } from "@self/tootils";

afterEach(() => {
  cleanup();
});
```

## `fireEvent`

An async wrapper around `@testing-library/dom`'s `fireEvent`. Each event method waits for two Svelte ticks after firing, ensuring reactive state updates and any resulting event emissions have settled before your assertions run:

```ts
import { render, fireEvent } from "@self/tootils";

const { getByRole } = await render(MyComponent, { value: "" });

const input = getByRole("textbox");
await fireEvent.input(input, { target: { value: "hello" } });
await fireEvent.blur(input);

// state has settled — safe to assert
```

All standard DOM event methods are available (`click`, `input`, `change`, `focus`, `blur`, `keyDown`, etc.).

## `download_file`

Clicks an element and captures the resulting file download. This triggers a real browser download via Playwright's download event API — the file is actually downloaded and its content is readable.

Works with both download patterns used in Gradio components:
- Static `<a download href="...">` links (DownloadLink, FilePreview, etc.)
- Programmatic downloads that create an anchor, set `.href`/`.download`, and call `.click()` (DownloadButton, Gallery, Code, etc.)

```ts
import { render, download_file } from "@self/tootils/render";

const { container } = await render(FileComponent, {
  value: { url: "/files/data.csv", orig_name: "data.csv" }
});

const { suggested_filename, content } = await download_file("a[download]");

expect(suggested_filename).toBe("data.csv");
expect(content).toContain("col1,col2");
```

### Signature

```ts
function download_file(
  selector: string,
  options?: { timeout?: number }
): Promise<{ suggested_filename: string; content: string | null }>
```

#### `selector`

A CSS selector for the element to click. The click triggers the download.

#### `options.timeout`

How long to wait for the download event (default 5000ms). If no download is triggered within this window, the promise rejects.

#### Return value

- `suggested_filename` — the filename the browser would save the file as (from the `download` attribute or `Content-Disposition` header)
- `content` — the text content of the downloaded file, or `null` if the file couldn't be read

### How it works

This utility uses a [Vitest browser command](https://vitest.dev/guide/browser/commands) that runs server-side with access to the Playwright `Page` object. It sets up `page.waitForEvent("download")` **before** clicking the element, so the download event is never missed regardless of timing. The downloaded file is saved to a temp path by Playwright and its content is read back.

## `upload_file`

Sets files on an `<input type="file">` element using real file fixtures. Triggers the browser's native change event.

```ts
import { render, upload_file, mock_client, TEST_JPG } from "@self/tootils/render";

const { listen } = await render(ImageUpload, { interactive: true, client: mock_client() });
const upload = listen("upload");

await upload_file(TEST_JPG);

await vi.waitFor(() => expect(upload).toHaveBeenCalled());
```

### Signature

```ts
function upload_file(
  files: FileData | FileData[],
  selector?: string  // default: 'input[type="file"]'
): Promise<void>
```

## `drop_file`

Simulates dragging and dropping files onto an element. Reads fixture files from disk, constructs a real `DataTransfer` with `File` objects, and dispatches `dragenter`, `dragover`, and `drop` events on the target.

```ts
import { render, drop_file, mock_client, TEST_JPG } from "@self/tootils/render";

const { listen } = await render(ImageUpload, { interactive: true, client: mock_client() });
const upload = listen("upload");

await drop_file(TEST_JPG, "[aria-label='Click to upload or drop files']");

await vi.waitFor(() => expect(upload).toHaveBeenCalled());
```

### Signature

```ts
function drop_file(
  files: FileData | FileData[],
  selector: string
): Promise<void>
```

## `mock_client`

Creates a mock client suitable for components that use file uploads. The upload mock echoes back the input `FileData` unchanged, and the stream mock returns a no-op event source.

```ts
import { render, mock_client } from "@self/tootils/render";

await render(FileComponent, {
  interactive: true,
  root: "http://localhost:7860",
  client: mock_client()
});
```

## Test fixtures

Pre-built `FileData` instances pointing to existing test files in `test/test_files/`. Use these as `value` props or with `upload_file`/`drop_file`:

| Export | File | MIME type |
|--------|------|-----------|
| `TEST_TXT` | `alphabet.txt` | `text/plain` |
| `TEST_JPG` | `cheetah1.jpg` | `image/jpeg` |
| `TEST_PNG` | `bus.png` | `image/png` |
| `TEST_MP4` | `video_sample.mp4` | `video/mp4` |
| `TEST_WAV` | `audio_sample.wav` | `audio/wav` |
| `TEST_PDF` | `sample_file.pdf` | `application/pdf` |

```ts
import { render, TEST_PNG } from "@self/tootils/render";

// As a component value
await render(ImageComponent, { value: TEST_PNG });

// As an upload fixture
await upload_file(TEST_PNG);
```

Each fixture has `path`, `url`, `orig_name`, `size`, and `mime_type` set. The URLs are served by the Vite dev server during tests.

## Re-exports

Everything from `@testing-library/dom` is re-exported, so you can import query utilities, `screen`, `within`, etc. directly:

```ts
import { screen, within } from "@self/tootils";
```
README_EOF

echo "Patch applied successfully."
