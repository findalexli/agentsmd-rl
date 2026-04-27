#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard — if a distinctive line from the gold patch is already present, exit.
if grep -qF '列说明：' CLAUDE.md 2>/dev/null && \
   grep -qF '[Global Config](/components/config-provider#component-config)' components/affix/index.en-US.md 2>/dev/null; then
    echo "Already patched; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 6b0824d1241b..9d766bbf122b 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -71,7 +71,9 @@ ant-design/
 | loadingIcon | (仅支持全局配置) 自定义加载图标 | ReactNode | - | × | 6.2.0 |
 | type | 按钮类型 | `primary` \| `default` | `default` | - | ✔ |

-- 参数：按字母顺序排列
+列说明：
+
+- 参数：按字母顺序排列，忽略 className, style, onClick, onKeyDown 等通用属性, onChange, onClick 等事件回调放在最后
 - 说明：简洁描述参数作用，如果仅支持全局配置需在描述中用括号注明
 - 类型：使用 TypeScript 定义的类型
 - 默认值：字符串用反引号，布尔/数字直接写，无默认值用 `-`
diff --git a/components/affix/index.en-US.md b/components/affix/index.en-US.md
index 773f206821a7..5d8ac356cfc3 100644
--- a/components/affix/index.en-US.md
+++ b/components/affix/index.en-US.md
@@ -33,12 +33,12 @@ Please note that Affix should not cover other content on the page, especially wh

 Common props ref：[Common props](/docs/react/common-props)

-| Property | Description | Type | Default |
-| --- | --- | --- | --- |
-| offsetBottom | Offset from the bottom of the viewport (in pixels) | number | - |
-| offsetTop | Offset from the top of the viewport (in pixels) | number | 0 |
-| target | Specifies the scrollable area DOM node | () => HTMLElement | () => window |
-| onChange | Callback for when Affix state is changed | (affixed?: boolean) => void | - |
+| Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |
+| --- | --- | --- | --- | --- | --- |
+| offsetBottom | Offset from the bottom of the viewport (in pixels) | number | - |  | × |
+| offsetTop | Offset from the top of the viewport (in pixels) | number | 0 |  | × |
+| target | Specifies the scrollable area DOM node | () => Window \| HTMLElement \| null | () => window |  | × |
+| onChange | Callback for when Affix state is changed | (affixed?: boolean) => void | - |  | × |

 **Note:** Children of `Affix` must not have the property `position: absolute`, but you can set `position: absolute` on `Affix` itself:

diff --git a/components/affix/index.zh-CN.md b/components/affix/index.zh-CN.md
index 310b073b2e3d..aeb7dbf82b18 100644
--- a/components/affix/index.zh-CN.md
+++ b/components/affix/index.zh-CN.md
@@ -34,12 +34,12 @@ group:

 通用属性参考：[通用属性](/docs/react/common-props)

-| 参数 | 说明 | 类型 | 默认值 |
-| --- | --- | --- | --- |
-| offsetBottom | 距离窗口底部达到指定偏移量后触发 | number | - |
-| offsetTop | 距离窗口顶部达到指定偏移量后触发 | number | 0 |
-| target | 设置 `Affix` 需要监听其滚动事件的元素，值为一个返回对应 DOM 元素的函数 | () => HTMLElement | () => window |
-| onChange | 固定状态改变时触发的回调函数 | (affixed?: boolean) => void | - |
+| 参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config) |
+| --- | --- | --- | --- | --- | --- |
+| offsetBottom | 距离窗口底部达到指定偏移量后触发 | number | - |  | × |
+| offsetTop | 距离窗口顶部达到指定偏移量后触发 | number | 0 |  | × |
+| target | 设置 `Affix` 需要监听其滚动事件的元素，值为一个返回对应 DOM 元素的函数 | () => Window \| HTMLElement \| null | () => window |  | × |
+| onChange | 固定状态改变时触发的回调函数 | (affixed?: boolean) => void | - |  | × |

 **注意：**`Affix` 内的元素不要使用绝对定位，如需要绝对定位的效果，可以直接设置 `Affix` 为绝对定位：

diff --git a/components/config-provider/index.en-US.md b/components/config-provider/index.en-US.md
index 4bcc2a7323d0..5a36cb126073 100644
--- a/components/config-provider/index.en-US.md
+++ b/components/config-provider/index.en-US.md
@@ -110,7 +110,7 @@ const {

 | Property | Description | Type | Default | Version |
 | --- | --- | --- | --- | --- |
-| affix | Set Affix common props | { className?: string, style?: React.CSSProperties } | - | 6.0.0 |
+| affix | Set Affix common props | See [Affix](/components/affix#api) | - | 6.0.0 |
 | alert | Set Alert common props | See [Alert](/components/alert#api) | - | 5.7.0 |
 | anchor | Set Anchor common props | { className?: string, style?: React.CSSProperties, classNames?: [AnchorStyleConfig\["classNames"\]](/components/anchor#semantic-dom), styles?: [AnchorStyleConfig\["styles"\]](/components/anchor#semantic-dom) } | - | 5.7.0, `classNames` and `styles`: 6.0.0 |
 | avatar | Set Avatar common props | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
diff --git a/components/config-provider/index.zh-CN.md b/components/config-provider/index.zh-CN.md
index 3005c1158abc..3c1cc015938c 100644
--- a/components/config-provider/index.zh-CN.md
+++ b/components/config-provider/index.zh-CN.md
@@ -112,7 +112,7 @@ const {

 | 参数 | 说明 | 类型 | 默认值 | 版本 |
 | --- | --- | --- | --- | --- |
-| affix | 设置 Affix 组件的通用属性 | { className?: string, style?: React.CSSProperties } | - | 6.0.0 |
+| affix | 设置 Affix 组件的通用属性 | 参见 [Affix](/components/affix-cn#api) | - | 6.0.0 |
 | alert | 设置 Alert 组件的通用属性 | 参见 [Alert](/components/alert-cn#api) | - | 5.7.0 |
 | anchor | 设置 Anchor 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [AnchorStyleConfig\["classNames"\]](/components/anchor-cn#semantic-dom), styles?: [AnchorStyleConfig\["styles"\]](/components/anchor-cn#semantic-dom) } | - | 5.7.0, `classNames` 和 `styles`: 6.0.0 |
 | avatar | 设置 Avatar 组件的通用属性 | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
PATCH

echo "Patch applied."
