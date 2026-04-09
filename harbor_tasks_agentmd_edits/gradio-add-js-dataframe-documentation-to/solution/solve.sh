#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied (check for distinctive content in new README)
if grep -q "## Install" js/dataframe/README.md 2>/dev/null && ! grep -q "standalone/README.md" js/dataframe/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the comprehensive patch
git apply - <<'PATCH'
diff --git a/js/_website/src/routes/[[version]]/docs/+layout.server.ts b/js/_website/src/routes/[[version]]/docs/+layout.server.ts
index feca3ece73d..513db511638 100644
--- a/js/_website/src/routes/[[version]]/docs/+layout.server.ts
+++ b/js/_website/src/routes/[[version]]/docs/+layout.server.ts
@@ -9,6 +9,8 @@ const VERSION = version.version;

 let cache = new Map();

+const components_to_document = ["dataframe", "js-client"];
+
 async function load_release_docs(
 	version: string
 ): Promise<typeof import("$lib/json/docs.json")> {
@@ -39,7 +41,10 @@ export async function load({ params, url }) {

 	let docs: { [key: string]: any } = docs_json.docs;
 	let js = docs_json.js || {};
-	let js_pages = docs_json.js_pages || [];
+	let js_pages =
+		docs_json.js_pages.filter((p: string) =>
+			components_to_document.includes(p)
+		) || [];
 	let js_client = docs_json.js_client;
 	let on_main = params.version === "main";
 	let pages: any = docs_json.pages;
diff --git a/js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts b/js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts
index ff3ffc1662e..ccbcdfc57a1 100644
--- a/js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts
+++ b/js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts
@@ -10,6 +10,7 @@ import "prismjs/components/prism-typescript";
 import "prismjs/components/prism-javascript";
 import "prismjs/components/prism-csv";
 import "prismjs/components/prism-markup";
+import "prism-svelte";

 function plugin() {
 	return function transform(tree: any) {
@@ -32,7 +33,11 @@ const langs = {
 	ts: "typescript",
 	javascript: "javascript",
 	js: "javascript",
-	directory: "json"
+	directory: "json",
+	svelte: "svelte",
+	sv: "svelte",
+	md: "markdown",
+	css: "css"
 };

 function highlight(code: string, lang: string | undefined) {
diff --git a/js/_website/src/routes/[[version]]/docs/js/+page.server.ts b/js/_website/src/routes/[[version]]/docs/js/+page.server.ts
index 50c23bae4b9..3bc9f6d5d68 100644
--- a/js/_website/src/routes/[[version]]/docs/js/+page.server.ts
+++ b/js/_website/src/routes/[[version]]/docs/js/+page.server.ts
@@ -2,8 +2,27 @@ import { redirect } from "@sveltejs/kit";

 export const prerender = true;

-export function load({ params }) {
-	if (params?.version) throw redirect(302, `/${params?.version}/docs/js/atoms`);
+	async function urlExists(fetch: any, url: string): Promise<boolean> {
+		try {
+			const res = await fetch(url, { method: "HEAD" });
+			return res.ok;
+		} catch (e) {
+			return false;
+		}
+	}

-	throw redirect(302, `/docs/js/atoms`);
+	export async function load({ params, fetch }) {
+		const url = params.version
+			? `/${params.version}/docs/js/dataframe`
+			: `/docs/js/dataframe`;
+		const fallback_url = params.version
+			? `/${params.version}/docs/js/js-client`
+			: `/docs/js/js-client`;
+		const exists = await urlExists(fetch, url);
+
+		if (exists) {
+			throw redirect(302, url);
+		}
+
+		throw redirect(302, fallback_url);
 }
diff --git a/js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts b/js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts
index 3ebc79fdbe6..1c8467b856e 100644
--- a/js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts
+++ b/js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts
@@ -10,6 +10,7 @@ import "prismjs/components/prism-typescript";
 import "prismjs/components/prism-javascript";
 import "prismjs/components/prism-csv";
 import "prismjs/components/prism-markup";
+import "prism-svelte";
 import { error } from "@sveltejs/kit";

 export const prerender = true;
@@ -32,8 +33,14 @@ const langs = {
 	shell: "bash",
 	json: "json",
 	typescript: "typescript",
+	ts: "typescript",
 	javascript: "javascript",
-	directory: "json"
+	js: "javascript",
+	directory: "json",
+	svelte: "svelte",
+	sv: "svelte",
+	md: "markdown",
+	css: "css"
 };

 function highlight(code: string, lang: string | undefined) {
diff --git a/js/_website/src/routes/changelog/+page.server.ts b/js/_website/src/routes/changelog/+page.server.ts
index af0f5298a16..56e30acf29f 100644
--- a/js/_website/src/routes/changelog/+page.server.ts
+++ b/js/_website/src/routes/changelog/+page.server.ts
@@ -13,6 +13,7 @@ import "prismjs/components/prism-json";
 import "prismjs/components/prism-typescript";
 import "prismjs/components/prism-csv";
 import "prismjs/components/prism-markup";
+import "prism-svelte";

 const langs = {
 	python: "python",
@@ -23,7 +24,14 @@ const langs = {
 	shell: "bash",
 	json: "json",
 	typescript: "typescript",
-	directory: "json"
+	ts: "typescript",
+	js: "javascript",
+	javascript: "javascript",
+	directory: "json",
+	svelte: "svelte",
+	sv: "svelte",
+	md: "markdown",
+	css: "css"
 };

 function highlight(code: string, lang: string | undefined) {
diff --git a/js/code/package.json b/js/code/package.json
index da1b83a185f..80383b268ff 100644
--- a/js/code/package.json
+++ b/js/code/package.json
@@ -38,14 +38,16 @@
 	"main": "./Index.svelte",
 	"exports": {
 		".": {
+			"types": "./dist/Index.svelte.d.ts",
 			"gradio": "./Index.svelte",
 			"svelte": "./dist/Index.svelte",
-			"types": "./dist/Index.svelte.d.ts"
+			"default": "./dist/Index.svelte"
 		},
 		"./example": {
+			"types": "./dist/Example.svelte.d.ts",
 			"gradio": "./Example.svelte",
 			"svelte": "./dist/Example.svelte",
-			"types": "./dist/Example.svelte.d.ts"
+			"default": "./dist/Example.svelte"
 		},
 		"./package.json": "./package.json"
 	},
PATCH

# Delete standalone README (git apply doesn't handle deletions well)
rm -f js/dataframe/standalone/README.md

# Update README with comprehensive docs
cat > js/dataframe/README.md << 'READMEEOF'
# @gradio/dataframe

Standalone Svelte component that brings Gradio's Dataframe UI to any Svelte/SvelteKit project.

This component is lightweight, virtualized for efficient rendering of large datasets, and offers features like column freezing, and customizable styling via CSS variables. Use this component when you need a highly interactive, accessible, and easily themeable table for user-facing applications, especially where seamless Svelte/SvelteKit integration is important.

## Install

With `npm`:

```shell
npm i @gradio/dataframe
```

With `pnpm`:

```shell
pnpm add @gradio/dataframe
```

**[View on npm](https://www.npmjs.com/package/@gradio/dataframe)**

## Usage (Svelte/SvelteKit)

```svelte
<script lang="ts">
  import Dataframe from "@gradio/dataframe";

  let value = {
    data: [
      ["Alice", 25, true],
      ["Bob", 30, false]
    ],
    headers: ["Name", "Age", "Active"],
  };

  function handle_change(e: any) {
    console.log("changed", e.detail);
  }

  function handle_select(e: any) {
    console.log("selected", e.detail);
  }

  function handle_input(e: any) {
    console.log("input", e.detail);
  }
</script>

<Dataframe
  bind:value
  {datatype}
  show_search="search"
  show_row_numbers={true}
  show_copy_button={true}
  show_fullscreen_button={true}
  editable={true}
  on:change={handle_change}
  on:select={handle_select}
  on:input={handle_input}
  />
```

## Props

```typescript
interface DataframeProps {

  /**
   * The value object containing the table data, headers, and optional metadata.
   * Example: { data: [...], headers: [...], metadata?: any }
   * Default: { data: [[]], headers: [] }
   */
  value: {
    data: (string | number | boolean)[][];
    headers: string[];
    metadata?: any;
  };

  /**
   * Array of data types per column. Supported: "str", "number", "bool", "date", "markdown", "html".
   * Default: []
   */
  datatype?: string[];

  /**
   * Enable or disable cell editing.
   * Default: true
   */
  editable?: boolean;

  /**
   * Show or hide the row number column.
   * Default: true
   */
  show_row_numbers?: boolean;

  /**
   * Show search input. Can be "search", "filter", or "none.
   * Default: "none"
   */
  show_search?: "none" | "search" | "filter" | boolean;

  /**
   * Show or hide the copy to clipboard button.
   * Default: true
   */
  show_copy_button?: boolean;

  /**
   * Show or hide the fullscreen toggle button.
   * Default: true
   */
  show_fullscreen_button?: boolean;

  /**
   * Accessible caption for the table.
   * Default: null
   */
  label?: string | null;

  /**
   * Show or hide the dataframe label.
   * Default: true
   */
  show_label?: boolean;

  /**
   * (Optional) Set column widths in CSS units (e.g. ["100px", "20%", ...]).
   */
  column_widths?: string[];

  /**
   * (Optional) Set the maximum height of the table in pixels.
   * Default: 500
   */
  max_height?: number;

  /**
   * (Optional) Set the maximum number of characters per cell.
   */
  max_chars?: number;

  /**
   * (Optional) Enable or disable line breaks in cells.
   * Default: true
   */
  line_breaks?: boolean;

  /**
   * (Optional) Enable or disable text wrapping in cells.
   * Default: false
   */
  wrap?: boolean;
}
```

## Events

The component emits the following events:

```ts
// Fired when table data changes
on:change={(e: CustomEvent<{ data: (string | number | boolean)[][]; headers: string[]; metadata: any }>) => void}

// Fired when a cell is selected
on:select={(e: CustomEvent<{ index: number[]; value: any; selected: boolean }>) => void}

// Fired on user input (search/filter)
on:input={(e: CustomEvent<string | null>) => void}
```

Example:

```svelte
<Dataframe
  on:change={(e) => console.log('data', e.detail)}
  on:input={(e) => console.log('input', e.detail)}
  on:select={(e) => console.log('select', e.detail)}
/>
```

## TypeScript

The package publishes `types.d.ts` with `DataframeProps` module declarations.

## Custom Styling

The standalone package exposes a small set of public CSS variables you can use to theme the Dataframe. These variables are namespaced with `--gr-df-*` and are the recommended way to override the default styling.

**Color Variables**
- `--gr-df-table-bg-even` — background for even rows
- `--gr-df-table-bg-odd` — background for odd rows
- `--gr-df-copied-cell-color` - background for copied cells
- `--gr-df-table-border` — table border color
- `--gr-df-table-text` — table text color
- `--gr-df-accent` — primary accent color
- `--gr-df-accent-soft` — soft/pale accent color

**Font Variables**
- `--gr-df-font-size` — table body font-size
- `--gr-df-font-mono` — monospace font family
- `--gr-df-font-sans` — sans serif font family

**Border/Radius Variables**
- `--gr-df-table-radius` — table corner radius

Example:

```svelte
<div class="df-theme">
  <Dataframe ... />
</div>

<style>
  .df-theme {
    --gr-df-accent: #7c3aed;
  }
</style>
```

Alternatively, you can target internal classes within the Dataframe using a global override.

```css
.df-theme :global(.cell-wrap) {
  background-color: #7c3aed ;
}
```

**Note:** This standalone component does **not** currently support the file upload functionality (e.g. drag-and-dropping to populate the dataframe) that is available in the Gradio Dataframe component.


## License

MIT

READMEEOF

echo "Patch applied successfully."
