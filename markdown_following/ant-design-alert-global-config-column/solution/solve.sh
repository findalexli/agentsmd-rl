#!/bin/bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency: if the gold patch has already been applied, skip.
if grep -q '(Only supports global configuration) Custom close icon' components/alert/index.en-US.md 2>/dev/null; then
    echo "Gold already applied; nothing to do."
    exit 0
fi

cat > /tmp/gold.patch <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 783a918da81c..019247a21c08 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -37,13 +37,28 @@ ant-design/
 
 ### API 表格格式
 
+英文版：
+
 | Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |
 | --- | --- | --- | --- | --- | --- |
-| disabled | 是否禁用 | boolean | false | - | - |
-| type | 按钮类型 | `primary` \| `default` | `default` | - | - |
+| disabled | Whether the component is disabled | boolean | false | - | × |
+| loadingIcon | (Only supports global configuration) Custom loading icon | ReactNode | - | - | 6.2.0 |
+| type | Button type | `primary` \| `default` | `default` | - | ✔ |
+
+中文版：
 
-- 字符串默认值用反引号，布尔/数字直接写，无默认值用 `-`
-- API 按字母顺序排列，新增属性需声明版本号
+| 参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config) |
+| --- | --- | --- | --- | --- | --- |
+| disabled | 是否禁用 | boolean | false | - | × |
+| loadingIcon | (仅支持全局配置) 自定义加载图标 | ReactNode | - | × | 6.2.0 |
+| type | 按钮类型 | `primary` \| `default` | `default` | - | ✔ |
+
+- 参数：按字母顺序排列
+- 说明：简洁描述参数作用，如果仅支持全局配置需在描述中用括号注明
+- 类型：使用 TypeScript 定义的类型
+- 默认值：字符串用反引号，布尔/数字直接写，无默认值用 `-`
+- 版本：新增属性需声明引入的版本号；上个大版本已存在属性标注 `-`；仅支持全局配置的属性标注 `×`
+- 全局配置：支持全局配置的属性需标注版本号；上个大版本已支持的标注 `✔`；不支持全局配置的属性标注 `×`
 
 ### 文档锚点 ID 规范
 
diff --git a/components/alert/index.en-US.md b/components/alert/index.en-US.md
index d6ca0dd50730..a90e0a79ccc6 100644
--- a/components/alert/index.en-US.md
+++ b/components/alert/index.en-US.md
@@ -37,21 +37,26 @@ group:
 
 Common props ref：[Common props](/docs/react/common-props)
 
-| Property | Description | Type | Default | Version |
-| --- | --- | --- | --- | --- |
-| action | The action of Alert | ReactNode | - | 4.9.0 |
-| ~~afterClose~~ | Called when close animation is finished, please use `closable.afterClose` instead | () => void | - |  |
-| banner | Whether to show as banner | boolean | false |  |
-| classNames | Customize class for each semantic structure inside the component. Supports object or function | Record<[SemanticDOM](#semantic-dom), string> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), string> | - |  |
-| closable | The config of closable, >=5.15.0: support `aria-*` | boolean \| [ClosableType](#closabletype) & React.AriaAttributes | `false` |  |
-| description | Additional content of Alert | ReactNode | - |  |
-| icon | Custom icon, effective when `showIcon` is true | ReactNode | - |  |
-| ~~message~~ | Content of Alert, please use `title` instead | ReactNode | - |  |
-| title | Content of Alert | ReactNode | - |  |
-| showIcon | Whether to show icon | boolean | false, in `banner` mode default is true |  |
-| styles | Customize inline style for each semantic structure inside the component. Supports object or function | Record<[SemanticDOM](#semantic-dom), CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), CSSProperties> | - |  |
-| type | Type of Alert styles, options: `success`, `info`, `warning`, `error` | string | `info`, in `banner` mode default is `warning` |  |
-| ~~onClose~~ | Callback when Alert is closed, please use `closable.onClose` instead | (e: MouseEvent) => void | - |  |
+| Property | Description | Type | Default | Version | [Global Config](/components/config-provider#component-config) |
+| --- | --- | --- | --- | --- | --- |
+| action | The action of Alert | ReactNode | - |  | × |
+| ~~afterClose~~ | Called when close animation is finished, please use `closable.afterClose` instead | () => void | - |  | × |
+| banner | Whether to show as banner | boolean | false |  | × |
+| classNames | Customize class for each semantic structure inside the component. Supports object or function | Record<[SemanticDOM](#semantic-dom), string> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), string> | - |  | 6.0.0 |
+| closable | The config of closable | boolean \| [ClosableType](#closabletype) & React.AriaAttributes | `false` |  | ✔ |
+| closeIcon | (Only supports global configuration) Custom close icon | ReactNode | - | × | 6.3.0 |
+| description | Additional content of Alert | ReactNode | - |  | × |
+| errorIcon | (Only supports global configuration) Custom error icon in Alert icon | ReactNode | - | × | 6.2.0 |
+| icon | Custom icon, effective when `showIcon` is true | ReactNode | - |  | × |
+| infoIcon | (Only supports global configuration) Custom info icon in Alert icon | ReactNode | - | × | 6.2.0 |
+| ~~message~~ | Content of Alert, please use `title` instead | ReactNode | - |  | × |
+| ~~onClose~~ | Callback when Alert is closed, please use `closable.onClose` instead | (e: MouseEvent) => void | - |  | × |
+| showIcon | Whether to show icon | boolean | false, in `banner` mode default is true |  | × |
+| styles | Customize inline style for each semantic structure inside the component. Supports object or function | Record<[SemanticDOM](#semantic-dom), CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), CSSProperties> | - |  | 6.0.0 |
+| successIcon | (Only supports global configuration) Custom success icon in Alert icon | ReactNode | - | × | 6.2.0 |
+| title | Content of Alert | ReactNode | - |  | × |
+| type | Type of Alert styles, options: `success`, `info`, `warning`, `error` | string | `info`, in `banner` mode default is `warning` |  | × |
+| warningIcon | (Only supports global configuration) Custom warning icon in Alert icon | ReactNode | - | × | 6.2.0 |
 
 ### ClosableType
 
diff --git a/components/alert/index.zh-CN.md b/components/alert/index.zh-CN.md
index 4f69cbf72ab5..971866a7a4e8 100644
--- a/components/alert/index.zh-CN.md
+++ b/components/alert/index.zh-CN.md
@@ -38,21 +38,26 @@ group:
 
 通用属性参考：[通用属性](/docs/react/common-props)
 
-| 参数 | 说明 | 类型 | 默认值 | 版本 |
-| --- | --- | --- | --- | --- |
-| action | 自定义操作项 | ReactNode | - | 4.9.0 |
-| ~~afterClose~~ | 关闭动画结束后触发的回调函数，请使用 `closable.afterClose` 替换 | () => void | - |  |
-| banner | 是否用作顶部公告 | boolean | false |  |
-| classNames | 自定义组件内部各语义化结构的类名。支持对象或函数 | Record<[SemanticDOM](#semantic-dom), string> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), string> | - |  |
-| closable | 可关闭配置，>=5.15.0: 支持 `aria-*` | boolean \| [ClosableType](#closabletype) & React.AriaAttributes | `false` |  |
-| description | 警告提示的辅助性文字介绍 | ReactNode | - |  |
-| icon | 自定义图标，`showIcon` 为 true 时有效 | ReactNode | - |  |
-| ~~message~~ | 警告提示内容，请使用 `title` 替换 | ReactNode | - |  |
-| title | 警告提示内容 | ReactNode | - |  |
-| showIcon | 是否显示辅助图标 | boolean | false，`banner` 模式下默认值为 true |  |
-| styles | 自定义组件内部各语义化结构的内联样式。支持对象或函数 | Record<[SemanticDOM](#semantic-dom), CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), CSSProperties> | - |  |
-| type | 指定警告提示的样式，有四种选择 `success`、`info`、`warning`、`error` | string | `info`，`banner` 模式下默认值为 `warning` |  |
-| ~~onClose~~ | 关闭时触发的回调函数，请使用 `closable.onClose` 替换 | (e: MouseEvent) => void | - |  |
+| 参数 | 说明 | 类型 | 默认值 | 版本 | [全局配置](/components/config-provider-cn#component-config) |
+| --- | --- | --- | --- | --- | --- |
+| action | 自定义操作项 | ReactNode | - |  | × |
+| ~~afterClose~~ | 关闭动画结束后触发的回调函数，请使用 `closable.afterClose` 替换 | () => void | - |  | × |
+| banner | 是否用作顶部公告 | boolean | false |  | × |
+| classNames | 自定义组件内部各语义化结构的类名。支持对象或函数 | Record<[SemanticDOM](#semantic-dom), string> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), string> | - |  | 6.0.0 |
+| closable | 可关闭配置 | boolean \| [ClosableType](#closabletype) & React.AriaAttributes | `false` |  | ✔ |
+| closeIcon | （仅支持全局配置）自定义关闭图标 | ReactNode | - | × | 6.3.0 |
+| description | 警告提示的辅助性文字介绍 | ReactNode | - |  | × |
+| errorIcon | （仅支持全局配置）自定义错误图标 | ReactNode | - | × | 6.2.0 |
+| icon | 自定义图标，`showIcon` 为 true 时有效 | ReactNode | - |  | × |
+| infoIcon | （仅支持全局配置）自定义信息图标 | ReactNode | - | × | 6.2.0 |
+| ~~message~~ | 警告提示内容，请使用 `title` 替换 | ReactNode | - |  | × |
+| ~~onClose~~ | 关闭时触发的回调函数，请使用 `closable.onClose` 替换 | (e: MouseEvent) => void | - |  | × |
+| showIcon | 是否显示辅助图标 | boolean | false，`banner` 模式下默认值为 true |  | × |
+| styles | 自定义组件内部各语义化结构的内联样式。支持对象或函数 | Record<[SemanticDOM](#semantic-dom), CSSProperties> \| (info: { props }) => Record<[SemanticDOM](#semantic-dom), CSSProperties> | - |  | 6.0.0 |
+| successIcon | （仅支持全局配置）自定义成功图标 | ReactNode | - | × | 6.2.0 |
+| title | 警告提示内容 | ReactNode | - |  | × |
+| type | 指定警告提示的样式，有四种选择 `success`、`info`、`warning`、`error` | string | `info`，`banner` 模式下默认值为 `warning` |  | × |
+| warningIcon | （仅支持全局配置）自定义警告图标 | ReactNode | - | × | 6.2.0 |
 
 ### ClosableType
 
diff --git a/components/config-provider/index.en-US.md b/components/config-provider/index.en-US.md
index 15404bac82f0..2c822fe3f8e5 100644
--- a/components/config-provider/index.en-US.md
+++ b/components/config-provider/index.en-US.md
@@ -109,7 +109,7 @@ const {
 | Property | Description | Type | Default | Version |
 | --- | --- | --- | --- | --- |
 | affix | Set Affix common props | { className?: string, style?: React.CSSProperties } | - | 6.0.0 |
-| alert | Set Alert common props | { className?: string, style?: React.CSSProperties, closeIcon?: React.ReactNode, successIcon?: React.ReactNode, infoIcon?: React.ReactNode, warningIcon?: React.ReactNode, errorIcon?: React.ReactNode } | - | 5.7.0, `closeIcon`: 5.14.0, `successIcon`, `infoIcon`, `warningIcon` and `errorIcon`: 6.2.0 |
+| alert | Set Alert common props | See [Alert](/components/alert#api) | - | 5.7.0 |
 | anchor | Set Anchor common props | { className?: string, style?: React.CSSProperties, classNames?: [AnchorStyleConfig\["classNames"\]](/components/anchor#semantic-dom), styles?: [AnchorStyleConfig\["styles"\]](/components/anchor#semantic-dom) } | - | 5.7.0, `classNames` and `styles`: 6.0.0 |
 | avatar | Set Avatar common props | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
 | badge | Set Badge common props | { className?: string, style?: React.CSSProperties, classNames?: [BadgeProps\["classNames"\]](/components/badge#semantic-dom), styles?: [BadgeProps\["styles"\]](/components/badge#semantic-dom) } | - | 5.7.0 |
diff --git a/components/config-provider/index.zh-CN.md b/components/config-provider/index.zh-CN.md
index 69497154aea8..369c4f73ba48 100644
--- a/components/config-provider/index.zh-CN.md
+++ b/components/config-provider/index.zh-CN.md
@@ -111,7 +111,7 @@ const {
 | 参数 | 说明 | 类型 | 默认值 | 版本 |
 | --- | --- | --- | --- | --- |
 | affix | 设置 Affix 组件的通用属性 | { className?: string, style?: React.CSSProperties } | - | 6.0.0 |
-| alert | 设置 Alert 组件的通用属性 | { className?: string, style?: React.CSSProperties, closeIcon?: React.ReactNode, successIcon?: React.ReactNode, infoIcon?: React.ReactNode, warningIcon?: React.ReactNode, errorIcon?: React.ReactNode } | - | 5.7.0, `closeIcon`: 5.14.0, `successIcon`, `infoIcon`, `warningIcon` 和 `errorIcon`: 6.2.0 |
+| alert | 设置 Alert 组件的通用属性 | 参见 [Alert](/components/alert-cn#api) | - | 5.7.0 |
 | anchor | 设置 Anchor 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [AnchorStyleConfig\["classNames"\]](/components/anchor-cn#semantic-dom), styles?: [AnchorStyleConfig\["styles"\]](/components/anchor-cn#semantic-dom) } | - | 5.7.0, `classNames` 和 `styles`: 6.0.0 |
 | avatar | 设置 Avatar 组件的通用属性 | { className?: string, style?: React.CSSProperties } | - | 5.7.0 |
 | badge | 设置 Badge 组件的通用属性 | { className?: string, style?: React.CSSProperties, classNames?: [BadgeProps\["classNames"\]](/components/badge-cn#semantic-dom), styles?: [BadgeProps\["styles"\]](/components/badge-cn#semantic-dom) } | - | 5.7.0 |
PATCH

git apply --whitespace=nowarn /tmp/gold.patch
echo "Gold patch applied."
