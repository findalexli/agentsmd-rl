#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if [ -f packages/create-cloudflare/bin/c3.js ]; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/create-cloudflare/AGENTS.md b/packages/create-cloudflare/AGENTS.md
index afa7084592..4631f84112 100644
--- a/packages/create-cloudflare/AGENTS.md
+++ b/packages/create-cloudflare/AGENTS.md
@@ -2,19 +2,20 @@

 ## OVERVIEW

-Project scaffolding CLI for Cloudflare Workers. Single entry: `src/cli.ts` serves as CLI, library export, and bin target.
+Project scaffolding CLI for Cloudflare Workers. Main source entry: `src/cli.ts`. Bin entry: `bin/c3.js` (Node.js version gate shim).

 ## STRUCTURE

-- `src/cli.ts` — Main entry. Exports `main(argv)` for programmatic use, has shebang for direct execution
+- `bin/c3.js` — Bin shim that checks Node.js version before requiring `dist/cli.js`
+- `src/cli.ts` — Main entry. Exports `main(argv)` for programmatic use
 - `templates/` — Scaffolding templates (excluded from linting and most formatting)
 - `scripts/build.ts` — esbuild-based build → `dist/cli.js`

 ## BUILD

 - esbuild bundles `src/cli.ts` as CJS → `dist/cli.js`
-- `package.json` `main`, `exports["."]`, and `bin` all point at `dist/cli.js`
-- No separate bin shim — the built output IS the bin
+- `package.json` `main` and `exports["."]` point at `dist/cli.js`; `bin` points at `bin/c3.js`
+- `bin/c3.js` is a plain CommonJS shim that gates on Node.js version (read from `package.json` `engines.node`) before requiring `dist/cli.js`

 ## CONVENTIONS

diff --git a/packages/create-cloudflare/bin/c3.js b/packages/create-cloudflare/bin/c3.js
new file mode 100644
index 0000000000..47208a1cb0
--- /dev/null
+++ b/packages/create-cloudflare/bin/c3.js
@@ -0,0 +1,54 @@
+#!/usr/bin/env node
+
+const MIN_NODE_VERSION = require("../package.json").engines.node.replace(
+	">=",
+	""
+);
+
+// semiver implementation via https://github.com/lukeed/semiver/blob/ae7eebe6053c96be63032b14fb0b68e2553fcac4/src/index.js
+
+/**
+MIT License
+
+Copyright (c) Luke Edwards <luke.edwards05@gmail.com> (lukeed.com)
+
+Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
+
+The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
+
+THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
+
+ */
+
+var fn = new Intl.Collator(0, { numeric: 1 }).compare;
+
+function semiver(a, b, bool) {
+	a = a.split(".");
+	b = b.split(".");
+
+	return (
+		fn(a[0], b[0]) ||
+		fn(a[1], b[1]) ||
+		((b[2] = b.slice(2).join(".")),
+		(bool = /[.-]/.test((a[2] = a.slice(2).join(".")))),
+		bool == /[.-]/.test(b[2]) ? fn(a[2], b[2]) : bool ? -1 : 1)
+	);
+}
+
+// end semiver implementation
+
+function main() {
+	if (semiver(process.versions.node, MIN_NODE_VERSION) < 0) {
+		console.error(
+			`create-cloudflare requires at least Node.js v${MIN_NODE_VERSION}. You are using v${process.versions.node}. Please update your version of Node.js.
+
+Consider using a Node.js version manager such as https://volta.sh/ or https://github.com/nvm-sh/nvm.`
+		);
+		process.exitCode = 1;
+		return;
+	}
+
+	require("../dist/cli.js");
+}
+
+main();
diff --git a/packages/create-cloudflare/package.json b/packages/create-cloudflare/package.json
index e6412f53e3..9bba9e5d40 100644
--- a/packages/create-cloudflare/package.json
+++ b/packages/create-cloudflare/package.json
@@ -16,8 +16,9 @@
 		"url": "https://github.com/cloudflare/workers-sdk.git",
 		"directory": "packages/create-cloudflare"
 	},
-	"bin": "./dist/cli.js",
+	"bin": "./bin/c3.js",
 	"files": [
+		"bin",
 		"dist",
 		"templates",
 		"templates-experimental"
@@ -89,7 +90,7 @@
 		"yargs": "^17.7.2"
 	},
 	"engines": {
-		"node": ">=18.14.1"
+		"node": ">=20.0.0"
 	},
 	"volta": {
 		"extends": "../../package.json"

PATCH

echo "Patch applied successfully."
