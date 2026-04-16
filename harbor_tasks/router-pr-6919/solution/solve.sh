#!/bin/bash
set -euo pipefail

cd /workspace/router

# Idempotency check - skip if already applied
if grep -q "getUniqueProgramIdentifier" packages/router-plugin/src/core/utils.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/packages/router-plugin/src/core/code-splitter/compilers.ts b/packages/router-plugin/src/core/code-splitter/compilers.ts
index 6e0f4068096..49b9fb6a29a 100644
--- a/packages/router-plugin/src/core/code-splitter/compilers.ts
+++ b/packages/router-plugin/src/core/code-splitter/compilers.ts
@@ -11,6 +11,10 @@ import { tsrShared, tsrSplit } from '../constants'
 import { routeHmrStatement } from '../route-hmr-statement'
 import { createIdentifier } from './path-ids'
 import { getFrameworkOptions } from './framework-options'
+import type {
+  CompileCodeSplitReferenceRouteOptions,
+  ReferenceRouteCompilerPlugin,
+} from './plugins'
 import type { GeneratorResult, ParseAstOptions } from '@tanstack/router-utils'
 import type { CodeSplitGroupings, SplitRouteIdentNodes } from '../constants'
 import type { Config, DeletableNodes } from '../config'
@@ -642,6 +646,7 @@ export function compileCodeSplitReferenceRoute(
     id: string
     addHmr?: boolean
     sharedBindings?: Set<string>
+    compilerPlugins?: Array<ReferenceRouteCompilerPlugin>
   },
 ): GeneratorResult | null {
   const ast = parseAst(opts)
@@ -714,6 +719,23 @@ export function compileCodeSplitReferenceRoute(
                   )
                 }
                 if (!splittableCreateRouteFns.includes(createRouteFn)) {
+                  const insertionPath = path.getStatementParent() ?? path
+
+                  opts.compilerPlugins?.forEach((plugin) => {
+                    const pluginResult = plugin.onUnsplittableRoute?.({
+                      programPath,
+                      callExpressionPath: path,
+                      insertionPath,
+                      routeOptions,
+                      createRouteFn,
+                      opts: opts as CompileCodeSplitReferenceRouteOptions,
+                    })
+
+                    if (pluginResult?.modified) {
+                      modified = true
+                    }
+                  })
+
                   // we can't split this route but we still add HMR handling if enabled
                   if (opts.addHmr && !hmrAdded) {
                     programPath.pushContainer('body', routeHmrStatement)
diff --git a/packages/router-plugin/src/core/code-splitter/plugins.ts b/packages/router-plugin/src/core/code-splitter/plugins.ts
new file mode 100644
index 00000000000..52f2f315edc
--- /dev/null
+++ b/packages/router-plugin/src/core/code-splitter/plugins.ts
@@ -0,0 +1,34 @@
+import type babel from '@babel/core'
+import type * as t from '@babel/types'
+import type { Config, DeletableNodes } from '../config'
+import type { CodeSplitGroupings } from '../constants'
+
+export type CompileCodeSplitReferenceRouteOptions = {
+  codeSplitGroupings: CodeSplitGroupings
+  deleteNodes?: Set<DeletableNodes>
+  targetFramework: Config['target']
+  filename: string
+  id: string
+  addHmr?: boolean
+  sharedBindings?: Set<string>
+}
+
+export type ReferenceRouteCompilerPluginContext = {
+  programPath: babel.NodePath<t.Program>
+  callExpressionPath: babel.NodePath<t.CallExpression>
+  insertionPath: babel.NodePath
+  routeOptions: t.ObjectExpression
+  createRouteFn: string
+  opts: CompileCodeSplitReferenceRouteOptions
+}
+
+export type ReferenceRouteCompilerPluginResult = {
+  modified?: boolean
+}
+
+export type ReferenceRouteCompilerPlugin = {
+  name: string
+  onUnsplittableRoute?: (
+    ctx: ReferenceRouteCompilerPluginContext,
+  ) => void | ReferenceRouteCompilerPluginResult
+}
diff --git a/packages/router-plugin/src/core/code-splitter/plugins/framework-plugins.ts b/packages/router-plugin/src/core/code-splitter/plugins/framework-plugins.ts
new file mode 100644
index 00000000000..067dccd2362
--- /dev/null
+++ b/packages/router-plugin/src/core/code-splitter/plugins/framework-plugins.ts
@@ -0,0 +1,19 @@
+import { createReactRefreshRouteComponentsPlugin } from './react-refresh-route-components'
+import type { ReferenceRouteCompilerPlugin } from '../plugins'
+import type { Config } from '../../config'
+
+export function getReferenceRouteCompilerPlugins(opts: {
+  targetFramework: Config['target']
+  addHmr?: boolean
+}): Array<ReferenceRouteCompilerPlugin> | undefined {
+  switch (opts.targetFramework) {
+    case 'react': {
+      if (opts.addHmr) {
+        return [createReactRefreshRouteComponentsPlugin()]
+      }
+      return undefined
+    }
+    default:
+      return undefined
+  }
+}
diff --git a/packages/router-plugin/src/core/code-splitter/plugins/react-refresh-route-components.ts b/packages/router-plugin/src/core/code-splitter/plugins/react-refresh-route-components.ts
new file mode 100644
index 00000000000..6436e1b9acd
--- /dev/null
+++ b/packages/router-plugin/src/core/code-splitter/plugins/react-refresh-route-components.ts
@@ -0,0 +1,63 @@
+import * as t from '@babel/types'
+import { getUniqueProgramIdentifier } from '../../utils'
+import type { ReferenceRouteCompilerPlugin } from '../plugins'
+
+const REACT_REFRESH_ROUTE_COMPONENT_IDENTS = new Set([
+  'component',
+  'pendingComponent',
+  'errorComponent',
+  'notFoundComponent',
+])
+
+export function createReactRefreshRouteComponentsPlugin(): ReferenceRouteCompilerPlugin {
+  return {
+    name: 'react-refresh-route-components',
+    onUnsplittableRoute(ctx) {
+      if (!ctx.opts.addHmr) {
+        return
+      }
+
+      const hoistedDeclarations: Array<t.VariableDeclaration> = []
+
+      ctx.routeOptions.properties.forEach((prop) => {
+        if (!t.isObjectProperty(prop) || !t.isIdentifier(prop.key)) {
+          return
+        }
+
+        if (!REACT_REFRESH_ROUTE_COMPONENT_IDENTS.has(prop.key.name)) {
+          return
+        }
+
+        if (
+          !t.isArrowFunctionExpression(prop.value) &&
+          !t.isFunctionExpression(prop.value)
+        ) {
+          return
+        }
+
+        const hoistedIdentifier = getUniqueProgramIdentifier(
+          ctx.programPath,
+          `TSR${prop.key.name[0]!.toUpperCase()}${prop.key.name.slice(1)}`,
+        )
+
+        hoistedDeclarations.push(
+          t.variableDeclaration('const', [
+            t.variableDeclarator(
+              hoistedIdentifier,
+              t.cloneNode(prop.value, true),
+            ),
+          ]),
+        )
+
+        prop.value = t.cloneNode(hoistedIdentifier)
+      })
+
+      if (hoistedDeclarations.length === 0) {
+        return
+      }
+
+      ctx.insertionPath.insertBefore(hoistedDeclarations)
+      return { modified: true }
+    },
+  }
+}
diff --git a/packages/router-plugin/src/core/router-code-splitter-plugin.ts b/packages/router-plugin/src/core/router-code-splitter-plugin.ts
index c0d8bf357ed..36b51798d03 100644
--- a/packages/router-plugin/src/core/router-code-splitter-plugin.ts
+++ b/packages/router-plugin/src/core/router-code-splitter-plugin.ts
@@ -13,6 +13,7 @@ import {
   computeSharedBindings,
   detectCodeSplitGroupingsFromRoute,
 } from './code-splitter/compilers'
+import { getReferenceRouteCompilerPlugins } from './code-splitter/plugins/framework-plugins'
 import {
   defaultCodeSplitGroupings,
   splitRouteIdentNodes,
@@ -90,7 +91,6 @@ export const unpluginRouterCodeSplitterFactory: UnpluginFactory<
     }
   }
   const isProduction = process.env.NODE_ENV === 'production'
-
   // Map from normalized route file path → set of shared binding names.
   // Populated by the reference compiler, consumed by virtual and shared compilers.
   const sharedBindingsMap = new Map<string, Set<string>>()
@@ -156,6 +156,9 @@ export const unpluginRouterCodeSplitterFactory: UnpluginFactory<
       sharedBindingsMap.delete(id)
     }

+    const addHmr =
+      (userConfig.codeSplittingOptions?.addHmr ?? true) && !isProduction
+
     const compiledReferenceRoute = compileCodeSplitReferenceRoute({
       code,
       codeSplitGroupings: splitGroupings,
@@ -165,9 +168,12 @@ export const unpluginRouterCodeSplitterFactory: UnpluginFactory<
       deleteNodes: userConfig.codeSplittingOptions?.deleteNodes
         ? new Set(userConfig.codeSplittingOptions.deleteNodes)
         : undefined,
-      addHmr:
-        (userConfig.codeSplittingOptions?.addHmr ?? true) && !isProduction,
+      addHmr,
       sharedBindings: sharedBindings.size > 0 ? sharedBindings : undefined,
+      compilerPlugins: getReferenceRouteCompilerPlugins({
+        targetFramework: userConfig.target,
+        addHmr,
+      }),
     })

     if (compiledReferenceRoute === null) {
diff --git a/packages/router-plugin/src/core/router-hmr-plugin.ts b/packages/router-plugin/src/core/router-hmr-plugin.ts
index 1983d5b34b6..12c95bb2371 100644
--- a/packages/router-plugin/src/core/router-hmr-plugin.ts
+++ b/packages/router-plugin/src/core/router-hmr-plugin.ts
@@ -1,4 +1,6 @@
 import { generateFromAst, logDiff, parseAst } from '@tanstack/router-utils'
+import { compileCodeSplitReferenceRoute } from './code-splitter/compilers'
+import { getReferenceRouteCompilerPlugins } from './code-splitter/plugins/framework-plugins'
 import { routeHmrStatement } from './route-hmr-statement'
 import { debug, normalizePath } from './utils'
 import { getConfig } from './config'
@@ -41,6 +43,30 @@ export const unpluginRouterHmrFactory: UnpluginFactory<

         if (debug) console.info('Adding HMR handling to route ', normalizedId)

+        if (userConfig.target === 'react') {
+          const compiled = compileCodeSplitReferenceRoute({
+            code,
+            filename: normalizedId,
+            id: normalizedId,
+            addHmr: true,
+            codeSplitGroupings: [],
+            targetFramework: 'react',
+            compilerPlugins: getReferenceRouteCompilerPlugins({
+              targetFramework: 'react',
+              addHmr: true,
+            }),
+          })
+
+          if (compiled) {
+            if (debug) {
+              logDiff(code, compiled.code)
+              console.log('Output:\n', compiled.code + '\n\n')
+            }
+
+            return compiled
+          }
+        }
+
         const ast = parseAst({ code })
         ast.program.body.push(routeHmrStatement)
         const result = generateFromAst(ast, {
diff --git a/packages/router-plugin/src/core/utils.ts b/packages/router-plugin/src/core/utils.ts
index 7f31f212b8e..84ccf86894d 100644
--- a/packages/router-plugin/src/core/utils.ts
+++ b/packages/router-plugin/src/core/utils.ts
@@ -1,3 +1,6 @@
+import * as t from '@babel/types'
+import type babel from '@babel/core'
+
 export const debug =
   process.env.TSR_VITE_DEBUG &&
   ['true', 'router-plugin'].includes(process.env.TSR_VITE_DEBUG)
@@ -12,3 +15,21 @@ export const debug =
 export function normalizePath(path: string): string {
   return path.replace(/\\/g, '/')
 }
+
+export function getUniqueProgramIdentifier(
+  programPath: babel.NodePath<t.Program>,
+  baseName: string,
+): t.Identifier {
+  let name = baseName
+  let suffix = 2
+
+  while (
+    programPath.scope.hasBinding(name) ||
+    programPath.scope.hasGlobal(name)
+  ) {
+    name = `${baseName}${suffix}`
+    suffix++
+  }
+
+  return t.identifier(name)
+}
diff --git a/packages/router-plugin/tests/add-hmr.test.ts b/packages/router-plugin/tests/add-hmr.test.ts
index 893b65d9c61..3369ea6dd9f 100644
--- a/packages/router-plugin/tests/add-hmr.test.ts
+++ b/packages/router-plugin/tests/add-hmr.test.ts
@@ -4,6 +4,7 @@ import { describe, expect, it } from 'vitest'

 import { compileCodeSplitReferenceRoute } from '../src/core/code-splitter/compilers'
 import { defaultCodeSplitGroupings } from '../src/core/constants'
+import { getReferenceRouteCompilerPlugins } from '../src/core/code-splitter/plugins/framework-plugins'
 import { frameworks } from './constants'

 function getFrameworkDir(framework: string) {
@@ -30,6 +31,10 @@ describe('add-hmr works', () => {
           addHmr: true,
           codeSplitGroupings: defaultCodeSplitGroupings,
           targetFramework: framework,
+          compilerPlugins: getReferenceRouteCompilerPlugins({
+            targetFramework: framework,
+            addHmr: true,
+          }),
         })

         await expect(compileResult?.code || code).toMatchFileSnapshot(
@@ -51,6 +56,10 @@ describe('add-hmr works', () => {
           addHmr: false,
           codeSplitGroupings: defaultCodeSplitGroupings,
           targetFramework: framework,
+          compilerPlugins: getReferenceRouteCompilerPlugins({
+            targetFramework: framework,
+            addHmr: false,
+          }),
         })

         await expect(compileResult?.code || code).toMatchFileSnapshot(
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@false.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@false.tsx
new file mode 100644
index 00000000000..5daf0186170
--- /dev/null
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@false.tsx
@@ -0,0 +1,6 @@
+import * as React from 'react'
+import { createRootRoute } from '@tanstack/react-router'
+
+export const Route = createRootRoute({
+  component: () => <div>root hmr</div>,
+})
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@true.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@true.tsx
new file mode 100644
index 00000000000..a8a83bbbb88
--- /dev/null
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/createRootRoute-inline-component@true.tsx
@@ -0,0 +1,44 @@
+import * as React from 'react';
+import { createRootRoute } from '@tanstack/react-router';
+const TSRComponent = () => <div>root hmr</div>;
+export const Route = createRootRoute({
+  component: TSRComponent
+});
+if (import.meta.hot) {
+  import.meta.hot.accept(newModule => {
+    if (Route && newModule && newModule.Route) {
+      (function handleRouteUpdate(oldRoute, newRoute) {
+        newRoute._path = oldRoute._path;
+        newRoute._id = oldRoute._id;
+        newRoute._fullPath = oldRoute._fullPath;
+        newRoute._to = oldRoute._to;
+        newRoute.children = oldRoute.children;
+        newRoute.parentRoute = oldRoute.parentRoute;
+        const router = window.__TSR_ROUTER__;
+        router.routesById[newRoute.id] = newRoute;
+        router.routesByPath[newRoute.fullPath] = newRoute;
+        router.processedTree.matchCache.clear();
+        router.processedTree.flatCache?.clear();
+        router.processedTree.singleCache.clear();
+        router.resolvePathCache.clear();
+        walkReplaceSegmentTree(newRoute, router.processedTree.segmentTree);
+        const filter = m => m.routeId === oldRoute.id;
+        if (router.state.matches.find(filter) || router.state.pendingMatches?.find(filter)) {
+          router.invalidate({
+            filter
+          });
+        }
+        ;
+        function walkReplaceSegmentTree(route, node) {
+          if (node.route?.id === route.id) node.route = route;
+          if (node.index) walkReplaceSegmentTree(route, node.index);
+          node.static?.forEach(child => walkReplaceSegmentTree(route, child));
+          node.staticInsensitive?.forEach(child => walkReplaceSegmentTree(route, child));
+          node.dynamic?.forEach(child => walkReplaceSegmentTree(route, child));
+          node.optional?.forEach(child => walkReplaceSegmentTree(route, child));
+          node.wildcard?.forEach(child => walkReplaceSegmentTree(route, child));
+        }
+      })(Route, newModule.Route);
+    }
+  });
+}
\ No newline at end of file
diff --git a/packages/router-plugin/tests/add-hmr/test-files/react/createRootRoute-inline-component.tsx b/packages/router-plugin/tests/add-hmr/test-files/react/createRootRoute-inline-component.tsx
new file mode 100644
index 00000000000..5daf0186170
--- /dev/null
+++ b/packages/router-plugin/tests/add-hmr/test-files/react/createRootRoute-inline-component.tsx
@@ -0,0 +1,6 @@
+import * as React from 'react'
+import { createRootRoute } from '@tanstack/react-router'
+
+export const Route = createRootRoute({
+  component: () => <div>root hmr</div>,
+})
diff --git a/packages/router-plugin/tests/utils.test.ts b/packages/router-plugin/tests/utils.test.ts
index 08c34206223..e49637feea5 100644
--- a/packages/router-plugin/tests/utils.test.ts
+++ b/packages/router-plugin/tests/utils.test.ts
@@ -1,5 +1,27 @@
+import * as babel from '@babel/core'
+import { parseAst } from '@tanstack/router-utils'
 import { describe, expect, it } from 'vitest'
-import { normalizePath } from '../src/core/utils'
+import { getUniqueProgramIdentifier, normalizePath } from '../src/core/utils'
+import type { NodePath } from '@babel/core'
+import type * as t from '@babel/types'
+
+function getProgramPath(code: string): NodePath<t.Program> {
+  const ast = parseAst({ code })
+  let programPath: NodePath<t.Program> | undefined
+
+  babel.traverse(ast, {
+    Program(path: NodePath<t.Program>) {
+      programPath = path
+      path.stop()
+    },
+  })
+
+  if (!programPath) {
+    throw new Error('Program path not found')
+  }
+
+  return programPath
+}

 describe('normalizePath', () => {
   it('should convert Windows backslashes to forward slashes', () => {
@@ -34,3 +56,31 @@ describe('normalizePath', () => {
     )
   })
 })
+
+describe('getUniqueProgramIdentifier', () => {
+  it('returns the base name when unused', () => {
+    const programPath = getProgramPath('const existing = 1')
+
+    expect(getUniqueProgramIdentifier(programPath, 'TSRComponent').name).toBe(
+      'TSRComponent',
+    )
+  })
+
+  it('appends numeric suffixes for existing bindings', () => {
+    const programPath = getProgramPath(
+      'const TSRComponent = 1\nconst TSRComponent2 = 2',
+    )
+
+    expect(getUniqueProgramIdentifier(programPath, 'TSRComponent').name).toBe(
+      'TSRComponent3',
+    )
+  })
+
+  it('avoids globals too', () => {
+    const programPath = getProgramPath('const existing = window')
+
+    expect(getUniqueProgramIdentifier(programPath, 'window').name).toBe(
+      'window2',
+    )
+  })
+})
PATCH

echo "Patch applied successfully."
