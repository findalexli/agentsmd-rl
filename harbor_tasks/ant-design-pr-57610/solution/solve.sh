#!/bin/bash
# Gold solution for ant-design Image accessibility enhancement
set -e

cd /workspace/antd

# Check if patch has already been applied (idempotency)
if grep -q "genFocusOutline" components/image/style/index.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/image/demo/_semantic.tsx b/components/image/demo/_semantic.tsx
index e5c1e996f571..a0ef5f3fafb3 100644
--- a/components/image/demo/_semantic.tsx
+++ b/components/image/demo/_semantic.tsx
@@ -73,7 +73,7 @@ const Block: React.FC<Readonly<ImagePropsBlock>> = ({ classNames, ...restProps }
           ]}
           classNames={classNames}
           styles={{ popup: { root: { position: 'absolute' } } }}
-          preview={{ getContainer: () => holderRef.current!, open: true }}
+          preview={{ getContainer: () => holderRef.current!, open: true, focusTrap: false }}
         />
       </div>
     </Flex>
diff --git a/components/image/index.en-US.md b/components/image/index.en-US.md
index ac4eb560b6a2..dda34496c806 100644
--- a/components/image/index.en-US.md
+++ b/components/image/index.en-US.md
@@ -75,6 +75,7 @@ Other Property ref [&lt;img>](https://developer.mozilla.org/en-US/docs/Web/HTML/
 | actionsRender | Custom toolbar render | (originalNode: React.ReactElement, info: ToolbarRenderInfoType) => React.ReactNode | - |  |
 | closeIcon | Custom close icon | React.ReactNode | - |  |
 | cover | Custom preview mask | React.ReactNode \| [CoverConfig](#coverconfig) | - | CoverConfig support after v6.0 |
+| focusTrap | Whether to trap focus within the preview when open | boolean | true | 6.4.0 |
 | ~~destroyOnClose~~ | Destroy child elements on preview close (removed, no longer supported) | boolean | false |  |
 | ~~forceRender~~ | Force render preview image (removed, no longer supported) | boolean | - |  |
 | getContainer | Specify container for preview mounting; still full screen; false mounts at current location | string \| HTMLElement \| (() => HTMLElement) \| false | - |  |
@@ -111,6 +112,7 @@ Other Property ref [&lt;img>](https://developer.mozilla.org/en-US/docs/Web/HTML/
 | actionsRender | Custom toolbar render | (originalNode: React.ReactElement, info: ToolbarRenderInfoType) => React.ReactNode | - |  |
 | closeIcon | Custom close icon | React.ReactNode | - |  |
 | countRender | Custom preview count render | (current: number, total: number) => React.ReactNode | - |  |
+| focusTrap | Whether to trap focus within the preview when open | boolean | true | 6.4.0 |
 | current | Index of the current preview image | number | - |  |
 | ~~forceRender~~ | Force render preview image (removed, no longer supported) | boolean | - |  |
 | getContainer | Specify container for preview mounting; still full screen; false mounts at current location | string \| HTMLElement \| (() => HTMLElement) \| false | - |  |
diff --git a/components/image/index.zh-CN.md b/components/image/index.zh-CN.md
index 786fe845963d..21defc734ef5 100644
--- a/components/image/index.zh-CN.md
+++ b/components/image/index.zh-CN.md
@@ -76,6 +76,7 @@ coverDark: https://mdn.alipayobjects.com/huamei_7uahnr/afts/img/A*LVQ3R5JjjJEAAA
 | actionsRender | 自定义工具栏渲染 | (originalNode: React.ReactElement, info: ToolbarRenderInfoType) => React.ReactNode | - |  |
 | closeIcon | 自定义关闭 Icon | React.ReactNode | - |  |
 | cover | 自定义预览遮罩 | React.ReactNode \| [CoverConfig](#coverconfig) | - | CoverConfig v6.0 开始支持 |
+| focusTrap | 预览打开时是否在预览内捕获焦点 | boolean | true | 6.4.0 |
 | ~~destroyOnClose~~ | 关闭预览时销毁子元素，已移除，不再支持 | boolean | false |  |
 | ~~forceRender~~ | 强制渲染预览图，已移除，不再支持 | boolean | - |  |
 | getContainer | 指定预览挂载的节点，但依旧为全屏展示，false 为挂载在当前位置 | string \| HTMLElement \| (() => HTMLElement) \| false | - |  |
@@ -112,6 +113,7 @@ coverDark: https://mdn.alipayobjects.com/huamei_7uahnr/afts/img/A*LVQ3R5JjjJEAAA
 | actionsRender | 自定义工具栏渲染 | (originalNode: React.ReactElement, info: ToolbarRenderInfoType) => React.ReactNode | - |  |
 | closeIcon | 自定义关闭 Icon | React.ReactNode | - |  |
 | countRender | 自定义预览计数内容 | (current: number, total: number) => React.ReactNode | - |  |
+| focusTrap | 预览打开时是否在预览内捕获焦点 | boolean | true | 6.4.0 |
 | current | 当前预览图的 index | number | - |  |
 | ~~forceRender~~ | 强制渲染预览图，已移除，不再支持 | boolean | - |  |
 | getContainer | 指定预览挂载的节点，但依旧为全屏展示，false 为挂载在当前位置 | string \| HTMLElement \| (() => HTMLElement) \| false | - |  |
diff --git a/components/image/style/index.ts b/components/image/style/index.ts
index c3643aaaa6cf..a0a3a015c2d5 100644
--- a/components/image/style/index.ts
+++ b/components/image/style/index.ts
@@ -4,6 +4,7 @@ import { FastColor } from '@ant-design/fast-color';

 import type { FullToken, GenerateStyle, GetDefaultToken } from '../../theme/internal';
 import { genStyleHooks, mergeToken } from '../../theme/internal';
+import { genFocusOutline, genFocusStyle } from '../../style';
 import { inkFlow1, inkFlow2, inkFlow3, progressActive } from './progressAnimation';

 export interface ComponentToken {
@@ -79,7 +80,7 @@ export const genImageCoverStyle: GenerateStyle<ImageToken, CSSObject> = (token)
         opacity: 0,
         transition: `opacity ${motionDurationSlow}`,
       },
-      '&:hover': {
+      '&:hover, &:focus-visible': {
         [`${componentCls}-cover`]: {
           opacity: 1,
         },
@@ -270,6 +271,7 @@ export const genImagePreviewStyle: GenerateStyle<ImageToken, CSSObject> = (token
     '&:active': {
       backgroundColor: operationBg.toRgbString(),
     },
+    '&:focus-visible': genFocusOutline(token),
   };

   return {
@@ -393,6 +395,7 @@ export const genImagePreviewStyle: GenerateStyle<ImageToken, CSSObject> = (token
           [`&:not(${previewCls}-actions-action-disabled):hover`]: {
             color: previewOperationHoverColor,
           },
+          '&:focus-visible': genFocusOutline(token),
           '&-disabled': {
             color: previewOperationColorDisabled,
             cursor: 'not-allowed',
@@ -410,6 +413,7 @@ const genImageStyle: GenerateStyle<ImageToken, CSSObject> = (token) => {
     [componentCls]: {
       position: 'relative',
       display: 'inline-block',
+      ...genFocusStyle(token),
       [`${componentCls}-img`]: {
         width: '100%',
         height: 'auto',
diff --git a/package.json b/package.json
index a888bdc1e470..fa99154901ce 100644
--- a/package.json
+++ b/package.json
@@ -121,7 +121,7 @@
     "@rc-component/drawer": "~1.4.2",
     "@rc-component/dropdown": "~1.0.2",
     "@rc-component/form": "~1.8.0",
-    "@rc-component/image": "~1.8.0",
+    "@rc-component/image": "~1.9.0",
     "@rc-component/input": "~1.3.0",
     "@rc-component/input-number": "~1.6.2",
     "@rc-component/mentions": "~1.8.1",
PATCH

# Install updated dependencies (for the @rc-component/image upgrade)
npm install --legacy-peer-deps

echo "Patch applied successfully"
