#!/bin/bash
set -e

cd /workspace/antd

# Idempotency check - if patch already applied, exit
if grep -q "popupMenuColumnStyle: 'styles.popup.listItem'" components/cascader/index.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/components/cascader/__tests__/index.test.tsx b/components/cascader/__tests__/index.test.tsx
index 9a266a4ac952..3ba8525c0e85 100644
--- a/components/cascader/__tests__/index.test.tsx
+++ b/components/cascader/__tests__/index.test.tsx
@@ -613,7 +613,7 @@ describe('Cascader', () => {
         />,
       );
       expect(errSpy).toHaveBeenCalledWith(
-        'Warning: [antd: Cascader] `dropdownMenuColumnStyle` is deprecated. Please use `popupMenuColumnStyle` instead.',
+        'Warning: [antd: Cascader] `dropdownMenuColumnStyle` is deprecated. Please use `styles.popup.listItem` instead.',
       );
       const menuColumn = getByRole('menuitemcheckbox');
       expect(menuColumn).toHaveStyle({ padding: '10px' });
@@ -621,6 +621,46 @@ describe('Cascader', () => {
       errSpy.mockRestore();
     });

+    it('deprecated popupMenuColumnStyle', () => {
+      resetWarned();
+
+      const errSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
+
+      const { getByRole } = render(
+        <Cascader
+          options={[{ label: 'test', value: 1 }]}
+          popupMenuColumnStyle={{ padding: 10 }}
+          open
+        />,
+      );
+      expect(errSpy).toHaveBeenCalledWith(
+        'Warning: [antd: Cascader] `popupMenuColumnStyle` is deprecated. Please use `styles.popup.listItem` instead.',
+      );
+      const menuColumn = getByRole('menuitemcheckbox');
+      expect(menuColumn).toHaveStyle({ padding: '10px' });
+
+      errSpy.mockRestore();
+    });
+
+    it('styles.popup.listItem should override popupMenuColumnStyle', () => {
+      resetWarned();
+
+      const errSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
+
+      const { getByRole } = render(
+        <Cascader
+          options={[{ label: 'test', value: 1 }]}
+          popupMenuColumnStyle={{ padding: 10 }}
+          styles={{ popup: { listItem: { padding: 20 } } }}
+          open
+        />,
+      );
+
+      expect(getByRole('menuitemcheckbox')).toHaveStyle({ padding: '20px' });
+
+      errSpy.mockRestore();
+    });
+
     it('legacy onDropdownVisibleChange', () => {
       resetWarned();

diff --git a/components/cascader/index.en-US.md b/components/cascader/index.en-US.md
index e1fc9b3065fd..74c6d0b5c759 100644
--- a/components/cascader/index.en-US.md
+++ b/components/cascader/index.en-US.md
@@ -95,8 +95,8 @@ Common props ref：[Common props](/docs/react/common-props)
 | showCheckedStrategy | The way to show selected items in the box (only effective when `multiple` is `true`). `Cascader.SHOW_CHILD`: just show child treeNode. `Cascader.SHOW_PARENT`: just show parent treeNode (when all child treeNode under the parent treeNode are checked) | `Cascader.SHOW_PARENT` \| `Cascader.SHOW_CHILD` | `Cascader.SHOW_PARENT` | 4.20.0 |
 | ~~searchValue~~ | Set search value, Need work with `showSearch` | string | - | 4.17.0 |
 | ~~onSearch~~ | The callback function triggered when input changed | (search: string) => void | - | 4.17.0 |
-| ~~dropdownMenuColumnStyle~~ | The style of the drop-down menu column, use `popupMenuColumnStyle` instead | CSSProperties | - |  |
-| popupMenuColumnStyle | The style of the drop-down menu column | CSSProperties | - |  |
+| ~~dropdownMenuColumnStyle~~ | The style of the drop-down menu column, use `styles.popup.listItem` instead | CSSProperties | - |  |
+| ~~popupMenuColumnStyle~~ | The style of the drop-down menu column, use `styles.popup.listItem` instead | CSSProperties | - |  |
 | optionRender | Customize the rendering dropdown options | (option: Option) => React.ReactNode | - | 5.16.0 |

 ### showSearch
diff --git a/components/cascader/index.tsx b/components/cascader/index.tsx
index 98ca2418ec8e..39a5d6ac8765 100644
--- a/components/cascader/index.tsx
+++ b/components/cascader/index.tsx
@@ -179,8 +179,9 @@ export interface CascaderProps<
   /** @deprecated Please use `popupRender` instead */
   dropdownRender?: (menu: React.ReactElement) => React.ReactElement;
   popupRender?: (menu: React.ReactElement) => React.ReactElement;
-  /** @deprecated Please use `popupMenuColumnStyle` instead */
+  /** @deprecated Please use `styles.popup.listItem` instead */
   dropdownMenuColumnStyle?: React.CSSProperties;
+  /** @deprecated Please use `styles.popup.listItem` instead */
   popupMenuColumnStyle?: React.CSSProperties;
   /** @deprecated Please use `onOpenChange` instead */
   onDropdownVisibleChange?: (visible: boolean) => void;
@@ -280,7 +281,8 @@ const Cascader = React.forwardRef<CascaderRef, CascaderProps<any>>((props, ref)
       dropdownClassName: 'classNames.popup.root',
       dropdownStyle: 'styles.popup.root',
       dropdownRender: 'popupRender',
-      dropdownMenuColumnStyle: 'popupMenuColumnStyle',
+      dropdownMenuColumnStyle: 'styles.popup.listItem',
+      popupMenuColumnStyle: 'styles.popup.listItem',
       onDropdownVisibleChange: 'onOpenChange',
       onPopupVisibleChange: 'onOpenChange',
       bordered: 'variant',
diff --git a/components/cascader/index.zh-CN.md b/components/cascader/index.zh-CN.md
index ea8b1368e2c9..8fb0f76590a1 100644
--- a/components/cascader/index.zh-CN.md
+++ b/components/cascader/index.zh-CN.md
@@ -96,8 +96,8 @@ demo:
 | removeIcon | 自定义的多选框清除图标 | ReactNode | - |  |
 | ~searchValue~ | 设置搜索的值，需要与 `showSearch` 配合使用 | string | - | 4.17.0 |
 | ~onSearch~ | 监听搜索，返回输入的值 | (search: string) => void | - | 4.17.0 |
-| ~~dropdownMenuColumnStyle~~ | 下拉菜单列的样式，请使用 `popupMenuColumnStyle` 替换 | CSSProperties | - |  |
-| popupMenuColumnStyle | 下拉菜单列的样式 | CSSProperties | - |  |
+| ~~dropdownMenuColumnStyle~~ | 下拉菜单列的样式，请使用 `styles.popup.listItem` 替换 | CSSProperties | - |  |
+| ~~popupMenuColumnStyle~~ | 下拉菜单列的样式，请使用 `styles.popup.listItem` 替换 | CSSProperties | - |  |
 | optionRender | 自定义渲染下拉选项 | (option: Option) => React.ReactNode | - | 5.16.0 |

 ### showSearch
diff --git a/docs/react/migration-v6.en-US.md b/docs/react/migration-v6.en-US.md
index 335fc407d050..98caae7b7430 100644
--- a/docs/react/migration-v6.en-US.md
+++ b/docs/react/migration-v6.en-US.md
@@ -114,7 +114,7 @@ If you encounter build errors during the upgrade, please verify that your `@ant-
   - `dropdownClassName` is deprecated and replaced by `classNames.popup.root`.
   - `dropdownStyle` is deprecated and replaced by `styles.popup.root`.
   - `dropdownRender` is deprecated and replaced by `popupRender`.
-  - `dropdownMenuColumnStyle` is deprecated and replaced by `popupMenuColumnStyle`.
+  - `dropdownMenuColumnStyle` is deprecated and replaced by `styles.popup.listItem`.
   - `onDropdownVisibleChange` is deprecated and replaced by `onOpenChange`.
   - `onPopupVisibleChange` is deprecated and replaced by `onOpenChange`.
   - `bordered` is deprecated and replaced by `variant`.
diff --git a/docs/react/migration-v6.zh-CN.md b/docs/react/migration-v6.zh-CN.md
index ca9c3c77fa1f..df28ecfab565 100644
--- a/docs/react/migration-v6.zh-CN.md
+++ b/docs/react/migration-v6.zh-CN.md
@@ -112,7 +112,7 @@ pnpm add @ant-design/icons@6
   - `dropdownClassName` 弃用，变为 `classNames.popup.root`。
   - `dropdownStyle` 弃用，变为 `styles.popup.root`。
   - `dropdownRender` 弃用，变为 `popupRender`。
-  - `dropdownMenuColumnStyle` 弃用，变为 `popupMenuColumnStyle`。
+  - `dropdownMenuColumnStyle` 弃用，变为 `styles.popup.listItem`。
   - `onDropdownVisibleChange` 弃用，变为 `onOpenChange`。
   - `onPopupVisibleChange` 弃用，变为 `onOpenChange`。
   - `bordered` 弃用，变为 `variant`。
PATCH

echo "Patch applied successfully"
