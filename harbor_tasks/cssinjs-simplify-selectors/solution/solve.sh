#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/collapse/style/index.ts b/components/collapse/style/index.ts
index 13a87a46bc2d..180e5019aba1 100644
--- a/components/collapse/style/index.ts
+++ b/components/collapse/style/index.ts
@@ -245,10 +245,7 @@ export const genBaseStyle: GenerateStyle<CollapseToken, CSSObject> = (token) =>
       },

       [`& ${componentCls}-item-disabled > ${componentCls}-header`]: {
-        [`
-          &,
-          & > .arrow
-        `]: {
+        '&, & > .arrow': {
           color: colorTextDisabled,
           cursor: 'not-allowed',
         },
diff --git a/components/date-picker/style/panel.ts b/components/date-picker/style/panel.ts
index 8f3341337572..6db8dc671f5c 100644
--- a/components/date-picker/style/panel.ts
+++ b/components/date-picker/style/panel.ts
@@ -230,17 +230,12 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token)
       // ========================================================
       // =                     Shared Panel                     =
       // ========================================================
-      [`&-decade-panel,
-        &-year-panel,
-        &-quarter-panel,
-        &-month-panel,
-        &-week-panel,
-        &-date-panel,
-        &-time-panel`]: {
-        display: 'flex',
-        flexDirection: 'column',
-        width: pickerPanelWidth,
-      },
+      '&-decade-panel, &-year-panel, &-quarter-panel, &-month-panel, &-week-panel, &-date-panel, &-time-panel':
+        {
+          display: 'flex',
+          flexDirection: 'column',
+          width: pickerPanelWidth,
+        },

       // ======================= Header =======================
       '&-header': {
@@ -306,10 +301,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token)
         },
       },
       // Arrow button
-      [`&-prev-icon,
-        &-next-icon,
-        &-super-prev-icon,
-        &-super-next-icon`]: {
+      '&-prev-icon, &-next-icon, &-super-prev-icon, &-super-next-icon': {
         position: 'relative',
         width: pickerControlIconSize,
         height: pickerControlIconSize,
@@ -327,8 +319,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token
         },
       },

-      [`&-super-prev-icon,
-        &-super-next-icon`]: {
+      '&-super-prev-icon, &-super-next-icon': {
         '&::after': {
           position: 'absolute',
           top: pickerControlIconMargin,
@@ -383,10 +374,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token
         ...genPickerCellInnerStyle(token),
       },

-      [`&-decade-panel,
-        &-year-panel,
-        &-quarter-panel,
-        &-month-panel`]: {
+      '&-decade-panel, &-year-panel, &-quarter-panel, &-month-panel': {
         [`${componentCls}-content`]: {
           height: token.calc(withoutTimeCellHeight).mul(4).equal(),
         },
@@ -418,9 +406,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token
       },

       // ============= Year & Quarter & Month Panel =============
-      [`&-year-panel,
-        &-quarter-panel,
-        &-month-panel`]: {
+      '&-year-panel, &-quarter-panel, &-month-panel': {
         [`${componentCls}-body`]: {
           padding: `0 ${unit(paddingXS)}`,
         },
diff --git a/components/dropdown/style/index.ts b/components/dropdown/style/index.ts
index baaf75fc118c..f3cef8350970 100644
--- a/components/dropdown/style/index.ts
+++ b/components/dropdown/style/index.ts
@@ -126,11 +126,7 @@ const genBaseStyle: GenerateStyle<DropdownToken> = (token) => {
           },
         },

-        [`
-        &-hidden,
-        &-menu-hidden,
-        &-menu-submenu-hidden
-      `]: {
+        '&-hidden, &-menu-hidden, &-menu-submenu-hidden': {
           display: 'none',
         },

diff --git a/components/form/style/index.ts b/components/form/style/index.ts
index 162bbfbe0c23..6e9fe419996c 100644
--- a/components/form/style/index.ts
+++ b/components/form/style/index.ts
@@ -123,9 +123,7 @@ const resetForm: GenerateStyle<AliasToken, CSSObject> = (token) => ({
   },

   // Focus for file, radio, and checkbox
-  [`input[type='file']:focus,
-  input[type='radio']:focus,
-  input[type='checkbox']:focus`]: {
+  "input[type='file']:focus, input[type='radio']:focus, input[type='checkbox']:focus": {
     outline: 0,
     boxShadow: `0 0 0 ${unit(token.controlOutlineWidth)} ${token.controlOutline}`,
   },
diff --git a/components/menu/style/index.ts b/components/menu/style/index.ts
index 5a7a133eab13..6dd5d9759256 100644
--- a/components/menu/style/index.ts
+++ b/components/menu/style/index.ts
@@ -743,59 +743,35 @@ const getBaseStyle: GenerateStyle<MenuToken> = (token) => {
             },
           },

-          [`
-          &-placement-leftTop,
-          &-placement-bottomRight,
-          `]: {
+          '&-placement-leftTop, &-placement-bottomRight': {
             transformOrigin: '100% 0',
           },

-          [`
-          &-placement-leftBottom,
-          &-placement-topRight,
-          `]: {
+          '&-placement-leftBottom, &-placement-topRight': {
             transformOrigin: '100% 100%',
           },

-          [`
-          &-placement-rightBottom,
-          &-placement-topLeft,
-          `]: {
+          '&-placement-rightBottom, &-placement-topLeft': {
             transformOrigin: '0 100%',
           },

-          [`
-          &-placement-bottomLeft,
-          &-placement-rightTop,
-          `]: {
+          '&-placement-bottomLeft, &-placement-rightTop': {
             transformOrigin: '0 0',
           },

-          [`
-          &-placement-leftTop,
-          &-placement-leftBottom
-          `]: {
+          '&-placement-leftTop, &-placement-leftBottom': {
             paddingInlineEnd: token.paddingXS,
           },

-          [`
-          &-placement-rightTop,
-          &-placement-rightBottom
-          `]: {
+          '&-placement-rightTop, &-placement-rightBottom': {
             paddingInlineStart: token.paddingXS,
           },

-          [`
-          &-placement-topRight,
-          &-placement-topLeft
-          `]: {
+          '&-placement-topRight, &-placement-topLeft': {
             paddingBottom: token.paddingXS,
           },

-          [`
-          &-placement-bottomRight,
-          &-placement-bottomLeft
-          `]: {
+          '&-placement-bottomRight, &-placement-bottomLeft': {
             paddingTop: token.paddingXS,
           },
         },
diff --git a/components/table/style/bordered.ts b/components/table/style/bordered.ts
index 6cfcc53f671c..896fefc2e7a6 100644
--- a/components/table/style/bordered.ts
+++ b/components/table/style/bordered.ts
@@ -25,10 +25,7 @@ const genBorderedStyle: GenerateStyle<TableToken, CSSObject> = (token) => {
     [`&${componentCls}-${size}`]: {
       [`> ${componentCls}-container`]: {
         [`> ${componentCls}-content, > ${componentCls}-body`]: {
-          [`
-            > table > tbody > tr > th,
-            > table > tbody > tr > td
-          `]: {
+          '> table > tbody > tr > th, > table > tbody > tr > td': {
             [`> ${componentCls}-expanded-row-fixed`]: {
               margin: `${unit(calc(paddingVertical).mul(-1).equal())}
               ${unit(calc(calc(paddingHorizontal).add(lineWidth)).mul(-1).equal())}`,
@@ -53,68 +50,51 @@ const genBorderedStyle: GenerateStyle<TableToken, CSSObject> = (token) => {
           borderInlineStart: tableBorder,
           borderTop: tableBorder,

-          [`
-            > ${componentCls}-content,
-            > ${componentCls}-header,
-            > ${componentCls}-body,
-            > ${componentCls}-summary
-          `]: {
-            '> table': {
-              // ============================= Cell =============================
-              [`
-                > thead > tr > th,
-                > thead > tr > td,
-                > tbody > tr > th,
-                > tbody > tr > td,
-                > tfoot > tr > th,
-                > tfoot > tr > td
-              `]: {
-                borderInlineEnd: tableBorder,
-              },
+          [`> ${componentCls}-content, > ${componentCls}-header, > ${componentCls}-body, > ${componentCls}-summary`]:
+            {
+              '> table': {
+                // ============================= Cell =============================
+                '> thead > tr > th, > thead > tr > td, > tbody > tr > th, > tbody > tr > td, > tfoot > tr > th, > tfoot > tr > td':
+                  {
+                    borderInlineEnd: tableBorder,
+                  },

-              // ============================ Header ============================
-              '> thead': {
-                '> tr:not(:last-child) > th': {
-                  borderBottom: tableBorder,
-                },
+                // ============================ Header ============================
+                '> thead': {
+                  '> tr:not(:last-child) > th': {
+                    borderBottom: tableBorder,
+                  },

-                '> tr > th::before': {
-                  backgroundColor: 'transparent !important',
+                  '> tr > th::before': {
+                    backgroundColor: 'transparent !important',
+                  },
                 },
-              },

-              // Fixed right should provides additional border
-              [`
-                > thead > tr,
-                > tbody > tr,
-                > tfoot > tr
-              `]: {
-                [`> ${componentCls}-cell-fix-right-first::after`]: {
-                  borderInlineEnd: tableBorder,
+                // Fixed right should provides additional border
+                '> thead > tr, > tbody > tr, > tfoot > tr': {
+                  [`> ${componentCls}-cell-fix-right-first::after`]: {
+                    borderInlineEnd: tableBorder,
+                  },
                 },
-              },

-              // ========================== Expandable ==========================
-              [`
-                > tbody > tr > th,
-                > tbody > tr > td
-              `]: {
-                [`> ${componentCls}-expanded-row-fixed`]: {
-                  margin: `${unit(calc(tablePaddingVertical).mul(-1).equal())} ${unit(
-                    calc(calc(tablePaddingHorizontal).add(lineWidth)).mul(-1).equal(),
-                  )}`,
-                  '&::after': {
-                    position: 'absolute',
-                    top: 0,
-                    insetInlineEnd: lineWidth,
-                    bottom: 0,
-                    borderInlineEnd: tableBorder,
-                    content: '""',
+                // ========================== Expandable ==========================
+                '> tbody > tr > th, > tbody > tr > td': {
+                  [`> ${componentCls}-expanded-row-fixed`]: {
+                    margin: `${unit(calc(tablePaddingVertical).mul(-1).equal())} ${unit(
+                      calc(calc(tablePaddingHorizontal).add(lineWidth)).mul(-1).equal(),
+                    )}`,
+                    '&::after': {
+                      position: 'absolute',
+                      top: 0,
+                      insetInlineEnd: lineWidth,
+                      bottom: 0,
+                      borderInlineEnd: tableBorder,
+                      content: '""',
+                    },
                   },
                 },
               },
             },
-          },
         },

         // ============================ Scroll ============================
diff --git a/components/table/style/empty.ts b/components/table/style/empty.ts
index 63461903f209..2e4f1987af93 100644
--- a/components/table/style/empty.ts
+++ b/components/table/style/empty.ts
@@ -12,10 +12,7 @@ const genEmptyStyle: GenerateStyle<TableToken, CSSObject> = (token) => {
         textAlign: 'center',
         color: token.colorTextDisabled,

-        [`
-          &:hover > th,
-          &:hover > td,
-        `]: {
+        '&:hover > th, &:hover > td': {
           background: token.colorBgContainer,
         },
       },
diff --git a/components/table/style/index.ts b/components/table/style/index.ts
index 5edb7b9339dc..2207a41c1863 100644
--- a/components/table/style/index.ts
+++ b/components/table/style/index.ts
@@ -306,10 +306,7 @@ const genTableStyle: GenerateStyle<TableToken, CSSObject> = (token) => {

       // ============================ Header ============================
       [`${componentCls}-thead`]: {
-        [`
-          > tr > th,
-          > tr > td
-        `]: {
+        '> tr > th, > tr > td': {
           position: 'relative',
           color: tableHeaderTextColor,
           fontWeight: fontWeightStrong,
diff --git a/components/typography/style/index.ts b/components/typography/style/index.ts
index 3521eb1d4618..66e3fb28af08 100644
--- a/components/typography/style/index.ts
+++ b/components/typography/style/index.ts
@@ -64,42 +64,19 @@ const genTypographyStyle: GenerateStyle<TypographyToken, CSSObject> = (token) =>
         userSelect: 'none',
       },

-      [`
-        div&,
-        p
-      `]: {
+      'div&, p': {
         marginBottom: '1em',
       },

       ...getTitleStyles(token),

-      [`
-      & + h1${componentCls},
-      & + h2${componentCls},
-      & + h3${componentCls},
-      & + h4${componentCls},
-      & + h5${componentCls}
-      `]: {
-        marginTop: titleMarginTop,
-      },
+      [`& + h1${componentCls}, & + h2${componentCls}, & + h3${componentCls}, & + h4${componentCls}, & + h5${componentCls}`]:
+        {
+          marginTop: titleMarginTop,
+        },

-      [`
-      div,
-      ul,
-      li,
-      p,
-      h1,
-      h2,
-      h3,
-      h4,
-      h5`]: {
-        [`
-        + h1,
-        + h2,
-        + h3,
-        + h4,
-        + h5
-        `]: {
+      'div, ul, li, p, h1, h2, h3, h4, h5': {
+        '+ h1, + h2, + h3, + h4, + h5': {
           marginTop: titleMarginTop,
         },
       },
diff --git a/components/typography/style/mixins.ts b/components/typography/style/mixins.ts
index 591c2b3a86d8..d979b4e8c43c 100644
--- a/components/typography/style/mixins.ts
+++ b/components/typography/style/mixins.ts
@@ -219,10 +219,7 @@ export const getEditableStyles: GenerateStyle<TypographyToken, CSSObject> = (tok

 export const getCopyableStyles: GenerateStyle<TypographyToken, CSSObject> = (token) => ({
   [`${token.componentCls}-copy-success`]: {
-    [`
-    &,
-    &:hover,
-    &:focus`]: {
+    '&, &:hover, &:focus': {
       color: token.colorSuccess,
     },
   },
@@ -232,10 +229,7 @@ export const getCopyableStyles: GenerateStyle<TypographyToken, CSSObject> = (tok
 });

 export const getEllipsisStyles = (): CSSObject => ({
-  [`
-  a&-ellipsis,
-  span&-ellipsis
-  `]: {
+  'a&-ellipsis, span&-ellipsis': {
     display: 'inline-block',
     maxWidth: '100%',
   },
PATCH

# Idempotency check - verify a distinctive line from the patch
if ! grep -q "'&, & > .arrow'" components/collapse/style/index.ts; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
