#!/bin/bash
set -e

cd /workspace/oxc

# Apply the fix for benchmark imports
# Using a distinctive line from the patch for idempotency check
if grep -q 'import { parseAsync, parseSync } from' napi/parser/bench.bench.js; then
    cat <<'PATCH' > /tmp/fix.patch
--- a/napi/parser/bench.bench.js
+++ b/napi/parser/bench.bench.js
@@ -2,13 +2,13 @@ import { writeFile } from "node:fs/promises";
 import { join as pathJoin } from "node:path";
 import { bench, describe } from "vitest";
 import { parseRawSync } from "./src-js/bindings.js";
-import { parseAsync, parseSync } from "./src-js/index.js";
+import { parse as parseAsync, parseSync } from "./src-js/index.js";

 // Internals
-import { DATA_POINTER_POS_32, PROGRAM_OFFSET } from "./generated/constants.js";
-import { deserialize as deserializeJS } from "./generated/deserialize/js.js";
-import { deserialize as deserializeTS } from "./generated/deserialize/ts.js";
-import { walkProgram } from "./generated/lazy/walk.js";
+import { DATA_POINTER_POS_32, PROGRAM_OFFSET } from "./src-js/generated/constants.js";
+import { deserialize as deserializeJS } from "./src-js/generated/deserialize/js.js";
+import { deserialize as deserializeTS } from "./src-js/generated/deserialize/ts.js";
+import { walkProgram } from "./src-js/generated/lazy/walk.js";
 import { isJsAst, prepareRaw, returnBufferToCache } from "./src-js/raw-transfer/common.js";
 import { TOKEN } from "./src-js/raw-transfer/lazy-common.js";
 import { getVisitorsArr, Visitor } from "./src-js/raw-transfer/visitor.js";
PATCH
    git apply /tmp/fix.patch
    echo "Fix applied successfully"
else
    echo "Fix already applied or file has different content"
fi
