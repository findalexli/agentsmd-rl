#!/bin/bash
set -euo pipefail

cd /workspace/remix

# Idempotency check
if grep -q 'paramsMeta:' packages/route-pattern/src/lib/route-pattern.ts 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply <<'PATCH'
diff --git a/packages/route-pattern/.changes/minor.rename-meta-to-paramsMeta.md b/packages/route-pattern/.changes/minor.rename-meta-to-paramsMeta.md
new file mode 100644
index 00000000000..9c66fb0fec1
--- /dev/null
+++ b/packages/route-pattern/.changes/minor.rename-meta-to-paramsMeta.md
@@ -0,0 +1,36 @@
+BREAKING CHANGE: Rename match `meta` to `paramsMeta`
+
+For `RoutePattern.match` and `type RoutePatternMatch`:
+
+```ts
+import { RoutePattern, type RoutePatternMatch } from "@remix-run/route-pattern"
+
+let pattern = new RoutePattern("...")
+let match = pattern.match(url)
+
+// BEFORE
+type Meta = RoutePatternMatch['meta']
+match.meta
+
+// AFTER
+type ParamsMeta = RoutePatternMatch['paramsMeta']
+match.paramsMeta
+```
+
+For `Matcher.match` and `type Match`:
+
+```ts
+import { Matcher, type Match } from "@remix-run/route-pattern"
+
+let matcher: Matcher = new ArrayMatcher() // Or TrieMatcher
+
+let match = matcher.match(url)
+
+// BEFORE
+type Meta = Match['meta']
+match.meta
+
+// AFTER
+type ParamsMeta = Match['paramsMeta']
+match.paramsMeta
+```
diff --git a/packages/route-pattern/src/lib/route-pattern.ts b/packages/route-pattern/src/lib/route-pattern.ts
index 1146dffc10f..e9effdc1035 100644
--- a/packages/route-pattern/src/lib/route-pattern.ts
+++ b/packages/route-pattern/src/lib/route-pattern.ts
@@ -34,7 +34,12 @@ export type RoutePatternMatch<source extends string = string> = {
   pattern: RoutePattern
   url: URL
   params: Params<source>
-  meta: {
+
+  /**
+   * Rich information about matched params (variables and wildcards) in the hostname and pathname,
+   * analogous to RegExp groups/indices.
+   */
+  paramsMeta: {
     hostname: PartPatternMatch
     pathname: PartPatternMatch
   }
@@ -232,7 +237,7 @@ export class RoutePattern<source extends string = string> {
       pattern: this,
       url,
       params: params as Params<source>,
-      meta: { hostname: hostname ?? [], pathname },
+      paramsMeta: { hostname: hostname ?? [], pathname },
     }
   }

diff --git a/packages/route-pattern/src/lib/specificity.ts b/packages/route-pattern/src/lib/specificity.ts
index 16495f197e1..c5871bcd1c6 100644
--- a/packages/route-pattern/src/lib/specificity.ts
+++ b/packages/route-pattern/src/lib/specificity.ts
@@ -65,11 +65,11 @@ export function compare(a: RoutePatternMatch, b: RoutePatternMatch): -1 | 0 | 1
   }

   // Hostname comparison
-  let hostnameResult = compareHostname(a.url.hostname, a.meta.hostname, b.meta.hostname)
+  let hostnameResult = compareHostname(a.url.hostname, a.paramsMeta.hostname, b.paramsMeta.hostname)
   if (hostnameResult !== 0) return hostnameResult

   // Pathname comparison
-  let pathnameResult = comparePathname(a.meta.pathname, b.meta.pathname)
+  let pathnameResult = comparePathname(a.paramsMeta.pathname, b.paramsMeta.pathname)
   if (pathnameResult !== 0) return pathnameResult

   // Search comparison
@@ -81,8 +81,8 @@ export function compare(a: RoutePatternMatch, b: RoutePatternMatch): -1 | 0 | 1

 function compareHostname(
   hostname: string,
-  a: RoutePatternMatch['meta']['hostname'],
-  b: RoutePatternMatch['meta']['hostname'],
+  a: RoutePatternMatch['paramsMeta']['hostname'],
+  b: RoutePatternMatch['paramsMeta']['hostname'],
 ): -1 | 0 | 1 {
   if (a.length === 0 && b.length === 0) return 0
   if (a.length === 0 && b.length > 0) return 1
@@ -123,8 +123,8 @@ function compareHostname(
 }

 function comparePathname(
-  a: RoutePatternMatch['meta']['pathname'],
-  b: RoutePatternMatch['meta']['pathname'],
+  a: RoutePatternMatch['paramsMeta']['pathname'],
+  b: RoutePatternMatch['paramsMeta']['pathname'],
 ): -1 | 0 | 1 {
   if (a.length === 0 && b.length === 0) return 0
   if (a.length === 0 && b.length > 0) return 1
diff --git a/packages/route-pattern/src/lib/trie-matcher.test.ts b/packages/route-pattern/src/lib/trie-matcher.test.ts
index eb3dc832bf3..cb29efc7349 100644
--- a/packages/route-pattern/src/lib/trie-matcher.test.ts
+++ b/packages/route-pattern/src/lib/trie-matcher.test.ts
@@ -95,8 +95,8 @@ describe('TrieMatcher', () => {
         let match = matcher.match('https://example.com/users/123')
         assert.ok(match)
         assert.deepEqual(match.params, { id: '123' })
-        assert.equal(match.meta.pathname.length, 1)
-        assert.deepEqual(match.meta.pathname[0], {
+        assert.equal(match.paramsMeta.pathname.length, 1)
+        assert.deepEqual(match.paramsMeta.pathname[0], {
           name: 'id',
           type: ':',
           value: '123',
@@ -112,15 +112,15 @@ describe('TrieMatcher', () => {
         let match = matcher.match('https://example.com/api/v2/users/456')
         assert.ok(match)
         assert.deepEqual(match.params, { version: '2', id: '456' })
-        assert.equal(match.meta.pathname.length, 2)
-        assert.deepEqual(match.meta.pathname[0], {
+        assert.equal(match.paramsMeta.pathname.length, 2)
+        assert.deepEqual(match.paramsMeta.pathname[0], {
           name: 'version',
           type: ':',
           value: '2',
           begin: 5,
           end: 6,
         })
-        assert.deepEqual(match.meta.pathname[1], {
+        assert.deepEqual(match.paramsMeta.pathname[1], {
           name: 'id',
           type: ':',
           value: '456',
@@ -138,8 +138,8 @@ describe('TrieMatcher', () => {
         let match = matcher.match('https://example.com/files/docs/readme.txt')
         assert.ok(match)
         assert.deepEqual(match.params, { path: 'docs/readme.txt' })
-        assert.equal(match.meta.pathname.length, 1)
-        assert.deepEqual(match.meta.pathname[0], {
+        assert.equal(match.paramsMeta.pathname.length, 1)
+        assert.deepEqual(match.paramsMeta.pathname[0], {
           name: 'path',
           type: '*',
           value: 'docs/readme.txt',
diff --git a/packages/route-pattern/src/lib/trie-matcher.ts b/packages/route-pattern/src/lib/trie-matcher.ts
index ea6647fd6d2..6327fc75269 100644
--- a/packages/route-pattern/src/lib/trie-matcher.ts
+++ b/packages/route-pattern/src/lib/trie-matcher.ts
@@ -48,7 +48,7 @@ export class TrieMatcher<data = unknown> implements Matcher<data> {
           pattern: match.pattern,
           url,
           params: match.params,
-          meta: { hostname: match.hostname, pathname: match.pathname },
+          paramsMeta: { hostname: match.hostname, pathname: match.pathname },
           data: match.data,
         }
       })
PATCH
