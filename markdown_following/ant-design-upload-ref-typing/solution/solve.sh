#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

if grep -q "RefAttributes<UploadRef<U>>" components/upload/index.tsx 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/components/upload/index.tsx b/components/upload/index.tsx
index b69ef1f255f7..9d9210a0690d 100644
--- a/components/upload/index.tsx
+++ b/components/upload/index.tsx
@@ -1,5 +1,5 @@
 import Dragger from './Dragger';
-import type { UploadProps } from './Upload';
+import type { UploadProps, UploadRef } from './Upload';
 import InternalUpload, { LIST_IGNORE } from './Upload';

 export type { DraggerProps } from './Dragger';
@@ -13,12 +13,13 @@ export type {
   UploadSemanticName,
   UploadSemanticStyles,
 } from './interface';
+export type { UploadRef } from './Upload';

 type InternalUploadType = typeof InternalUpload;

 type CompoundedComponent<T = any> = InternalUploadType & {
   <U extends T>(
-    props: React.PropsWithChildren<UploadProps<U>> & React.RefAttributes<any>,
+    props: React.PropsWithChildren<UploadProps<U>> & React.RefAttributes<UploadRef<U>>,
   ): React.ReactElement;
   Dragger: typeof Dragger;
   LIST_IGNORE: string;
diff --git a/tests/utils.tsx b/tests/utils.tsx
index f260ade3b4c6..9585f51a43ab 100644
--- a/tests/utils.tsx
+++ b/tests/utils.tsx
@@ -33,7 +33,7 @@ const customRender = (ui: ReactElement, options?: Partial<RenderOptions>) =>
   render(ui, { wrapper: StrictMode, ...options });

 export function renderHook<T>(func: () => T): { result: React.RefObject<T> } {
-  const result = createRef<any>();
+  const result = createRef<ReturnType<typeof func>>();

   const Demo: React.FC = () => {
     result.current = func();
PATCH

echo "Patch applied successfully."
