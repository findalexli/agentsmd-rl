#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'new URLSearchParams(source)' packages/route-pattern/src/lib/route-pattern/parse.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/route-pattern/README.md b/packages/route-pattern/README.md
index b1b497b3ad2..bb01ae9191d 100644
--- a/packages/route-pattern/README.md
+++ b/packages/route-pattern/README.md
@@ -61,11 +61,10 @@ new RoutePattern('docs(/guides/:category)') // multiple segments optional: /docs
 new RoutePattern('api(/v:major(.:minor))') // nested optionals: /api, /api/v2, /api/v2.1
 ```

-**Search params** narrow matches using `?key` or `?key=value`:
+**Search params** narrow matches using `?key`, `?key=`, or `?key=value`. Parsing and serialization follow `URLSearchParams` (`application/x-www-form-urlencoded`): `?key` and `?key=` are the same constraint (stored as an empty `Set` in `ast.search`: key must be present; empty value is OK), and spaces use `+` / `%20` like in real query strings.

 ```ts
-new RoutePattern('search?q') // requires ?q in URL
-new RoutePattern('search?q=') // requires ?q with any value
+new RoutePattern('search?q') // same constraint as ?q= — key must be present
 new RoutePattern('search?q=routing') // requires ?q=routing exactly
 ```

@@ -138,12 +137,11 @@ matcher.match('https://example.com/blog/hello')
 let router = new ArrayMatcher<string>()
 router.add('search', 'no-params')
 router.add('search?q', 'has-q')
-router.add('search?q=', 'has-q-with-value')
 router.add('search?q=hello', 'exact-match')

 router.match('https://example.com/search?q=hello')
 // { pattern: 'search?q=hello', params: {}, data: 'exact-match' }
-// More constrained search params = more specific
+// More constrained search params = more specific (`?q` and `?q=` tie)
 ```

 ## Benchmark
diff --git a/packages/route-pattern/src/lib/route-pattern.ts b/packages/route-pattern/src/lib/route-pattern.ts
index d790b07144f..b89f3ca63de 100644
--- a/packages/route-pattern/src/lib/route-pattern.ts
+++ b/packages/route-pattern/src/lib/route-pattern.ts
@@ -14,17 +14,26 @@ type AST = {
   readonly port: string | null
   readonly pathname: PartPattern
   /**
-   * - `null`: key must be present
-   * - Empty `Set`: key must be present with a value
-   * - Non-empty `Set`: key must be present with all these values
+   * Required values keyed by search param name
+   *
+   * Follows
+   * [WHATWG's application/x-www-form-urlencoded parsing](https://url.spec.whatwg.org/#application/x-www-form-urlencoded) spec
+   * (same as [`URLSearchParams`](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams#percent_encoding)).
+   * For example, `+` is decoded as ` ` (literal space) instead of `%20`.
+   *
+   * - **Empty `Set`**: key must appear; value may be anything (including empty).
+   * - **Non-empty `Set`**: key must appear with all listed values; extra values are OK.
+   *
+   * Examples:
    *
    * ```ts
-   * new Map([['q', null]])                // -> ?q, ?q=, ?q=1
-   * new Map([['q', new Set()]])           // -> ?q=1
-   * new Map([['q', new Set(['x', 'y'])]]) // -> ?q=x&q=y
+   * parseSearch('q')            // -> Map([['q', new Set()]])
+   * parseSearch('q=')           // -> Map([['q', new Set()]])
+   * parseSearch('q=x&q=y')      // -> Map([['q', new Set(['x', 'y'])]])
+   * parseSearch('q&q=&q=x&q=y') // -> Map([['q', new Set(['x', 'y'])]])
    * ```
    */
-  readonly search: ReadonlyMap<string, ReadonlySet<string> | null>
+  readonly search: ReadonlyMap<string, ReadonlySet<string>>
 }

 /**
diff --git a/packages/route-pattern/src/lib/route-pattern/href.ts b/packages/route-pattern/src/lib/route-pattern/href.ts
index 8ba8ab600bd..6016572edfb 100644
--- a/packages/route-pattern/src/lib/route-pattern/href.ts
+++ b/packages/route-pattern/src/lib/route-pattern/href.ts
@@ -68,31 +68,18 @@ export function hrefSearch(pattern: RoutePattern, searchParams: SearchParams): s
     }
   }

-  let missingParams: Array<string> = []
-  for (let [key, constraint] of constraints) {
-    if (constraint === null) {
+  for (let [key, requiredValues] of constraints) {
+    if (requiredValues.size === 0) {
       if (key in searchParams) continue
       urlSearchParams.append(key, '')
-    } else if (constraint.size === 0) {
-      if (key in searchParams) continue
-      missingParams.push(key)
     } else {
-      for (let value of constraint) {
+      for (let value of requiredValues) {
         if (urlSearchParams.getAll(key).includes(value)) continue
         urlSearchParams.append(key, value)
       }
     }
   }

-  if (missingParams.length > 0) {
-    throw new HrefError({
-      type: 'missing-search-params',
-      pattern,
-      missingParams,
-      searchParams: searchParams,
-    })
-  }
-
   let result = urlSearchParams.toString()
   return result || undefined
 }
@@ -109,12 +96,6 @@ type HrefErrorDetails =
       missingParams: Array<string>
       params: Record<string, unknown>
     }
-  | {
-      type: 'missing-search-params'
-      pattern: RoutePattern
-      missingParams: Array<string>
-      searchParams: SearchParams
-    }
   | {
       type: 'nameless-wildcard'
       pattern: RoutePattern
@@ -154,12 +135,6 @@ export class HrefError extends Error {
       return `pattern contains nameless wildcard\n\nPattern: ${pattern}`
     }

-    if (details.type === 'missing-search-params') {
-      let params = details.missingParams.map((p) => `'${p}'`).join(', ')
-      let searchParamsStr = JSON.stringify(details.searchParams)
-      return `missing required search param(s): ${params}\n\nPattern: ${pattern}\nSearch params: ${searchParamsStr}`
-    }
-
     if (details.type === 'missing-params') {
       let params = details.missingParams.map((p) => `'${p}'`).join(', ')
       return `missing param(s): ${params}\n\nPattern: ${pattern}\nParams: ${JSON.stringify(details.params)}`
diff --git a/packages/route-pattern/src/lib/route-pattern/join.ts b/packages/route-pattern/src/lib/route-pattern/join.ts
index ec0a2e347ec..1503832bd9a 100644
--- a/packages/route-pattern/src/lib/route-pattern/join.ts
+++ b/packages/route-pattern/src/lib/route-pattern/join.ts
@@ -100,24 +100,22 @@ type Search = RoutePattern['ast']['search']
  * @returns the merged search constraints
  */
 export function joinSearch(a: Search, b: Search): Search {
-  let result = new Map<string, Set<string> | null>()
+  let result = new Map<string, Set<string>>()

-  for (let [name, constraint] of a) {
-    result.set(name, constraint === null ? null : new Set(constraint))
+  for (let [name, requiredValues] of a) {
+    result.set(name, new Set(requiredValues))
   }

-  for (let [name, constraint] of b) {
+  for (let [name, requiredValues] of b) {
     let current = result.get(name)

-    if (current === null || current === undefined) {
-      result.set(name, constraint === null ? null : new Set(constraint))
+    if (current === undefined) {
+      result.set(name, new Set(requiredValues))
       continue
     }

-    if (constraint !== null) {
-      for (let value of constraint) {
-        current.add(value)
-      }
+    for (let value of requiredValues) {
+      current.add(value)
     }
   }

diff --git a/packages/route-pattern/src/lib/route-pattern/match.ts b/packages/route-pattern/src/lib/route-pattern/match.ts
index 816ec93f09c..f239294b652 100644
--- a/packages/route-pattern/src/lib/route-pattern/match.ts
+++ b/packages/route-pattern/src/lib/route-pattern/match.ts
@@ -11,22 +11,17 @@ export function matchSearch(
   params: URLSearchParams,
   constraints: RoutePattern['ast']['search'],
 ): boolean {
-  for (let [name, constraint] of constraints) {
+  for (let [name, requiredValues] of constraints) {
     let hasParam = params.has(name)
     let values = params.getAll(name)

-    if (constraint === null) {
+    if (requiredValues.size === 0) {
       if (!hasParam) return false
       continue
     }

-    if (constraint.size === 0) {
-      if (values.every((value) => value === '')) return false
-      continue
-    }
-
-    for (let value of constraint) {
-      if (!values.includes(value)) return false
+    for (let requiredValue of requiredValues) {
+      if (!values.includes(requiredValue)) return false
     }
   }
   return true
diff --git a/packages/route-pattern/src/lib/route-pattern/parse.ts b/packages/route-pattern/src/lib/route-pattern/parse.ts
index 77e269064ee..addec23b516 100644
--- a/packages/route-pattern/src/lib/route-pattern/parse.ts
+++ b/packages/route-pattern/src/lib/route-pattern/parse.ts
@@ -28,56 +28,19 @@ function isNamelessWildcard(part: PartPattern): boolean {
   return token.name === '*'
 }

-/**
- * Parse a search string into search constraints.
- *
- * Search constraints define what query params must be present:
- * - `null`: param must be present (e.g., `?q`, `?q=`, `?q=1`)
- * - Empty `Set`: param must be present with a value (e.g., `?q=1`)
- * - Non-empty `Set`: param must be present with all these values (e.g., `?q=x&q=y`)
- *
- * Examples:
- * ```ts
- * parse('q')       // -> Map([['q', null]])
- * parse('q=')      // -> Map([['q', new Set()]])
- * parse('q=x&q=y') // -> Map([['q', new Set(['x', 'y'])]])
- * ```
- *
- * @param source the search string to parse (without leading `?`)
- * @returns the parsed search constraints
- */
 export function parseSearch(source: string): RoutePattern['ast']['search'] {
-  let constraints: Map<string, Set<string> | null> = new Map()
-
-  for (let param of source.split('&')) {
-    if (param === '') continue
-    let equalIndex = param.indexOf('=')
-
-    // `?q`
-    if (equalIndex === -1) {
-      let name = decodeURIComponent(param)
-      if (!constraints.get(name)) {
-        constraints.set(name, null)
-      }
-      continue
+  let constraints = new Map<string, Set<string>>()
+
+  let searchParams = new URLSearchParams(source)
+  for (let [key, value] of searchParams) {
+    let requiredValues = constraints.get(key)
+    if (!requiredValues) {
+      requiredValues = new Set()
+      constraints.set(key, requiredValues)
     }
-
-    let name = decodeURIComponent(param.slice(0, equalIndex))
-    let value = decodeURIComponent(param.slice(equalIndex + 1))
-
-    // `?q=`
-    if (value.length === 0) {
-      if (!constraints.get(name)) {
-        constraints.set(name, new Set())
-      }
-      continue
-    }
-
-    // `?q=1`
-    let constraint = constraints.get(name)
-    constraints.set(name, constraint ? constraint.add(value) : new Set([value]))
+    if (value === '') continue
+    requiredValues.add(value)
   }
-
   return constraints
 }

diff --git a/packages/route-pattern/src/lib/route-pattern/serialize.ts b/packages/route-pattern/src/lib/route-pattern/serialize.ts
index d21ff830a6f..b94d183eb37 100644
--- a/packages/route-pattern/src/lib/route-pattern/serialize.ts
+++ b/packages/route-pattern/src/lib/route-pattern/serialize.ts
@@ -7,24 +7,17 @@ import type { RoutePattern } from '../route-pattern.ts'
  * @returns the query string (without leading `?`), or undefined if empty
  */
 export function serializeSearch(constraints: RoutePattern['ast']['search']): string | undefined {
-  if (constraints.size === 0) {
-    return undefined
-  }
-
-  let parts: Array<string> = []
+  if (constraints.size === 0) return undefined

+  let searchParams = new URLSearchParams()
   for (let [key, constraint] of constraints) {
-    if (constraint === null) {
-      parts.push(encodeURIComponent(key))
-    } else if (constraint.size === 0) {
-      parts.push(`${encodeURIComponent(key)}=`)
+    if (constraint.size === 0) {
+      searchParams.append(key, '')
     } else {
       for (let value of constraint) {
-        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
+        searchParams.append(key, value)
       }
     }
   }
-
-  let result = parts.join('&')
-  return result || undefined
+  return searchParams.toString()
 }
diff --git a/packages/route-pattern/src/lib/specificity.ts b/packages/route-pattern/src/lib/specificity.ts
index c5871bcd1c6..89651bc7629 100644
--- a/packages/route-pattern/src/lib/specificity.ts
+++ b/packages/route-pattern/src/lib/specificity.ts
@@ -168,11 +168,8 @@ function compareSearch(
   let aSpecificity = searchSpecificity(a)
   let bSpecificity = searchSpecificity(b)

-  if (aSpecificity.keyAndExactValue > bSpecificity.keyAndExactValue) return 1
-  if (aSpecificity.keyAndExactValue < bSpecificity.keyAndExactValue) return -1
-
-  if (aSpecificity.keyAndAnyValue > bSpecificity.keyAndAnyValue) return 1
-  if (aSpecificity.keyAndAnyValue < bSpecificity.keyAndAnyValue) return -1
+  if (aSpecificity.keyValue > bSpecificity.keyValue) return 1
+  if (aSpecificity.keyValue < bSpecificity.keyValue) return -1

   if (aSpecificity.key > bSpecificity.key) return 1
   if (aSpecificity.key < bSpecificity.key) return -1
@@ -181,25 +178,18 @@ function compareSearch(
 }

 function searchSpecificity(constraints: RoutePattern['ast']['search']): {
-  keyAndExactValue: number
-  keyAndAnyValue: number
   key: number
+  keyValue: number
 } {
-  let exactValue = 0
-  let anyValue = 0
-  let key = 0
+  let specificity = { key: 0, keyValue: 0 }

   for (let constraint of constraints.values()) {
-    if (constraint === null) {
-      key += 1
-      continue
-    }
     if (constraint.size === 0) {
-      anyValue += 1
+      specificity.key += 1
       continue
     }
-    exactValue += constraint.size
+    specificity.keyValue += constraint.size
   }

-  return { keyAndExactValue: exactValue, keyAndAnyValue: anyValue, key }
+  return specificity
 }

PATCH

echo "Patch applied successfully."
