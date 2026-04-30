#!/bin/bash
set -euo pipefail

cd /workspace/remix

# Idempotency check: if the patch is already applied, exit early
if grep -q "'nameless-wildcard'" packages/route-pattern/src/lib/route-pattern.test.ts 2>/dev/null; then
  echo "Patch already applied, skipping."
  exit 0
fi

git apply <<'PATCH'
diff --git a/packages/route-pattern/.changes/patch.href-errors.md b/packages/route-pattern/.changes/patch.href-errors.md
new file mode 100644
index 000000000..30f85a75f
--- /dev/null
+++ b/packages/route-pattern/.changes/patch.href-errors.md
@@ -0,0 +1,7 @@
+Previously, `href` was throwing an `HrefError` with `missing-params` type when a nameless wildcard was encountered outside of an optional.
+But that was misleading since nameless optionals aren't something the user should be passing in values for.
+Instead, `href` now throws an `HrefError` with the correct `nameless-wildcard` type for this case.
+
+Error messages have also been improved for many of the `HrefError` types.
+Notably, the variants shown in `missing-params` were confusing since they leaked internal formatting for params.
+That has been removed and the resulting error message is now shorter and simpler.
diff --git a/packages/route-pattern/src/lib/route-pattern.test.ts b/packages/route-pattern/src/lib/route-pattern.test.ts
index 8ac1ef6e4..c5ffdd5f5 100644
--- a/packages/route-pattern/src/lib/route-pattern.test.ts
+++ b/packages/route-pattern/src/lib/route-pattern.test.ts
@@ -472,10 +472,10 @@ describe('RoutePattern', () => {
         assert.equal(result, 'https://staging.example.com/path')
       })

-      it('throws for unnamed wildcard', () => {
+      it('throws for nameless wildcard', () => {
         let pattern = new RoutePattern('://*.example.com/path')
         // @ts-expect-error - missing required param
-        assert.throws(() => pattern.href(), hrefError('missing-params'))
+        assert.throws(() => pattern.href(), hrefError('nameless-wildcard'))
       })

       it('includes optional with static content', () => {
@@ -559,7 +559,7 @@ describe('RoutePattern', () => {
       it('throws for unnamed wildcard', () => {
         let pattern = new RoutePattern('/files/*')
         // @ts-expect-error - missing required param
-        assert.throws(() => pattern.href(), hrefError('missing-params'))
+        assert.throws(() => pattern.href(), hrefError('nameless-wildcard'))
       })

       it('supports repeated params', () => {
@@ -818,7 +818,7 @@ describe('RoutePattern', () => {
         })
       })

-      it('excludes unnamed wildcard from params', () => {
+      it('excludes nameless wildcard from params', () => {
         assertMatch('://*.example.com/path', 'https://api.example.com/path', {})
       })
     })
@@ -850,7 +850,7 @@ describe('RoutePattern', () => {
         })
       })

-      it('excludes unnamed wildcard from params', () => {
+      it('excludes nameless wildcard from params', () => {
         assertMatch('/posts/*/comments', 'https://example.com/posts/123/comments', {})
       })
     })
diff --git a/packages/route-pattern/src/lib/route-pattern.ts b/packages/route-pattern/src/lib/route-pattern.ts
index fa4b06e7c..046a2ed02 100644
--- a/packages/route-pattern/src/lib/route-pattern.ts
+++ b/packages/route-pattern/src/lib/route-pattern.ts
@@ -146,15 +146,15 @@ export class RoutePattern<source extends string = string> {
           pattern: this,
         })
       }
-      let hostname = hrefOrThrow(this.ast.hostname, params, this)
+      let hostname = Href.part(this, this.ast.hostname, params)

       // port
       let port = this.ast.port === null ? '' : `:${this.ast.port}`
       result += `${protocol}://${hostname}${port}`
     }

     // pathname
-    let pathname = hrefOrThrow(this.ast.pathname, params, this)
+    let pathname = Href.part(this, this.ast.pathname, params)
     result += '/' + pathname

     // search
@@ -229,20 +229,3 @@ export class RoutePattern<source extends string = string> {
     return this.match(url) !== null
   }
 }
-
-function hrefOrThrow(
-  part: PartPattern,
-  params: Record<string, string | number>,
-  pattern: RoutePattern,
-): string {
-  let result = Href.part(part, params)
-  if (result === null) {
-    throw new Href.HrefError({
-      type: 'missing-params',
-      pattern,
-      partPattern: part,
-      params,
-    })
-  }
-  return result
-}
diff --git a/packages/route-pattern/src/lib/route-pattern/href.test.ts b/packages/route-pattern/src/lib/route-pattern/href.test.ts
index 3c0e1ccd4..aa9f36fd1 100644
--- a/packages/route-pattern/src/lib/route-pattern/href.test.ts
+++ b/packages/route-pattern/src/lib/route-pattern/href.test.ts
@@ -8,7 +8,7 @@ import { RoutePattern } from '../route-pattern.ts'

 describe('HrefError', () => {
   describe('missing-hostname', () => {
-    it('shows error message with pattern', () => {
+    it('shows pattern', () => {
       let pattern = new RoutePattern('https://*:8080/api')
       let error = new HrefError({
         type: 'missing-hostname',
@@ -26,69 +26,22 @@ describe('HrefError', () => {
   })

   describe('missing-params', () => {
-    it('shows missing param for single variant', () => {
-      let pattern = new RoutePattern('https://example.com/:id')
+    it('shows missing param, pattern, and params', () => {
+      let pattern = new RoutePattern('https://example.com/:collection/:id')
       let error = new HrefError({
         type: 'missing-params',
         pattern,
         partPattern: pattern.ast.pathname,
+        missingParams: ['collection', 'id'],
         params: {},
       })
       assert.equal(
         error.toString(),
         dedent`
-          HrefError: missing params
+          HrefError: missing param(s): 'collection', 'id'

-          Pattern: https://example.com/:id
+          Pattern: https://example.com/:collection/:id
           Params: {}
-          Pathname variants:
-            - {:id} (missing: id)
-        `,
-      )
-    })
-
-    it('shows missing params across multiple variants', () => {
-      let pattern = new RoutePattern('https://example.com/:a/:b(/:c)')
-      let error = new HrefError({
-        type: 'missing-params',
-        pattern,
-        partPattern: pattern.ast.pathname,
-        params: { a: 'x' },
-      })
-      assert.equal(
-        error.toString(),
-        dedent`
-          HrefError: missing params
-
-          Pattern: https://example.com/:a/:b(/:c)
-          Params: {"a":"x"}
-          Pathname variants:
-            - {:a}/{:b} (missing: b)
-            - {:a}/{:b}/{:c} (missing: b, c)
-        `,
-      )
-    })
-
-    it('shows missing dependent params', () => {
-      let pattern = new RoutePattern('https://example.com/:a(:b)-:a(:c)')
-      let error = new HrefError({
-        type: 'missing-params',
-        pattern,
-        partPattern: pattern.ast.pathname,
-        params: { b: 'thing' },
-      })
-      assert.equal(
-        error.toString(),
-        dedent`
-          HrefError: missing params
-
-          Pattern: https://example.com/:a(:b)-:a(:c)
-          Params: {"b":"thing"}
-          Pathname variants:
-            - {:a}-{:a} (missing: a)
-            - {:a}-{:a}{:c} (missing: a, c)
-            - {:a}{:b}-{:a} (missing: a)
-            - {:a}{:b}-{:a}{:c} (missing: a, c)
         `,
       )
     })
@@ -106,7 +59,7 @@ describe('HrefError', () => {
       assert.equal(
         error.toString(),
         dedent`
-          HrefError: missing required search param(s) 'q'
+          HrefError: missing required search param(s): 'q'

           Pattern: https://example.com/search?q=
           Search params: {}
@@ -125,7 +78,7 @@ describe('HrefError', () => {
       assert.equal(
         error.toString(),
         dedent`
-          HrefError: missing required search param(s) 'q, sort'
+          HrefError: missing required search param(s): 'q', 'sort'

           Pattern: https://example.com/search?q=&sort=
           Search params: {"page":1}
diff --git a/packages/route-pattern/src/lib/route-pattern/href.ts b/packages/route-pattern/src/lib/route-pattern/href.ts
index a55afb280..f25ca4b05 100644
--- a/packages/route-pattern/src/lib/route-pattern/href.ts
+++ b/packages/route-pattern/src/lib/route-pattern/href.ts
@@ -21,11 +21,14 @@ type ParamsArg<source extends string> =
 /**
  * Generate a partial href from a part pattern and params.
  *
+ * @param pattern The route pattern containing the part pattern.
  * @param partPattern The part pattern to generate an href for.
  * @param params The parameters to substitute into the pattern.
  * @returns The href (URL) for the given params, or null if no variant matches.
  */
-export function part(partPattern: PartPattern, params: Params): string | null {
+export function part(pattern: RoutePattern, partPattern: PartPattern, params: Params): string {
+  let missingParams: Array<string> = []
+
   let stack: Array<{ begin?: number; href: string }> = [{ href: '' }]
   let i = 0
   while (i < partPattern.tokens.length) {
@@ -54,7 +57,15 @@ export function part(partPattern: PartPattern, params: Params): string | null {
     if (token.type === ':' || token.type === '*') {
       let value = params[token.name]
       if (value === undefined) {
-        if (stack.length <= 1) return null // todo: error
+        if (stack.length <= 1) {
+          if (token.name === '*') {
+            throw new HrefError({
+              type: 'nameless-wildcard',
+              pattern,
+            })
+          }
+          missingParams.push(token.name)
+        }
         let frame = stack.pop()!
         i = partPattern.optionals.get(frame.begin!)! + 1
         continue
@@ -65,6 +76,15 @@ export function part(partPattern: PartPattern, params: Params): string | null {
     }
     unreachable(token.type)
   }
+  if (missingParams.length > 0) {
+    throw new HrefError({
+      type: 'missing-params',
+      pattern,
+      partPattern,
+      missingParams,
+      params,
+    })
+  }
   if (stack.length !== 1) unreachable()
   return stack[0].href
 }
@@ -139,12 +159,13 @@ type HrefErrorDetails =
       type: 'missing-params'
       pattern: RoutePattern
       partPattern: PartPattern
+      missingParams: Array<string>
       params: Record<string, string | number>
     }
   | {
       type: 'missing-search-params'
       pattern: RoutePattern
-      missingParams: string[]
+      missingParams: Array<string>
       searchParams: SearchParams
     }
   | {
@@ -175,23 +196,14 @@ export class HrefError extends Error {
     }

     if (details.type === 'missing-search-params') {
-      let params = details.missingParams.join(', ')
+      let params = details.missingParams.map((p) => `'${p}'`).join(', ')
       let searchParamsStr = JSON.stringify(details.searchParams)
-      return `missing required search param(s) '${params}'\n\nPattern: ${pattern}\nSearch params: ${searchParamsStr}`
+      return `missing required search param(s): ${params}\n\nPattern: ${pattern}\nSearch params: ${searchParamsStr}`
     }

     if (details.type === 'missing-params') {
-      let paramNames = Object.keys(details.params)
-      let variants = details.partPattern.variants.map((variant) => {
-        let key = variant.toString()
-        let missing = Array.from(
-          new Set(variant.params.filter((p) => !paramNames.includes(p.name)).map((p) => p.name)),
-        )
-        return `  - ${key || '<empty>'} (missing: ${missing.join(', ')})`
-      })
-      let partTitle =
-        details.partPattern.type.charAt(0).toUpperCase() + details.partPattern.type.slice(1)
-      return `missing params\n\nPattern: ${pattern}\nParams: ${JSON.stringify(details.params)}\n${partTitle} variants:\n${variants.join('\n')}`
+      let params = details.missingParams.map((p) => `'${p}'`).join(', ')
+      return `missing param(s): ${params}\n\nPattern: ${pattern}\nParams: ${JSON.stringify(details.params)}`
     }

     unreachable(details)
PATCH

echo "Patch applied successfully."
