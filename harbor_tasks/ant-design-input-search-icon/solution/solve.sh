#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

if grep -q "searchIcon: contextSearchIcon" components/input/Search.tsx 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

cat > /tmp/pr_57256.patch << 'PATCH_EOF'
diff --git a/components/config-provider/context.ts b/components/config-provider/context.ts
index c0eb19f26cf2..fc2beb10c2fe 100644
--- a/components/config-provider/context.ts
+++ b/components/config-provider/context.ts
@@ -257,7 +257,8 @@ export type BreadcrumbConfig = ComponentStyleConfig &
 export type InputConfig = ComponentStyleConfig &
   Pick<InputProps, 'autoComplete' | 'classNames' | 'styles' | 'allowClear' | 'variant'>;
 
-export type InputSearchConfig = ComponentStyleConfig & Pick<SearchProps, 'classNames' | 'styles'>;
+export type InputSearchConfig = ComponentStyleConfig &
+  Pick<SearchProps, 'classNames' | 'styles' | 'searchIcon'>;
 
 export type TextAreaConfig = ComponentStyleConfig &
   Pick<TextAreaProps, 'autoComplete' | 'classNames' | 'styles' | 'allowClear' | 'variant'>;
diff --git a/components/config-provider/index.en-US.md b/components/config-provider/index.en-US.md
index 27d975609f7f..1f056c5558de 100644
--- a/components/config-provider/index.en-US.md
+++ b/components/config-provider/index.en-US.md
@@ -138,7 +138,7 @@ const {
 | input | Set Input common props | { autoComplete?: string, className?: string, style?: React.CSSProperties, allowClear?: boolean \| { clearIcon?: ReactNode, disabled?: boolean } } | - | 4.2.0, `allowClear`: 5.15.0, `allowClear.disabled`: 6.4.0 |
 | inputNumber | Set InputNumber common props | { className?: string, style?: React.CSSProperties, classNames?: [InputNumberConfig\["classNames"\]](/components/input-number#semantic-dom), styles?: [InputNumberConfig\["styles"\]](/components/input-number#semantic-dom) } | - |  |
 | otp | Set OTP common props | { className?: string, style?: React.CSSProperties, classNames?: [OTPConfig\["classNames"\]](/components/input#semantic-otp), styles?: [OTPConfig\["styles"\]](/components/input#semantic-otp) } | - |  |
-| inputSearch | Set Search common props | { className?: string, style?: React.CSSProperties, classNames?: [InputSearchConfig\["classNames"\]](/components/input#semantic-search), styles?: [InputSearchConfig\["styles"\]](/components/input#semantic-search) } | - |  |
+| inputSearch | Set Search common props | { className?: string, style?: React.CSSProperties, classNames?: [InputSearchConfig\["classNames"\]](/components/input#semantic-search), styles?: [InputSearchConfig\["styles"\]](/components/input#semantic-search), searchIcon?: React.ReactNode } | - | searchIcon: 6.4.0 |
 | textArea | Set TextArea common props | { autoComplete?: string, className?: string, style?: React.CSSProperties,classNames?:[TextAreaConfig\["classNames"\]](/components/input#semantic-textarea), styles?: [TextAreaConfig\["styles"\]](/components/input#semantic-textarea), allowClear?: boolean \| { clearIcon?: ReactNode } } | - | 5.15.0 |
 | layout | Set Layout common props | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
 | list | Set List common props | { className?: string, style?: React.CSSProperties, item?:{ classNames: [ListItemProps\["classNames"\]](/components/list#listitem), styles: [ListItemProps\["styles"\]](/components/list#listitem) } } | - | 5.7.0 |
diff --git a/components/config-provider/index.tsx b/components/config-provider/index.tsx
index 6c2af246aa1e..6336c2e277e7 100644
--- a/components/config-provider/index.tsx
+++ b/components/config-provider/index.tsx
@@ -399,6 +399,7 @@ const ProviderChildren: React.FC<ProviderChildrenProps> = (props) => {
     menu,
     pagination,
     input,
+    inputSearch,
     textArea,
     otp,
     empty,
@@ -498,6 +499,7 @@ const ProviderChildren: React.FC<ProviderChildrenProps> = (props) => {
     steps,
     image,
     input,
+    inputSearch,
     textArea,
     otp,
     layout,
diff --git a/components/config-provider/index.zh-CN.md b/components/config-provider/index.zh-CN.md
index bfe11a4b8059..05efd017ac45 100644
--- a/components/config-provider/index.zh-CN.md
+++ b/components/config-provider/index.zh-CN.md
@@ -140,7 +140,7 @@ const {
 | input | 设置 Input 组件的通用属性 | { autoComplete?: string, className?: string, style?: React.CSSProperties,classNames?:[InputConfig\["classNames"\]](/components/input-cn#semantic-input), styles?: [InputConfig\["styles"\]](/components/input-cn#semantic-input), allowClear?: boolean \| { clearIcon?: ReactNode, disabled?: boolean } } | - | 5.7.0, `allowClear`: 5.15.0, `allowClear.disabled`: 6.4.0 |
 | inputNumber | 设置 Input 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [InputNumberConfig\["classNames"\]](/components/input-number-cn#semantic-dom), styles?: [InputNumberConfig\["styles"\]](/components/input-number-cn#semantic-dom) } | - |  |
 | otp | 设置 OTP 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [OTPConfig\["classNames"\]](/components/input-cn#semantic-otp), styles?: [OTPConfig\["styles"\]](/components/input-cn#semantic-otp) } | - |  |
-| inputSearch | 设置 Search 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [InputSearchConfig\["classNames"\]](/components/input-cn#semantic-search), styles?: [InputSearchConfig\["styles"\]](/components/input-cn#semantic-search) } | - |  |
+| inputSearch | 设置 Search 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [InputSearchConfig\["classNames"\]](/components/input-cn#semantic-search), styles?: [InputSearchConfig\["styles"\]](/components/input-cn#semantic-search), searchIcon?: React.ReactNode } | - | searchIcon: 6.4.0 |
 | textArea | 设置 TextArea 组件的通用属性 | { autoComplete?: string, className?: string, style?: React.CSSProperties,classNames?:[TextAreaConfig\["classNames"\]](/components/input-cn#semantic-textarea), styles?: [TextAreaConfig\["styles"\]](/components/input-cn#semantic-textarea), allowClear?: boolean \| { clearIcon?: ReactNode } } | - | 5.15.0 |
 | layout | 设置 Layout 组件的通用属性 | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
 | list | 设置 List 组件的通用属性 | { className?: string, style?: React.CSSProperties, item?:{ classNames: [ListItemProps\["classNames"\]](/components/list-cn#listitem), styles: [ListItemProps\["styles"\]](/components/list-cn#listitem) } } | - | 5.7.0 |
diff --git a/components/input/Search.tsx b/components/input/Search.tsx
index 23cb7c193bf1..21d8812f51e9 100644
--- a/components/input/Search.tsx
+++ b/components/input/Search.tsx
@@ -5,6 +5,7 @@ import pickAttrs from '@rc-component/util/lib/pickAttrs';
 import { composeRef } from '@rc-component/util/lib/ref';
 import { clsx } from 'clsx';
 
+import fallbackProp from '../_util/fallbackProp';
 import { useMergeSemantic } from '../_util/hooks/useMergeSemantic';
 import type { GenerateSemantic } from '../_util/hooks/useMergeSemantic/semanticType';
 import { cloneElement } from '../_util/reactNode';
@@ -50,6 +51,7 @@ export interface SearchProps extends InputProps {
       source?: 'clear' | 'input';
     },
   ) => void;
+  searchIcon?: React.ReactNode;
   enterButton?: React.ReactNode;
   loading?: boolean;
   onPressEnter?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
@@ -65,6 +67,7 @@ const Search = React.forwardRef<InputRef, SearchProps>((props, ref) => {
     size: customizeSize,
     style,
     enterButton = false,
+    searchIcon: customizeSearchIcon,
     addonAfter,
     loading,
     disabled,
@@ -85,6 +88,7 @@ const Search = React.forwardRef<InputRef, SearchProps>((props, ref) => {
     getPrefixCls,
     classNames: contextClassNames,
     styles: contextStyles,
+    searchIcon: contextSearchIcon,
   } = useComponentConfig('inputSearch');
 
   const mergedProps: SearchProps = {
@@ -145,7 +149,10 @@ const Search = React.forwardRef<InputRef, SearchProps>((props, ref) => {
     onSearch(e);
   };
 
-  const searchIcon = typeof enterButton === 'boolean' ? <SearchOutlined /> : null;
+  const searchIcon =
+    typeof enterButton === 'boolean'
+      ? fallbackProp(customizeSearchIcon, contextSearchIcon, <SearchOutlined />)
+      : null;
   const btnPrefixCls = `${prefixCls}-btn`;
   const btnClassName = clsx(btnPrefixCls, {
     [`${btnPrefixCls}-${variant}`]: variant,
diff --git a/components/input/__tests__/Search.test.tsx b/components/input/__tests__/Search.test.tsx
index a4489745f704..28c4583a84d1 100644
--- a/components/input/__tests__/Search.test.tsx
+++ b/components/input/__tests__/Search.test.tsx
@@ -6,6 +6,7 @@ import focusTest from '../../../tests/shared/focusTest';
 import mountTest from '../../../tests/shared/mountTest';
 import rtlTest from '../../../tests/shared/rtlTest';
 import Button from '../../button';
+import ConfigProvider from '../../config-provider';
 import type { InputRef } from '../Input';
 import Search from '../Search';
 import type { SearchProps } from '../Search';
@@ -358,4 +359,29 @@ describe('Input.Search', () => {
     expect(buttonIcon).toHaveStyle('color: rgb(255, 0, 0)');
     expect(buttonContent).toHaveStyle('color: rgb(0, 255, 0)');
   });
+
+  describe('searchIcon', () => {
+    it('should support custom searchIcon', () => {
+      const { container } = render(<Search searchIcon={<div>bamboo</div>} />);
+      expect(container.querySelector('.ant-input-search-btn')).toHaveTextContent('bamboo');
+    });
+
+    it('should support ConfigProvider searchIcon', () => {
+      const { container } = render(
+        <ConfigProvider inputSearch={{ searchIcon: <div>foobar</div> }}>
+          <Search />
+        </ConfigProvider>,
+      );
+      expect(container.querySelector('.ant-input-search-btn')).toHaveTextContent('foobar');
+    });
+
+    it('should prefer prop searchIcon over ConfigProvider searchIcon', () => {
+      const { container } = render(
+        <ConfigProvider inputSearch={{ searchIcon: <div>foobar</div> }}>
+          <Search searchIcon={<div>bamboo</div>} />
+        </ConfigProvider>,
+      );
+      expect(container.querySelector('.ant-input-search-btn')).toHaveTextContent('bamboo');
+    });
+  });
 });
diff --git a/components/input/index.en-US.md b/components/input/index.en-US.md
index e7aa6426dfaa..d65a4a089f66 100644
--- a/components/input/index.en-US.md
+++ b/components/input/index.en-US.md
@@ -115,6 +115,7 @@ The rest of the props of `Input.TextArea` are the same as the original [textarea
 | loading | Search box with loading | boolean | false |  |
 | onSearch | The callback function triggered when you click on the search-icon, the clear-icon or press the Enter key | function(value, event, { source: "input" \| "clear" }) | - |  |
 | styles | Customize inline style for each semantic structure inside the component. Supports object or function. | Record<[SemanticDOM](#semantic-search), CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-search), CSSProperties> | - |  |
+| searchIcon | Customize the search icon | ReactNode | - | 6.4.0 |
 
 Supports all props of `Input`.
 
diff --git a/components/input/index.zh-CN.md b/components/input/index.zh-CN.md
index acbd0af48ec9..8ce7bb25fb47 100644
--- a/components/input/index.zh-CN.md
+++ b/components/input/index.zh-CN.md
@@ -116,6 +116,7 @@ interface CountConfig {
 | loading | 搜索 loading | boolean | false |  |
 | onSearch | 点击搜索图标、清除图标，或按下回车键时的回调 | function(value, event, { source: "input" \| "clear" }) | - |  |
 | styles | 用于自定义组件内部各语义化结构的行内 style，支持对象或函数 | Record<[SemanticDOM](#semantic-search) , CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-search) , CSSProperties> | - |  |
+| searchIcon | 自定义搜索图标 | ReactNode | - | 6.4.0 |
 
 其余属性和 Input 一致。
 
PATCH_EOF

git apply --whitespace=nowarn /tmp/pr_57256.patch
echo "Patch applied."
