#!/bin/bash
set -e

cd /workspace/ant-design

# Check if patch is already applied (idempotency check)
# The distinctive line from the patch: icon styling with clsx
if grep -q 'className={clsx(\`${prefixCls}-message-icon\`, classNames?.icon)}' components/popconfirm/PurePanel.tsx; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/components/popconfirm/PurePanel.tsx b/components/popconfirm/PurePanel.tsx
index dce1a8613145..f5db12de4da7 100644
--- a/components/popconfirm/PurePanel.tsx
+++ b/components/popconfirm/PurePanel.tsx
@@ -2,7 +2,6 @@ import * as React from 'react';
 import ExclamationCircleFilled from '@ant-design/icons/ExclamationCircleFilled';
 import { clsx } from 'clsx';

-import type { PopconfirmProps } from '.';
 import ActionButton from '../_util/ActionButton';
 import { getRenderPropValue } from '../_util/getRenderPropValue';
 import Button from '../button/Button';
@@ -10,7 +9,7 @@ import { convertLegacyProps } from '../button/buttonHelpers';
 import { ConfigContext } from '../config-provider';
 import { useLocale } from '../locale';
 import defaultLocale from '../locale/en_US';
-import type { PopoverSemanticAllType } from '../popover';
+import type { PopconfirmProps, PopconfirmSemanticAllType } from '.';
 import PopoverPurePanel from '../popover/PurePanel';
 import useStyle from './style';

@@ -37,8 +36,8 @@ export interface OverlayProps
   close?: (...args: any[]) => void;
   onConfirm?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
   onCancel?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
-  classNames?: PopoverSemanticAllType['classNames'];
-  styles?: PopoverSemanticAllType['styles'];
+  classNames?: PopconfirmSemanticAllType['classNames'];
+  styles?: PopconfirmSemanticAllType['styles'];
 }

 export const Overlay: React.FC<OverlayProps> = (props) => {
@@ -71,7 +70,14 @@ export const Overlay: React.FC<OverlayProps> = (props) => {
   return (
     <div className={`${prefixCls}-inner-content`} onClick={onPopupClick}>
       <div className={`${prefixCls}-message`}>
-        {icon && <span className={`${prefixCls}-message-icon`}>{icon}</span>}
+        {icon && (
+          <span
+            className={clsx(`${prefixCls}-message-icon`, classNames?.icon)}
+            style={styles?.icon}
+          >
+            {icon}
+          </span>
+        )}
         <div className={`${prefixCls}-message-text`}>
           {titleNode && (
             <div className={clsx(`${prefixCls}-title`, classNames?.title)} style={styles?.title}>
diff --git a/components/popconfirm/__tests__/__snapshots__/demo-semantic.test.tsx.snap b/components/popconfirm/__tests__/__snapshots__/demo-semantic.test.tsx.snap
index e8588124a31f..14cd2e84c067 100644
--- a/components/popconfirm/__tests__/__snapshots__/demo-semantic.test.tsx.snap
+++ b/components/popconfirm/__tests__/__snapshots__/demo-semantic.test.tsx.snap
@@ -44,7 +44,7 @@ exports[\`renders components/popconfirm/demo/_semantic.tsx correctly 1\`] =
                   class="ant-popconfirm-message"
                 >
                   <span
-                    class="ant-popconfirm-message-icon"
+                    class="ant-popconfirm-message-icon semantic-mark-icon"
                   >
                     <span
                       aria-label="exclamation-circle"
@@ -299,6 +299,99 @@ exports[\`renders components/popconfirm/demo/_semantic.tsx correctly 1\`] =
             </div>
           </div>
         </li>
+        <li
+          class="acss-1ehfz5v"
+        >
+          <div
+            class="ant-flex css-var-test-id ant-flex-align-stretch ant-flex-gap-small ant-flex-vertical"
+          >
+            <div
+              class="ant-flex css-var-test-id ant-flex-align-center ant-flex-justify-space-between ant-flex-gap-small"
+            >
+              <div
+                class="ant-flex css-var-test-id ant-flex-align-center ant-flex-gap-small"
+              >
+                <h5
+                  class="ant-typography css-var-test-id"
+                  style="margin: 0px;"
+                >
+                  icon
+                </h5>
+              </div>
+              <div
+                class="ant-flex css-var-test-id ant-flex-align-center ant-flex-gap-small"
+              >
+                <button
+                  aria-hidden="true"
+                  class="ant-btn css-var-test-id ant-btn-default ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"
+                  type="button"
+                >
+                  <span
+                    class="ant-btn-icon"
+                  >
+                    <span
+                      aria-label="pushpin"
+                      class="anticon anticon-pushpin"
+                      role="img"
+                    >
+                      <svg
+                        aria-hidden="true"
+                        data-icon="pushpin"
+                        fill="currentColor"
+                        focusable="false"
+                        height="1em"
+                        viewBox="64 64 896 896"
+                        width="1em"
+                      >
+                        <path
+                          d="M878.3 392.1L631.9 145.7c-6.5-6.5-15-9.7-23.5-9.7s-17 3.2-23.5 9.7L423.8 306.9c-12.2-1.4-24.5-2-36.8-2-73.2 0-146.4 24.1-206.5 72.3a33.23 33.23 0 00-2.7 49.4l181.7 181.7-215.4 215.2a15.8 15.8 0 00-4.6 9.8l-3.4 37.2c-.9 9.4 6.6 17.4 15.9 17.4.5 0 1 0 1.5-.1l37.2-3.4c3.7-.3 7.2-2 9.8-4.6l215.4-215.4 181.7 181.7c6.5 6.5 15 9.7 23.5 9.7 9.7 0 19.3-4.2 25.9-12.4 56.3-70.3 79.7-158.3 70.2-243.4l161.1-161.1c12.9-12.8 12.9-33.8 0-46.8zM666.2 549.3l-24.5 24.5 3.8 34.4a259.92 259.92 0 01-30.4 153.9L262 408.8c12.9-7.1 26.3-13.1 40.3-17.9 27.2-9.4 55.7-14.1 84.7-14.1 9.6 0 19.3.5 28.9 1.6l34.4 3.8 24.5-24.5L608.5 224 800 415.5 666.2 549.3z"
+                        />
+                      </svg>
+                    </span>
+                  </span>
+                </button>
+                <button
+                  aria-hidden="true"
+                  class="ant-btn css-var-test-id ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"
+                  type="button"
+                >
+                  <span
+                    class="ant-btn-icon"
+                  >
+                    <span
+                      aria-label="info-circle"
+                      class="anticon anticon-info-circle"
+                      role="img"
+                    >
+                      <svg
+                        aria-hidden="true"
+                        data-icon="info-circle"
+                        fill="currentColor"
+                        focusable="false"
+                        height="1em"
+                        viewBox="64 64 896 896"
+                        width="1em"
+                      >
+                        <path
+                          d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"
+                        />
+                        <path
+                          d="M464 336a48 48 0 1096 0 48 48 0 10-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z"
+                        />
+                      </svg>
+                    </span>
+                  </span>
+                </button>
+              </div>
+            </div>
+            <div
+              class="ant-typography css-var-test-id"
+              style="margin: 0px; font-size: 12px;"
+            >
+              图标元素，设置确认图标的尺寸、颜色和布局样式
+            </div>
+          </div>
+        </li>
         <li
           class="acss-1ehfz5v"
         >
diff --git a/components/popconfirm/__tests__/semantic.test.tsx b/components/popconfirm/__tests__/semantic.test.tsx
index c501a704b11c..1bb85646ea8e 100644
--- a/components/popconfirm/__tests__/semantic.test.tsx
+++ b/components/popconfirm/__tests__/semantic.test.tsx
@@ -25,8 +25,12 @@ describe('Popconfirm.semantic', () => {
         title="Test"
         description="Content"
         open
-        classNames={{ root: 'custom-root', container: 'custom-container' }}
-        styles={{ root: { backgroundColor: 'red' }, container: { padding: '20px' } }}
+        classNames={{ root: 'custom-root', container: 'custom-container', icon: 'custom-icon' }}
+        styles={{
+          root: { backgroundColor: 'red' },
+          container: { padding: '20px' },
+          icon: { color: 'blue' },
+        }}
       >
         <span>Static Test</span>
       </Popconfirm>,
@@ -34,11 +38,14 @@ describe('Popconfirm.semantic', () => {

     const popconfirmElement = container.querySelector('.ant-popover');
     const contentElement = container.querySelector('.ant-popover-container');
+    const iconElement = container.querySelector('.ant-popconfirm-message-icon');

     expect(popconfirmElement).toHaveClass('custom-root');
     expect(contentElement).toHaveClass('custom-container');
+    expect(iconElement).toHaveClass('custom-icon');
     expect(popconfirmElement).toHaveStyle({ backgroundColor: 'rgb(255, 0, 0)' });
     expect(contentElement).toHaveStyle({ padding: '20px' });
+    expect(iconElement).toHaveStyle({ color: 'rgb(0, 0, 255)' });
   });

   it('should support function-based classNames and styles', () => {
@@ -51,10 +58,12 @@ describe('Popconfirm.semantic', () => {
         classNames={({ props }) => ({
           root: props.placement === 'top' ? 'top-root' : 'default-root',
           container: 'custom-container',
+          icon: 'dynamic-icon',
         })}
         styles={({ props }) => ({
           root: { backgroundColor: props.placement === 'top' ? 'blue' : 'transparent' },
           container: { padding: '16px' },
+          icon: { color: props.placement === 'top' ? 'green' : 'transparent' },
         })}
       >
         <span>Dynamic Test</span>
@@ -63,10 +72,13 @@ describe('Popconfirm.semantic', () => {

     const popconfirmElement = container.querySelector('.ant-popover');
     const contentElement = container.querySelector('.ant-popover-container');
+    const iconElement = container.querySelector('.ant-popconfirm-message-icon');

     expect(popconfirmElement).toHaveClass('top-root');
     expect(contentElement).toHaveClass('custom-container');
+    expect(iconElement).toHaveClass('dynamic-icon');
     expect(popconfirmElement).toHaveStyle({ backgroundColor: 'rgb(0, 0, 255)' });
     expect(contentElement).toHaveStyle({ padding: '16px' });
+    expect(iconElement).toHaveStyle({ color: 'rgb(0, 128, 0)' });
   });
 });
diff --git a/components/popconfirm/demo/_semantic.tsx b/components/popconfirm/demo/_semantic.tsx
index 40713a6efd8e..604b417ec0c7 100644
--- a/components/popconfirm/demo/_semantic.tsx
+++ b/components/popconfirm/demo/_semantic.tsx
@@ -9,6 +9,7 @@ const locales = {
   cn: {
     root: '根元素，设置绝对定位、层级、变换原点、箭头指向和弹层容器样式',
     container: '容器元素，设置背景色、内边距、圆角、阴影、边框和内容展示样式',
+    icon: '图标元素，设置确认图标的尺寸、颜色和布局样式',
     arrow: '箭头元素，设置宽高、位置、颜色和边框样式',
     title: '标题元素，设置标题文本样式和间距',
     content: '描述元素，设置描述文本样式和布局',
@@ -17,6 +18,7 @@ const locales = {
     root: 'Root element, set absolute positioning, z-index, transform origin, arrow direction and popover container styles',
     container:
       'Container element, set background color, padding, border radius, shadow, border and content display styles',
+    icon: 'Icon element, set the confirmation icon size, color and layout styles',
     arrow: 'Arrow element with width, height, position, color and border styles',
     title: 'Title element, set title text styles and spacing',
     content: 'Description element, set content text styles and layout',
@@ -49,6 +51,7 @@ const App: React.FC = () => {
       semantics={[
         { name: 'root', desc: locale.root },
         { name: 'container', desc: locale.container },
+        { name: 'icon', desc: locale.icon },
         { name: 'title', desc: locale.title },
         { name: 'content', desc: locale.content },
         { name: 'arrow', desc: locale.arrow },
diff --git a/components/popconfirm/index.tsx b/components/popconfirm/index.tsx
index 22ec2a4f874a..e315eccbf26e 100644
--- a/components/popconfirm/index.tsx
+++ b/components/popconfirm/index.tsx
@@ -9,14 +9,21 @@ import type { GenerateSemantic } from '../_util/hooks/useMergeSemantic/semanticT
 import { devUseWarning } from '../_util/warning';
 import type { ButtonProps, LegacyButtonType } from '../button/Button';
 import { useComponentConfig } from '../config-provider/context';
-import type { PopoverProps, PopoverSemanticAllType } from '../popover';
+import type { PopoverProps, PopoverSemanticType } from '../popover';
 import Popover from '../popover';
 import type { AbstractTooltipProps, TooltipRef } from '../tooltip';
 import useMergedArrow from '../tooltip/hook/useMergedArrow';
 import PurePanel, { Overlay } from './PurePanel';
 import useStyle from './style';

-export type PopconfirmSemanticType = PopoverSemanticAllType;
+export type PopconfirmSemanticType = {
+  classNames?: PopoverSemanticType['classNames'] & {
+    icon?: string;
+  };
+  styles?: PopoverSemanticType['styles'] & {
+    icon?: React.CSSProperties;
+  };
+};

 export type PopconfirmSemanticAllType = GenerateSemantic<PopconfirmSemanticType, PopconfirmProps>;
PATCH

echo "Patch applied successfully"
