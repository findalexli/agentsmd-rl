#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Organize by feature' packages/route-pattern/src/lib/route-pattern/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/route-pattern/src/index.ts b/packages/route-pattern/src/index.ts
index e3e485057ca..594cd5c8be9 100644
--- a/packages/route-pattern/src/index.ts
+++ b/packages/route-pattern/src/index.ts
@@ -5,7 +5,7 @@ export {
 } from './lib/route-pattern.ts'
 export type { Join, Params } from './lib/types/index.ts'
 export { ParseError } from './lib/route-pattern/parse.ts'
-export { type Args as HrefArgs, HrefError } from './lib/route-pattern/href.ts'
+export { type HrefArgs, HrefError } from './lib/route-pattern/href.ts'

 export { type Matcher, type Match } from './lib/matcher.ts'
 export { ArrayMatcher } from './lib/array-matcher.ts'
diff --git a/packages/route-pattern/src/lib/route-pattern.test.ts b/packages/route-pattern/src/lib/route-pattern.test.ts
index b474971c74c..95ed00d674d 100644
--- a/packages/route-pattern/src/lib/route-pattern.test.ts
+++ b/packages/route-pattern/src/lib/route-pattern.test.ts
@@ -2,8 +2,7 @@ import * as assert from 'node:assert/strict'
 import { describe, it } from 'node:test'

 import { RoutePattern } from './route-pattern.ts'
-import * as Href from './route-pattern/href.ts'
-import * as Source from './route-pattern/source.ts'
+import { HrefError } from './route-pattern/href.ts'

 describe('RoutePattern', () => {
   describe('parse', () => {
@@ -24,15 +23,15 @@ describe('RoutePattern', () => {
       assert.deepEqual(
         {
           protocol: pattern.ast.protocol,
-          hostname: pattern.ast.hostname ? Source.part(pattern.ast.hostname) : undefined,
-          port: pattern.ast.port ?? null,
-          pathname: pattern.ast.pathname ? Source.part(pattern.ast.pathname) : null,
+          hostname: pattern.ast.hostname?.source ?? null,
+          port: pattern.ast.port,
+          pathname: pattern.ast.pathname.source,
           search: pattern.ast.search,
         },
         {
           // explicitly set each prop so that we can omitted keys from `expected` to set them as defaults
           protocol: expected.protocol ?? null,
-          hostname: expected.hostname,
+          hostname: expected.hostname ?? null,
           port: expected.port ?? null,
           pathname: expected.pathname ?? '',
           search: expectedSearch,
@@ -391,8 +390,8 @@ describe('RoutePattern', () => {
   })

   describe('href', () => {
-    function hrefError(type: Href.HrefError['details']['type']) {
-      return (error: unknown) => error instanceof Href.HrefError && error.details.type === type
+    function hrefError(type: HrefError['details']['type']) {
+      return (error: unknown) => error instanceof HrefError && error.details.type === type
     }

     describe('protocol', () => {
diff --git a/packages/route-pattern/src/lib/route-pattern.ts b/packages/route-pattern/src/lib/route-pattern.ts
index cfc68928fbf..1146dffc10f 100644
--- a/packages/route-pattern/src/lib/route-pattern.ts
+++ b/packages/route-pattern/src/lib/route-pattern.ts
@@ -1,18 +1,29 @@
 import { split } from './route-pattern/split.ts'
-import * as Search from './route-pattern/search.ts'
 import { PartPattern, type PartPatternMatch } from './route-pattern/part-pattern.ts'
-import type { Join as JoinResult, Params } from './types/index.ts'
-import * as Parse from './route-pattern/parse.ts'
-import * as Source from './route-pattern/source.ts'
-import * as Href from './route-pattern/href.ts'
-import * as Join from './route-pattern/join.ts'
+import type { Join, Params } from './types/index.ts'
+import { parseHostname, parseProtocol, parseSearch } from './route-pattern/parse.ts'
+import { serializeSearch } from './route-pattern/serialize.ts'
+import { joinPathname, joinSearch } from './route-pattern/join.ts'
+import { HrefError, hrefSearch, type HrefArgs } from './route-pattern/href.ts'
+import { matchSearch } from './route-pattern/match.ts'

 type AST = {
   protocol: 'http' | 'https' | 'http(s)' | null
   hostname: PartPattern | null
   port: string | null
   pathname: PartPattern
-  search: Search.Constraints
+  /**
+   * - `null`: key must be present
+   * - Empty `Set`: key must be present with a value
+   * - Non-empty `Set`: key must be present with all these values
+   *
+   * ```ts
+   * new Map([['q', null]])                // -> ?q, ?q=, ?q=1
+   * new Map([['q', new Set()]])           // -> ?q=1
+   * new Map([['q', new Set(['x', 'y'])]]) // -> ?q=x&q=y
+   * ```
+   */
+  search: Map<string, Set<string> | null>
 }

 export type RoutePatternOptions = {
@@ -43,13 +54,13 @@ export class RoutePattern<source extends string = string> {
     let spans = split(source)

     this.ast = {
-      protocol: Parse.protocol(source, spans.protocol),
-      hostname: Parse.hostname(source, spans.hostname),
+      protocol: parseProtocol(source, spans.protocol),
+      hostname: parseHostname(source, spans.hostname),
       port: spans.port ? source.slice(...spans.port) : null,
       pathname: spans.pathname
         ? PartPattern.parse(source, { span: spans.pathname, type: 'pathname', ignoreCase })
         : PartPattern.parse('', { span: [0, 0], type: 'pathname', ignoreCase }),
-      search: spans.search ? Parse.search(source.slice(...spans.search)) : new Map(),
+      search: spans.search ? parseSearch(source.slice(...spans.search)) : new Map(),
     }

     this.ignoreCase = ignoreCase
@@ -65,8 +76,7 @@ export class RoutePattern<source extends string = string> {
   }

   get hostname(): string {
-    if (this.ast.hostname === null) return ''
-    return Source.part(this.ast.hostname)
+    return this.ast.hostname?.source ?? ''
   }

   get port(): string {
@@ -74,11 +84,11 @@ export class RoutePattern<source extends string = string> {
   }

   get pathname(): string {
-    return Source.part(this.ast.pathname)
+    return this.ast.pathname.source
   }

   get search(): string {
-    return Source.search(this.ast.search) ?? ''
+    return serializeSearch(this.ast.search) ?? ''
   }

   get source(): string {
@@ -106,7 +116,7 @@ export class RoutePattern<source extends string = string> {
   join<other extends string>(
     other: other | RoutePattern<other>,
     options?: RoutePatternOptions,
-  ): RoutePattern<JoinResult<source, other>> {
+  ): RoutePattern<Join<source, other>> {
     other = typeof other === 'string' ? new RoutePattern(other, options) : other
     let ignoreCase = options?.ignoreCase ?? (this.ignoreCase || other.ignoreCase)

@@ -117,8 +127,8 @@ export class RoutePattern<source extends string = string> {
           protocol: other.ast.protocol ?? this.ast.protocol,
           hostname: other.ast.hostname ?? this.ast.hostname,
           port: other.ast.port ?? this.ast.port,
-          pathname: Join.pathname(this.ast.pathname, other.ast.pathname, ignoreCase),
-          search: Join.search(this.ast.search, other.ast.search),
+          pathname: joinPathname(this.ast.pathname, other.ast.pathname, ignoreCase),
+          search: joinSearch(this.ast.search, other.ast.search),
         },
       },
       ignoreCase: {
@@ -128,7 +138,7 @@ export class RoutePattern<source extends string = string> {
     })
   }

-  href(...args: Href.Args<source>): string {
+  href(...args: HrefArgs<source>): string {
     let [params, searchParams] = args
     params ??= {}
     searchParams ??= {}
@@ -142,12 +152,12 @@ export class RoutePattern<source extends string = string> {

       // hostname
       if (this.ast.hostname === null) {
-        throw new Href.HrefError({
+        throw new HrefError({
           type: 'missing-hostname',
           pattern: this,
         })
       }
-      let hostname = Href.part(this, this.ast.hostname, params)
+      let hostname = this.ast.hostname.href(this, params)

       // port
       let port = this.ast.port === null ? '' : `:${this.ast.port}`
@@ -155,11 +165,11 @@ export class RoutePattern<source extends string = string> {
     }

     // pathname
-    let pathname = Href.part(this, this.ast.pathname, params)
+    let pathname = this.ast.pathname.href(this, params)
     result += '/' + pathname

     // search
-    let search = Href.search(this, searchParams)
+    let search = hrefSearch(this, searchParams)
     if (search) result += `?${search}`

     return result
@@ -194,7 +204,7 @@ export class RoutePattern<source extends string = string> {
     let pathname = this.ast.pathname.match(url.pathname.slice(1))
     if (pathname === null) return null

-    if (!Search.test(url.searchParams, this.ast.search, this.ignoreCase)) return null
+    if (!matchSearch(url.searchParams, this.ast.search, this.ignoreCase)) return null

     let params: Record<string, string | undefined> = {}

diff --git a/packages/route-pattern/src/lib/route-pattern/AGENTS.md b/packages/route-pattern/src/lib/route-pattern/AGENTS.md
new file mode 100644
index 00000000000..caf0a824dc8
--- /dev/null
+++ b/packages/route-pattern/src/lib/route-pattern/AGENTS.md
@@ -0,0 +1,14 @@
+# Route Pattern Helpers
+
+This directory contains helpers for [`route-pattern.ts`](../route-pattern.ts).
+
+## Organization
+
+- **[`part-pattern.ts`](./part-pattern.ts)**: Logic that applies to any `PartPattern` (i.e. hostname _and_ pathname)
+- **Other files**: Organize by feature (not by pattern part)
+  - [`href.ts`](./href.ts): Href generation
+  - [`join.ts`](./join.ts): Pattern joining
+  - [`match.ts`](./match.ts): URL matching
+  - [`parse.ts`](./parse.ts): Parsing patterns
+  - [`serialize.ts`](./serialize.ts): Serializing to strings
+  - [`split.ts`](./split.ts): Splitting source strings
diff --git a/packages/route-pattern/src/lib/route-pattern/href.ts b/packages/route-pattern/src/lib/route-pattern/href.ts
index d1045008c46..9117fd6a3de 100644
--- a/packages/route-pattern/src/lib/route-pattern/href.ts
+++ b/packages/route-pattern/src/lib/route-pattern/href.ts
@@ -3,93 +3,22 @@ import type { RoutePattern } from '../route-pattern.ts'
 import type { OptionalParams, RequiredParams } from '../types/params.ts'
 import type { PartPattern } from './part-pattern.ts'

-type ParamValue = string | number
-type Params = Record<string, ParamValue>
+type HrefParamValue = string | number
+export type HrefParams = Record<string, HrefParamValue>

 // prettier-ignore
-export type Args<source extends string> =
+export type HrefArgs<source extends string> =
   [RequiredParams<source>] extends [never] ?
-    [] | [null | undefined | Record<string, any>] | [null | undefined | Record<string, any>, SearchParams] :
-    [ParamsArg<source>, SearchParams] | [ParamsArg<source>]
+    [] | [null | undefined | Record<string, any>] | [null | undefined | Record<string, any>, HrefSearchParams] :
+    [HrefParamsArg<source>, HrefSearchParams] | [HrefParamsArg<source>]

 // prettier-ignore
-type ParamsArg<source extends string> =
-  & Record<RequiredParams<source>, ParamValue>
-  & Partial<Record<OptionalParams<source>, ParamValue | null | undefined>>
+type HrefParamsArg<source extends string> =
+  & Record<RequiredParams<source>, HrefParamValue>
+  & Partial<Record<OptionalParams<source>, HrefParamValue | null | undefined>>
   & Record<string, unknown>

-/**
- * Generate a partial href from a part pattern and params.
- *
- * @param pattern The route pattern containing the part pattern.
- * @param partPattern The part pattern to generate an href for.
- * @param params The parameters to substitute into the pattern.
- * @returns The href (URL) for the given params, or null if no variant matches.
- */
-export function part(pattern: RoutePattern, partPattern: PartPattern, params: Params): string {
-  let missingParams: Array<string> = []
-
-  let stack: Array<{ begin?: number; href: string }> = [{ href: '' }]
-  let i = 0
-  while (i < partPattern.tokens.length) {
-    let token = partPattern.tokens[i]
-    if (token.type === 'text') {
-      stack[stack.length - 1].href += token.text
-      i += 1
-      continue
-    }
-    if (token.type === 'separator') {
-      stack[stack.length - 1].href += partPattern.separator
-      i += 1
-      continue
-    }
-    if (token.type === '(') {
-      stack.push({ begin: i, href: '' })
-      i += 1
-      continue
-    }
-    if (token.type === ')') {
-      let frame = stack.pop()!
-      stack[stack.length - 1].href += frame.href
-      i += 1
-      continue
-    }
-    if (token.type === ':' || token.type === '*') {
-      let value = params[token.name]
-      if (value === undefined) {
-        if (stack.length <= 1) {
-          if (token.name === '*') {
-            throw new HrefError({
-              type: 'nameless-wildcard',
-              pattern,
-            })
-          }
-          missingParams.push(token.name)
-        }
-        let frame = stack.pop()!
-        i = partPattern.optionals.get(frame.begin!)! + 1
-        continue
-      }
-      stack[stack.length - 1].href += typeof value === 'string' ? value : String(value)
-      i += 1
-      continue
-    }
-    unreachable(token.type)
-  }
-  if (missingParams.length > 0) {
-    throw new HrefError({
-      type: 'missing-params',
-      pattern,
-      partPattern,
-      missingParams,
-      params,
-    })
-  }
-  if (stack.length !== 1) unreachable()
-  return stack[0].href
-}
-
-export type SearchParams = Record<
+export type HrefSearchParams = Record<
   string,
   string | number | null | undefined | Array<string | number | null | undefined>
 >
@@ -101,7 +30,10 @@ export type SearchParams = Record<
  * @param searchParams the search params to include in the href
  * @returns the query string (without leading `?`), or undefined if empty
  */
-export function search(pattern: RoutePattern, searchParams: SearchParams): string | undefined {
+export function hrefSearch(
+  pattern: RoutePattern,
+  searchParams: HrefSearchParams,
+): string | undefined {
   let constraints = pattern.ast.search
   if (constraints.size === 0 && Object.keys(searchParams).length === 0) {
     return undefined
@@ -166,7 +98,7 @@ type HrefErrorDetails =
       type: 'missing-search-params'
       pattern: RoutePattern
       missingParams: Array<string>
-      searchParams: SearchParams
+      searchParams: HrefSearchParams
     }
   | {
       type: 'nameless-wildcard'
diff --git a/packages/route-pattern/src/lib/route-pattern/join.ts b/packages/route-pattern/src/lib/route-pattern/join.ts
index 83c8bd913f1..23f2518d617 100644
--- a/packages/route-pattern/src/lib/route-pattern/join.ts
+++ b/packages/route-pattern/src/lib/route-pattern/join.ts
@@ -31,7 +31,7 @@ type Pathname = RoutePattern['ast']['pathname']
  * @param ignoreCase whether to ignore case when matching
  * @returns the joined pathname pattern
  */
-export function pathname(a: Pathname, b: Pathname, ignoreCase: boolean): Pathname {
+export function joinPathname(a: Pathname, b: Pathname, ignoreCase: boolean): Pathname {
   if (a.tokens.length === 0) return b
   if (b.tokens.length === 0) return a

@@ -100,7 +100,7 @@ type Search = RoutePattern['ast']['search']
  * @param b the second search constraints
  * @returns the merged search constraints
  */
-export function search(a: Search, b: Search): Search {
+export function joinSearch(a: Search, b: Search): Search {
   let result: Search = new Map()

   for (let [name, constraint] of a) {
diff --git a/packages/route-pattern/src/lib/route-pattern/search.ts b/packages/route-pattern/src/lib/route-pattern/match.ts
similarity index 75%
rename from packages/route-pattern/src/lib/route-pattern/search.ts
rename to packages/route-pattern/src/lib/route-pattern/match.ts
index ffe620e0e7b..7d06245a53e 100644
--- a/packages/route-pattern/src/lib/route-pattern/search.ts
+++ b/packages/route-pattern/src/lib/route-pattern/match.ts
@@ -1,15 +1,4 @@
-/**
- * - `null`: key must be present
- * - Empty `Set`: key must be present with a value
- * - Non-empty `Set`: key must be present with all these values
- *
- * ```ts
- * new Map([['q', null]])                // -> ?q, ?q=, ?q=1
- * new Map([['q', new Set()]])           // -> ?q=1
- * new Map([['q', new Set(['x', 'y'])]]) // -> ?q=x&q=y
- * ```
- */
-export type Constraints = Map<string, Set<string> | null>
+import type { RoutePattern } from '../route-pattern'

 /**
  * Test if URL search params satisfy the given constraints.
@@ -19,9 +8,9 @@ export type Constraints = Map<string, Set<string> | null>
  * @param ignoreCase whether to ignore case when matching param names and values
  * @returns true if the params satisfy all constraints
  */
-export function test(
+export function matchSearch(
   params: URLSearchParams,
-  constraints: Constraints,
+  constraints: RoutePattern['ast']['search'],
   ignoreCase: boolean,
 ): boolean {
   for (let [name, constraint] of constraints) {
diff --git a/packages/route-pattern/src/lib/route-pattern/parse.ts b/packages/route-pattern/src/lib/route-pattern/parse.ts
index 73d76c91266..8b32c73ee61 100644
--- a/packages/route-pattern/src/lib/route-pattern/parse.ts
+++ b/packages/route-pattern/src/lib/route-pattern/parse.ts
@@ -2,7 +2,7 @@ import { PartPattern } from './part-pattern.ts'
 import type { Span } from './split.ts'
 import type { RoutePattern } from '../route-pattern.ts'

-export function protocol(source: string, span: Span | null): RoutePattern['ast']['protocol'] {
+export function parseProtocol(source: string, span: Span | null): RoutePattern['ast']['protocol'] {
   if (!span) return null
   let protocol = source.slice(...span)
   if (protocol === '' || protocol === 'http' || protocol === 'https' || protocol === 'http(s)') {
@@ -11,7 +11,7 @@ export function protocol(source: string, span: Span | null): RoutePattern['ast']
   throw new ParseError('invalid protocol', source, span[0])
 }

-export function hostname(
+export function parseHostname(
   source: string,
   span: Span | null,
 ): RoutePattern['ast']['hostname'] | null {
@@ -50,7 +50,7 @@ function isNamelessWildcard(part: PartPattern): boolean {
  * @param source the search string to parse (without leading `?`)
  * @returns the parsed search constraints
  */
-export function search(source: string): RoutePattern['ast']['search'] {
+export function parseSearch(source: string): RoutePattern['ast']['search'] {
   let constraints: RoutePattern['ast']['search'] = new Map()

   for (let param of source.split('&')) {
diff --git a/packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts b/packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts
index 9797eb25739..69fae400d95 100644
--- a/packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts
+++ b/packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts
@@ -3,7 +3,6 @@ import { describe, it } from 'node:test'

 import { ParseError } from './parse.ts'
 import { PartPattern } from './part-pattern.ts'
-import * as Source from './source.ts'

 describe('PartPattern', () => {
   describe('parse', () => {
@@ -193,7 +192,7 @@ describe('PartPattern', () => {
   describe('source', () => {
     function assertSource(expected: string) {
       let partPattern = PartPattern.parse(expected, { type: 'pathname', ignoreCase: false })
-      assert.equal(Source.part(partPattern), expected)
+      assert.equal(partPattern.source, expected)
     }

     it('returns source representation of pattern', () => {
diff --git a/packages/route-pattern/src/lib/route-pattern/part-pattern.ts b/packages/route-pattern/src/lib/route-pattern/part-pattern.ts
index c1f6be465a6..ac990e04299 100644
--- a/packages/route-pattern/src/lib/route-pattern/part-pattern.ts
+++ b/packages/route-pattern/src/lib/route-pattern/part-pattern.ts
@@ -2,6 +2,8 @@ import { ParseError } from './parse.ts'
 import { unreachable } from '../unreachable.ts'
 import * as RE from '../regexp.ts'
 import type { Span } from './split.ts'
+import { HrefError, type HrefParams } from './href.ts'
+import type { RoutePattern } from '../route-pattern.ts'

 type MatchParam = {
   type: ':' | '*'
@@ -26,6 +28,7 @@ export class PartPattern {
   readonly type: 'hostname' | 'pathname'
   readonly ignoreCase: boolean

+  // todo: params cache
   #regexp: RegExp | undefined

   constructor(
@@ -151,9 +154,109 @@ export class PartPattern {
     )
   }

+  get source(): string {
+    let result = ''
+    for (let token of this.tokens) {
+      if (token.type === '(' || token.type === ')') {
+        result += token.type
+        continue
+      }
+
+      if (token.type === 'text') {
+        result += token.text
+        continue
+      }
+
+      if (token.type === ':' || token.type === '*') {
+        let name = token.name === '*' ? '' : token.name
+        result += `${token.type}${name}`
+        continue
+      }
+
+      if (token.type === 'separator') {
+        result += this.separator
+        continue
+      }
+
+      unreachable(token.type)
+    }
+
+    return result
+  }
+
+  /**
+   * Generate a partial href from a part pattern and params.
+   *
+   * @param pattern The route pattern containing the part pattern.
+   * @param params The parameters to substitute into the pattern.
+   * @returns The partial href for the given params
+   */
+  href(pattern: RoutePattern, params: HrefParams): string {
+    let missingParams: Array<string> = []
+
+    let stack: Array<{ begin?: number; href: string }> = [{ href: '' }]
+    let i = 0
+    while (i < this.tokens.length) {
+      let token = this.tokens[i]
+      if (token.type === 'text') {
+        stack[stack.length - 1].href += token.text
+        i += 1
+        continue
+      }
+      if (token.type === 'separator') {
+        stack[stack.length - 1].href += this.separator
+        i += 1
+        continue
+      }
+      if (token.type === '(') {
+        stack.push({ begin: i, href: '' })
+        i += 1
+        continue
+      }
+      if (token.type === ')') {
+        let frame = stack.pop()!
+        stack[stack.length - 1].href += frame.href
+        i += 1
+        continue
+      }
+      if (token.type === ':' || token.type === '*') {
+        let value = params[token.name]
+        if (value === undefined) {
+          if (stack.length <= 1) {
+            if (token.name === '*') {
+              throw new HrefError({
+                type: 'nameless-wildcard',
+                pattern,
+              })
+            }
+            missingParams.push(token.name)
+          }
+          let frame = stack.pop()!
+          i = this.optionals.get(frame.begin!)! + 1
+          continue
+        }
+        stack[stack.length - 1].href += typeof value === 'string' ? value : String(value)
+        i += 1
+        continue
+      }
+      unreachable(token.type)
+    }
+    if (missingParams.length > 0) {
+      throw new HrefError({
+        type: 'missing-params',
+        pattern,
+        partPattern: this,
+        missingParams,
+        params,
+      })
+    }
+    if (stack.length !== 1) unreachable()
+    return stack[0].href
+  }
+
   match(part: string): PartPatternMatch | null {
     if (this.#regexp === undefined) {
-      this.#regexp = toRegExp(this.tokens, this.separator, this.ignoreCase)
+      this.#regexp = this.#toRegExp()
     }
     let reMatch = this.#regexp.exec(part)
     if (reMatch === null) return null
@@ -174,48 +277,44 @@ export class PartPattern {
     }
     return match
   }
-}
-
-function toRegExp(
-  tokens: Array<PartPatternToken>,
-  separator: '.' | '/',
-  ignoreCase: boolean,
-): RegExp {
-  let result = ''
-  for (let token of tokens) {
-    if (token.type === 'text') {
-      result += RE.escape(token.text)
-      continue
-    }
+  #toRegExp(): RegExp {
+    let result = ''
+    for (let token of this.tokens) {
+      if (token.type === 'text') {
+        result += RE.escape(token.text)
+        continue
+      }

-    if (token.type === ':') {
-      result += separator ? `([^${separator}]+?)` : `(.+?)`
-      continue
-    }
+      if (token.type === ':') {
+        result += this.separator ? `([^${this.separator}]+?)` : `(.+?)`
+        continue
+      }

-    if (token.type === '*') {
-      result += `(.*)`
-      continue
-    }
+      if (token.type === '*') {
+        result += `(.*)`
+        continue
+      }

-    if (token.type === '(') {
-      result += '(?:'
-      continue
-    }
+      if (token.type === '(') {
+        result += '(?:'
+        continue
+      }

-    if (token.type === ')') {
-      result += ')?'
-      continue
-    }
+      if (token.type === ')') {
+        result += ')?'
+        continue
+      }

-    if (token.type === 'separator') {
-      result += RE.escape(separator ?? '')
-      continue
-    }
+      if (token.type === 'separator') {
+        result += RE.escape(this.separator ?? '')
+        continue
+      }

-    unreachable(token.type)
+      unreachable(token.type)
+    }
+    return new RegExp(`^${result}$`, this.ignoreCase ? 'di' : 'd')
   }
-  return new RegExp(`^${result}$`, ignoreCase ? 'di' : 'd')
 }

 function separatorForType(type: 'hostname' | 'pathname'): '.' | '/' {
diff --git a/packages/route-pattern/src/lib/route-pattern/serialize.ts b/packages/route-pattern/src/lib/route-pattern/serialize.ts
new file mode 100644
index 00000000000..d21ff830a6f
--- /dev/null
+++ b/packages/route-pattern/src/lib/route-pattern/serialize.ts
@@ -0,0 +1,30 @@
+import type { RoutePattern } from '../route-pattern.ts'
+
+/**
+ * Serialize search constraints to a query string.
+ *
+ * @param constraints the search constraints to convert
+ * @returns the query string (without leading `?`), or undefined if empty
+ */
+export function serializeSearch(constraints: RoutePattern['ast']['search']): string | undefined {
+  if (constraints.size === 0) {
+    return undefined
+  }
+
+  let parts: Array<string> = []
+
+  for (let [key, constraint] of constraints) {
+    if (constraint === null) {
+      parts.push(encodeURIComponent(key))
+    } else if (constraint.size === 0) {
+      parts.push(`${encodeURIComponent(key)}=`)
+    } else {
+      for (let value of constraint) {
+        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
+      }
+    }
+  }
+
+  let result = parts.join('&')
+  return result || undefined
+}
diff --git a/packages/route-pattern/src/lib/route-pattern/source.ts b/packages/route-pattern/src/lib/route-pattern/source.ts
deleted file mode 100644
index 13e93b29d1f..00000000000
--- a/packages/route-pattern/src/lib/route-pattern/source.ts
+++ /dev/null
@@ -1,63 +0,0 @@
-import type { RoutePattern } from '../route-pattern.ts'
-import { unreachable } from '../unreachable.ts'
-import type { PartPattern } from './part-pattern.ts'
-
-export function part(partPattern: PartPattern): string {
-  let result = ''
-
-  for (let token of partPattern.tokens) {
-    if (token.type === '(' || token.type === ')') {
-      result += token.type
-      continue
-    }
-
-    if (token.type === 'text') {
-      result += token.text
-      continue
-    }
-
-    if (token.type === ':' || token.type === '*') {
-      let name = token.name === '*' ? '' : token.name
-      result += `${token.type}${name}`
-      continue
-    }
-
-    if (token.type === 'separator') {
-      result += partPattern.separator
-      continue
-    }
-
-    unreachable(token.type)
-  }
-
-  return result
-}
-
-/**
- * Convert search constraints to a query string.
- *
- * @param constraints the search constraints to convert
- * @returns the query string (without leading `?`), or undefined if empty
- */
-export function search(constraints: RoutePattern['ast']['search']): string | undefined {
-  if (constraints.size === 0) {
-    return undefined
-  }
-
-  let parts: Array<string> = []
-
-  for (let [key, constraint] of constraints) {
-    if (constraint === null) {
-      parts.push(encodeURIComponent(key))
-    } else if (constraint.size === 0) {
-      parts.push(`${encodeURIComponent(key)}=`)
-    } else {
-      for (let value of constraint) {
-        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
-      }
-    }
-  }
-
-  let result = parts.join('&')
-  return result || undefined
-}
diff --git a/packages/route-pattern/src/lib/trie-matcher.ts b/packages/route-pattern/src/lib/trie-matcher.ts
index cf803edeec4..ea6647fd6d2 100644
--- a/packages/route-pattern/src/lib/trie-matcher.ts
+++ b/packages/route-pattern/src/lib/trie-matcher.ts
@@ -6,9 +6,9 @@ import type {
 import { RoutePattern } from './route-pattern.ts'
 import * as Variant from './trie-matcher/variant.ts'
 import { unreachable } from './unreachable.ts'
-import * as Search from './route-pattern/search.ts'
 import type { Match, Matcher } from './matcher.ts'
 import * as Specificity from './specificity.ts'
+import { matchSearch } from './route-pattern/match.ts'

 type Param = Extract<PartPatternToken, { type: ':' | '*' }>

@@ -258,7 +258,7 @@ export class Trie<data = unknown> {
           let { value } = current.pathnameNode
           if (
             value &&
-            Search.test(url.searchParams, value.pattern.ast.search, value.pattern.ignoreCase)
+            matchSearch(url.searchParams, value.pattern.ast.search, value.pattern.ignoreCase)
           ) {
             let pathnameMatch: PartPatternMatch = []
             for (let i = 0; i < value.requiredParams.length; i++) {

PATCH

echo "Patch applied successfully."
