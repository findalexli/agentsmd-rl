#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency guard: if the patch's distinctive line is already present, do nothing.
if grep -q '& Record<string, unknown>' packages/route-pattern/src/lib/types/href.ts 2>/dev/null; then
    echo "Patch already applied — skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/route-pattern/.changes/patch.href-types-allow-extra-params.md b/packages/route-pattern/.changes/patch.href-types-allow-extra-params.md
new file mode 100644
index 00000000000..6ff31830017
--- /dev/null
+++ b/packages/route-pattern/.changes/patch.href-types-allow-extra-params.md
@@ -0,0 +1,18 @@
+Previously, including extra params in `RoutePattern.href` resulted in a type error:
+
+```ts
+let pattern = new RoutePattern("/posts/:id")
+pattern.href({ id : 1, extra: "stuff" })
+//                     ^^^^^
+// 'extra' does not exist in type 'HrefParams<"/posts/:id">'
+```
+
+Now, extra params are allowed and autocomplete for inferred params still works:
+
+```ts
+let pattern = new RoutePattern("/posts/:id")
+pattern.href({ id : 1, extra: "stuff" }) // no type error
+
+pattern.href({   })
+//             ^ autocomplete suggests `id`
+```
diff --git a/packages/route-pattern/src/lib/route-pattern.test.ts b/packages/route-pattern/src/lib/route-pattern.test.ts
index 9c279970084..bda97bc61ea 100644
--- a/packages/route-pattern/src/lib/route-pattern.test.ts
+++ b/packages/route-pattern/src/lib/route-pattern.test.ts
@@ -519,6 +519,18 @@ describe('RoutePattern', () => {
           assert.equal(result, '/posts/123')
         })

+        it('works with number params', () => {
+          let pattern = new RoutePattern('/posts/:id')
+          let result = pattern.href({ id: 123 })
+          assert.equal(result, '/posts/123')
+        })
+
+        it('ignores unrelated params', () => {
+          let pattern = new RoutePattern('/posts/:id')
+          let result = pattern.href({ id: '123', page: '2', sort: 'desc' })
+          assert.equal(result, '/posts/123')
+        })
+
         it('throws when missing', () => {
           let pattern = new RoutePattern('/posts/:id')
           // @ts-expect-error - missing required param
@@ -538,11 +550,23 @@ describe('RoutePattern', () => {
         assert.equal(result, '/files/docs/readme.md')
       })

+      it('supports wildcard with number param', () => {
+        let pattern = new RoutePattern('/files/*path')
+        let result = pattern.href({ path: 123 })
+        assert.equal(result, '/files/123')
+      })
+
       it('throws for unnamed wildcard', () => {
         let pattern = new RoutePattern('/files/*')
         // @ts-expect-error - missing required param
         assert.throws(() => pattern.href(), hrefError('missing-params'))
       })
+
+      it('supports repeated params', () => {
+        let pattern = new RoutePattern('/:lang/users/:userId/:lang/posts/:postId')
+        let result = pattern.href({ lang: 'en', userId: '42', postId: '123' })
+        assert.equal(result, '/en/users/42/en/posts/123')
+      })
     })

     describe('pattern with optionals', () => {
@@ -633,6 +657,12 @@ describe('RoutePattern', () => {
           assert.equal(result, '/posts')
         })
       })
+
+      it('handles optional locale and page on home route', () => {
+        let pattern = new RoutePattern('(/:locale)(/:page)')
+        let result = pattern.href()
+        assert.equal(result, '/')
+      })
     })

     describe('search params', () => {
diff --git a/packages/route-pattern/src/lib/types/href.ts b/packages/route-pattern/src/lib/types/href.ts
index 2678673d9ac..a2c1eec5e8e 100644
--- a/packages/route-pattern/src/lib/types/href.ts
+++ b/packages/route-pattern/src/lib/types/href.ts
@@ -4,12 +4,13 @@ import type * as Search from '../route-pattern/search.ts'
 type ParamValue = string | number

 // prettier-ignore
-export type HrefArgs<T extends string> =
-  [RequiredParams<T>] extends [never] ?
+export type HrefArgs<source extends string> =
+  [RequiredParams<source>] extends [never] ?
     [] | [null | undefined | Record<string, any>] | [null | undefined | Record<string, any>, Search.HrefParams] :
-    [HrefParams<T>, Search.HrefParams] | [HrefParams<T>]
+    [HrefParams<source>, Search.HrefParams] | [HrefParams<source>]

 // prettier-ignore
-type HrefParams<T extends string> =
-  Record<RequiredParams<T>, ParamValue> &
-  Partial<Record<OptionalParams<T>, ParamValue | null | undefined>>
+type HrefParams<source extends string> =
+  & Record<RequiredParams<source>, ParamValue>
+  & Partial<Record<OptionalParams<source>, ParamValue | null | undefined>>
+  & Record<string, unknown>
PATCH

echo "Patch applied successfully."
