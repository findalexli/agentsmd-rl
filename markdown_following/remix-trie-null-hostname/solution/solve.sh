#!/bin/bash
set -euo pipefail
cd /workspace/remix

if grep -q "anyHostname = hostNameNode.any.get" packages/route-pattern/src/lib/matchers/trie.ts; then
  exit 0
fi

git apply --verbose <<'PATCH'
diff --git a/packages/route-pattern/bench/comparison.bench.ts b/packages/route-pattern/bench/comparison.bench.ts
index a8c080b8345..b6aee2f2777 100644
--- a/packages/route-pattern/bench/comparison.bench.ts
+++ b/packages/route-pattern/bench/comparison.bench.ts
@@ -12,6 +12,7 @@ import FindMyWay from 'find-my-way'
 import { match } from 'path-to-regexp'

 import { ArrayMatcher } from '../src'
+import { TrieMatcher } from '../src/lib/matchers/trie.ts'

 type Syntax = 'route-pattern' | 'find-my-way' | 'path-to-regexp'

@@ -30,6 +31,11 @@ const matchers: Array<{
     syntax: 'route-pattern',
     createMatcher: () => new ArrayMatcher(),
   },
+  {
+    name: 'route-pattern/trie',
+    syntax: 'route-pattern',
+    createMatcher: () => new TrieMatcher(),
+  },
   {
     /** https://github.com/delvedor/find-my-way */
     name: 'find-my-way',
diff --git a/packages/route-pattern/src/lib/matchers/trie.test.ts b/packages/route-pattern/src/lib/matchers/trie.test.ts
index 5a8083b107e..483815d3235 100644
--- a/packages/route-pattern/src/lib/matchers/trie.test.ts
+++ b/packages/route-pattern/src/lib/matchers/trie.test.ts
@@ -5,6 +5,59 @@ import { TrieMatcher } from './trie.ts'

 describe('TrieMatcher', () => {
   describe('match', () => {
+    describe('pathname-only patterns', () => {
+      it('matches static pathname pattern', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('users', null)
+
+        let match = matcher.match('https://example.com/users')
+        assert.ok(match)
+        assert.deepEqual(match.params, {})
+        assert.equal(match.url.pathname, '/users')
+      })
+
+      it('matches nested static pathname pattern', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('api/v1/users', null)
+
+        let match = matcher.match('https://example.com/api/v1/users')
+        assert.ok(match)
+        assert.deepEqual(match.params, {})
+      })
+
+      it('matches pathname pattern with variable', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('users/:id', null)
+
+        let match = matcher.match('https://example.com/users/123')
+        assert.ok(match)
+        assert.deepEqual(match.params, { id: '123' })
+      })
+
+      it('matches pathname pattern with wildcard', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('files/*path', null)
+
+        let match = matcher.match('https://example.com/files/docs/readme.txt')
+        assert.ok(match)
+        assert.deepEqual(match.params, { path: 'docs/readme.txt' })
+      })
+
+      it('matches across different hostnames', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('api/users', null)
+
+        let match1 = matcher.match('https://example.com/api/users')
+        assert.ok(match1)
+
+        let match2 = matcher.match('https://other.com/api/users')
+        assert.ok(match2)
+
+        let match3 = matcher.match('http://localhost/api/users')
+        assert.ok(match3)
+      })
+    })
+
     describe('static patterns', () => {
       it('matches exact static pattern with full URL', () => {
         let matcher = new TrieMatcher<null>()
@@ -24,6 +77,14 @@ describe('TrieMatcher', () => {
         assert.ok(match)
         assert.deepEqual(match.params, {})
       })
+
+      it('does not match different hostname', () => {
+        let matcher = new TrieMatcher<null>()
+        matcher.add('://example.com/users', null)
+
+        let match = matcher.match('https://other.com/users')
+        assert.equal(match, null)
+      })
     })

     describe('variable patterns', () => {
diff --git a/packages/route-pattern/src/lib/matchers/trie.ts b/packages/route-pattern/src/lib/matchers/trie.ts
index efb11a6c8ae..b72a2245454 100644
--- a/packages/route-pattern/src/lib/matchers/trie.ts
+++ b/packages/route-pattern/src/lib/matchers/trie.ts
@@ -22,7 +22,7 @@ export class TrieMatcher<data = unknown> implements Matcher<data> {
   match(url: string | URL, compareFn = Specificity.descending): Matcher.Match<string, data> | null {
     url = typeof url === 'string' ? new URL(url) : url
     let matches = this.matchAll(url, compareFn)
-    return matches[0]
+    return matches[0] ?? null
   }

   matchAll(
@@ -56,7 +56,10 @@ export class TrieMatcher<data = unknown> implements Matcher<data> {

 type RoutePatternVariant = {
   protocol: 'http' | 'https'
-  hostname: { type: 'static'; value: string } | { type: 'dynamic'; value: PartPattern }
+  hostname:
+    | { type: 'static'; value: string }
+    | { type: 'dynamic'; value: PartPattern }
+    | { type: 'any' }
   port: string
   pathname: Variant
 }
@@ -70,7 +73,7 @@ function variants(pattern: RoutePattern): Array<RoutePatternVariant> {

   // prettier-ignore
   let hostnames =
-    pattern.ast.hostname === null ? [] :
+    pattern.ast.hostname === null ? [{ type: 'any' as const }] :
     pattern.ast.hostname.paramNames.length === 0 ?
       pattern.ast.hostname.variants.map((variant) => ({ type: 'static' as const, value: variant.toString() })) :
       [{ type: 'dynamic' as const, value: pattern.ast.hostname }]
@@ -97,12 +100,14 @@ type ProtocolNode<data> = {
 type HostnameNode<data> = {
   static: Map<string, PortNode<data>>
   dynamic: Array<{ part: PartPattern; portNode: PortNode<data> }>
+  any: PortNode<data>
 }

 function createHostnameNode<data>(): HostnameNode<data> {
   return {
     static: new Map(),
     dynamic: [],
+    any: new Map(),
   }
 }

@@ -154,7 +159,9 @@ export class Trie<data = unknown> {

       // hostname -> port
       let portNode: PortNode<data> | undefined = undefined
-      if (variant.hostname.type === 'static') {
+      if (variant.hostname.type === 'any') {
+        portNode = hostnameNode.any
+      } else if (variant.hostname.type === 'static') {
         portNode = hostnameNode.static.get(variant.hostname.value)
         if (portNode === undefined) {
           portNode = new Map()
@@ -230,6 +237,17 @@ export class Trie<data = unknown> {
     if (protocol !== 'http' && protocol !== 'https') return []
     let hostNameNode = this.protocolNode[protocol]

+    // any hostname + port -> pathname
+    let anyHostname = hostNameNode.any.get(url.port)
+    if (anyHostname) {
+      origins.push({
+        hostnameMatch: [
+          { type: '*', name: '*', begin: 0, end: url.hostname.length, value: url.hostname },
+        ],
+        pathnameNode: anyHostname,
+      })
+    }
+
     // static hostname + port -> pathname
     let staticHostname = hostNameNode.static.get(url.hostname)
     if (staticHostname) {
@@ -307,6 +325,7 @@ export class Trie<data = unknown> {
               params,
             })
           }
+          continue
         }

         let urlSegment = urlSegments[current.segmentIndex]
@@ -340,7 +359,7 @@ export class Trie<data = unknown> {
             }
             stack.push({
               segmentIndex: current.segmentIndex + 1,
-              pathnameNode: pathnameNode,
+              pathnameNode,
               charOffset: current.charOffset + match.index + match[0].length + 1,
               pathnameMatch,
             })
@@ -367,7 +386,7 @@ export class Trie<data = unknown> {
             }
             stack.push({
               segmentIndex: urlSegments.length,
-              pathnameNode: pathnameNode,
+              pathnameNode,
               charOffset: current.charOffset + remaining.length,
               pathnameMatch,
             })
PATCH
