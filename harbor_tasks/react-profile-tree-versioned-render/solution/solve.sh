#!/bin/bash
set -euo pipefail

TEST_FILE="packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js"

# Check if already applied (idempotency check - look for the new import pattern)
if grep -q "getVersionedRenderImplementation" "$TEST_FILE" 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js b/packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js
index 968fda1..f08629d 100644
--- a/packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js
+++ b/packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js
@@ -9,10 +9,7 @@

 import type Store from 'react-devtools-shared/src/devtools/store';

-import {
-  getLegacyRenderImplementation,
-  getModernRenderImplementation,
-} from './utils';
+import {getVersionedRenderImplementation} from './utils';

 describe('commit tree', () => {
   let React = require('react');
@@ -32,12 +29,10 @@ describe('commit tree', () => {
     Scheduler = require('scheduler');
   });

-  const {render: legacyRender} = getLegacyRenderImplementation();
-  const {render: modernRender} = getModernRenderImplementation();
+  const {render} = getVersionedRenderImplementation();

   // @reactVersion >= 16.9
-  // @reactVersion <= 18.2
-  it('should be able to rebuild the store tree for each commit (legacy render)', () => {
+  it('should be able to rebuild the store tree for each commit', () => {
     const Parent = ({count}) => {
       Scheduler.unstable_advanceTime(10);
       return new Array(count)
@@ -50,13 +45,13 @@ describe('commit tree', () => {
     });

     utils.act(() => store.profilerStore.startProfiling());
-    utils.act(() => legacyRender(<Parent count={1} />));
+    utils.act(() => render(<Parent count={1} />));
     expect(store).toMatchInlineSnapshot(`
       [root]
         ▾ <Parent>
             <Child key="0"> [Memo]
     `);
-    utils.act(() => legacyRender(<Parent count={3} />));
+    utils.act(() => render(<Parent count={3} />));
     expect(store).toMatchInlineSnapshot(`
       [root]
         ▾ <Parent>
@@ -64,73 +59,14 @@ describe('commit tree', () => {
             <Child key="1"> [Memo]
             <Child key="2"> [Memo]
     `);
-    utils.act(() => legacyRender(<Parent count={2} />));
+    utils.act(() => render(<Parent count={2} />));
     expect(store).toMatchInlineSnapshot(`
       [root]
         ▾ <Parent>
             <Child key="0"> [Memo]
             <Child key="1"> [Memo]
     `);
-    utils.act(() => legacyRender(<Parent count={0} />));
-    expect(store).toMatchInlineSnapshot(`
-      [root]
-          <Parent>
-    `);
-    utils.act(() => store.profilerStore.stopProfiling());
-
-    const rootID = store.roots[0];
-    const commitTrees = [];
-    for (let commitIndex = 0; commitIndex < 4; commitIndex++) {
-      commitTrees.push(
-        store.profilerStore.profilingCache.getCommitTree({
-          commitIndex,
-          rootID,
-        }),
-      );
-    }
-
-    expect(commitTrees[0].nodes.size).toBe(3); // <Root> + <Parent> + <Child>
-    expect(commitTrees[1].nodes.size).toBe(5); // <Root> + <Parent> + <Child> x 3
-    expect(commitTrees[2].nodes.size).toBe(4); // <Root> + <Parent> + <Child> x 2
-    expect(commitTrees[3].nodes.size).toBe(2); // <Root> + <Parent>
-  });
-
-  // @reactVersion >= 18
-  it('should be able to rebuild the store tree for each commit (createRoot)', () => {
-    const Parent = ({count}) => {
-      Scheduler.unstable_advanceTime(10);
-      return new Array(count)
-        .fill(true)
-        .map((_, index) => <Child key={index} />);
-    };
-    const Child = React.memo(function Child() {
-      Scheduler.unstable_advanceTime(2);
-      return null;
-    });
-
-    utils.act(() => store.profilerStore.startProfiling());
-    utils.act(() => modernRender(<Parent count={1} />));
-    expect(store).toMatchInlineSnapshot(`
-      [root]
-        ▾ <Parent>
-            <Child key="0"> [Memo]
-    `);
-    utils.act(() => modernRender(<Parent count={3} />));
-    expect(store).toMatchInlineSnapshot(`
-      [root]
-        ▾ <Parent>
-            <Child key="0"> [Memo]
-            <Child key="1"> [Memo]
-            <Child key="2"> [Memo]
-    `);
-    utils.act(() => modernRender(<Parent count={2} />));
-    expect(store).toMatchInlineSnapshot(`
-      [root]
-        ▾ <Parent>
-            <Child key="0"> [Memo]
-            <Child key="1"> [Memo]
-    `);
-    utils.act(() => modernRender(<Parent count={0} />));
+    utils.act(() => render(<Parent count={0} />));
     expect(store).toMatchInlineSnapshot(`
       [root]
           <Parent>
@@ -179,10 +115,9 @@ describe('commit tree', () => {
     });

     // @reactVersion >= 16.9
-    // @reactVersion <= 18.2
-    it('should support Lazy components (legacy render)', async () => {
+    it('should support Lazy components', async () => {
       utils.act(() => store.profilerStore.startProfiling());
-      utils.act(() => legacyRender(<App renderChildren={true} />));
+      utils.act(() => render(<App renderChildren={true} />));
       await Promise.resolve();
       expect(store).toMatchInlineSnapshot(`
         [root]
@@ -191,7 +126,7 @@ describe('commit tree', () => {
         [suspense-root]  rects={null}
           <Suspense name="App" rects={null}>
       `);
-      utils.act(() => legacyRender(<App renderChildren={true} />));
+      utils.act(() => render(<App renderChildren={true} />));
       expect(store).toMatchInlineSnapshot(`
         [root]
           ▾ <App>
@@ -200,7 +135,7 @@ describe('commit tree', () => {
         [suspense-root]  rects={null}
           <Suspense name="App" rects={null}>
       `);
-      utils.act(() => legacyRender(<App renderChildren={false} />));
+      utils.act(() => render(<App renderChildren={false} />));
       expect(store).toMatchInlineSnapshot(`
         [root]
             <App>
@@ -223,55 +158,10 @@ describe('commit tree', () => {
       expect(commitTrees[2].nodes.size).toBe(2); // <Root> + <App>
     });

-    // @reactVersion >= 18.0
-    it('should support Lazy components (createRoot)', async () => {
-      utils.act(() => store.profilerStore.startProfiling());
-      utils.act(() => modernRender(<App renderChildren={true} />));
-      await Promise.resolve();
-      expect(store).toMatchInlineSnapshot(`
-        [root]
-          ▾ <App>
-              <Suspense>
-        [suspense-root]  rects={null}
-          <Suspense name="App" rects={null}>
-      `);
-      utils.act(() => modernRender(<App renderChildren={true} />));
-      expect(store).toMatchInlineSnapshot(`
-        [root]
-          ▾ <App>
-            ▾ <Suspense>
-                <LazyInnerComponent>
-        [suspense-root]  rects={null}
-          <Suspense name="App" rects={null}>
-      `);
-      utils.act(() => modernRender(<App renderChildren={false} />));
-      expect(store).toMatchInlineSnapshot(`
-        [root]
-            <App>
-      `);
-      utils.act(() => store.profilerStore.stopProfiling());
-
-      const rootID = store.roots[0];
-      const commitTrees = [];
-      for (let commitIndex = 0; commitIndex < 3; commitIndex++) {
-        commitTrees.push(
-          store.profilerStore.profilingCache.getCommitTree({
-            commitIndex,
-            rootID,
-          }),
-        );
-      }
-
-      expect(commitTrees[0].nodes.size).toBe(3); // <Root> + <App> + <Suspense>
-      expect(commitTrees[1].nodes.size).toBe(4); // <Root> + <App> + <Suspense> + <LazyInnerComponent>
-      expect(commitTrees[2].nodes.size).toBe(2); // <Root> + <App>
-    });
-
     // @reactVersion >= 16.9
-    // @reactVersion <= 18.2
-    it('should support Lazy components that are unmounted before resolving (legacy render)', async () => {
+    it('should support Lazy components that are unmounted before resolving', async () => {
       utils.act(() => store.profilerStore.startProfiling());
-      utils.act(() => legacyRender(<App renderChildren={true} />));
+      utils.act(() => render(<App renderChildren={true} />));
       expect(store).toMatchInlineSnapshot(`
         [root]
           ▾ <App>
@@ -279,7 +169,7 @@ describe('commit tree', () => {
         [suspense-root]  rects={null}
           <Suspense name="App" rects={null}>
       `);
-      utils.act(() => legacyRender(<App renderChildren={false} />));
+      utils.act(() => render(<App renderChildren={false} />));
       expect(store).toMatchInlineSnapshot(`
         [root]
             <App>
@@ -300,38 +190,5 @@ describe('commit tree', () => {
       expect(commitTrees[0].nodes.size).toBe(3);
       expect(commitTrees[1].nodes.size).toBe(2); // <Root> + <App>
     });
-
-    // @reactVersion >= 18.0
-    it('should support Lazy components that are unmounted before resolving (createRoot)', async () => {
-      utils.act(() => store.profilerStore.startProfiling());
-      utils.act(() => modernRender(<App renderChildren={true} />));
-      expect(store).toMatchInlineSnapshot(`
-        [root]
-          ▾ <App>
-              <Suspense>
-        [suspense-root]  rects={null}
-          <Suspense name="App" rects={null}>
-      `);
-      utils.act(() => modernRender(<App renderChildren={false} />));
-      expect(store).toMatchInlineSnapshot(`
-        [root]
-            <App>
-      `);
-      utils.act(() => store.profilerStore.stopProfiling());
-
-      const rootID = store.roots[0];
-      const commitTrees = [];
-      for (let commitIndex = 0; commitIndex < 2; commitIndex++) {
-        commitTrees.push(
-          store.profilerStore.profilingCache.getCommitTree({
-            commitIndex,
-            rootID,
-          }),
-        );
-      }
-
-      expect(commitTrees[0].nodes.size).toBe(3); // <Root> + <App> + <Suspense>
-      expect(commitTrees[1].nodes.size).toBe(2); // <Root> + <App>
-    });
   });
 });
PATCH

echo "Fix applied successfully"
