#!/bin/bash
set -e

cd /workspace/workers-sdk

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/packages/miniflare/src/plugins/core/modules.ts b/packages/miniflare/src/plugins/core/modules.ts
index 238c855039..dc91dc5d38 100644
--- a/packages/miniflare/src/plugins/core/modules.ts
+++ b/packages/miniflare/src/plugins/core/modules.ts
@@ -122,7 +122,7 @@ export function compileModuleRules(rules: ModuleRule[]) {
 		if (finalisedTypes.has(rule.type)) continue;
 		compiledRules.push({
 			type: rule.type,
-			include: globsToRegExps(rule.include),
+			include: globsToRegExps(rule.include, { endAnchor: true }),
 		});
 		if (!rule.fallthrough) finalisedTypes.add(rule.type);
 	}
diff --git a/packages/miniflare/src/shared/matcher.ts b/packages/miniflare/src/shared/matcher.ts
index 856af3ea25..580a238b3f 100644
--- a/packages/miniflare/src/shared/matcher.ts
+++ b/packages/miniflare/src/shared/matcher.ts
@@ -1,21 +1,32 @@
 import globToRegexp from "glob-to-regexp";
 import { MatcherRegExps } from "../workers";
 
-export function globsToRegExps(globs: string[] = []): MatcherRegExps {
+export function globsToRegExps(
+	globs: string[] = [],
+	{ endAnchor }: { endAnchor?: boolean } = {}
+): MatcherRegExps {
 	const include: RegExp[] = [];
 	const exclude: RegExp[] = [];
 	// Setting `flags: "g"` removes "^" and "$" from the generated regexp,
 	// allowing matches anywhere in the path...
 	// (https://github.com/fitzgen/glob-to-regexp/blob/2abf65a834259c6504ed3b80e85f893f8cd99127/index.js#L123-L127)
 	const opts: globToRegexp.Options = { globstar: true, flags: "g" };
+	// When `endAnchor` is true, we re-add the trailing "$" that was stripped.
+	// Without it, a pattern like `**/*.wasm` incorrectly matches `foo.wasm.js`
+	// since the regex matches `foo.wasm` anywhere inside the string. The leading
+	// "^" is intentionally kept absent so the pattern can match anywhere within
+	// an absolute path (e.g. `**/*.wasm` still matches `/abs/path/to/foo.wasm`).
+	const suffix = endAnchor ? "$" : "";
 	for (const glob of globs) {
 		// ...however, we don't actually want to include the "g" flag, since it will
 		// change `lastIndex` as paths are matched, and we want to reuse `RegExp`s.
 		// So, reconstruct each `RegExp` without any flags.
 		if (glob.startsWith("!")) {
-			exclude.push(new RegExp(globToRegexp(glob.slice(1), opts), ""));
+			exclude.push(
+				new RegExp(globToRegexp(glob.slice(1), opts).source + suffix)
+			);
 		} else {
-			include.push(new RegExp(globToRegexp(glob, opts), ""));
+			include.push(new RegExp(globToRegexp(glob, opts).source + suffix));
 		}
 	}
 	return { include, exclude };
PATCH

# Rebuild miniflare
pnpm run build --filter miniflare
