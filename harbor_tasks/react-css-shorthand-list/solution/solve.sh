#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
if grep -q "borderBlock: \[" packages/react-dom-bindings/src/client/CSSShorthandProperty.js; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/client/CSSShorthandProperty.js b/packages/react-dom-bindings/src/client/CSSShorthandProperty.js
index 1781254b758c..19ec1d5ceff2 100644
--- a/packages/react-dom-bindings/src/client/CSSShorthandProperty.js
+++ b/packages/react-dom-bindings/src/client/CSSShorthandProperty.js
@@ -5,8 +5,8 @@
  * LICENSE file in the root directory of this source tree.
  */

-// List derived from Gecko source code:
-// https://github.com/mozilla/gecko-dev/blob/4e638efc71/layout/style/test/property_database.js
+// List derived from Firefox source code:
+// https://github.com/mozilla-firefox/firefox/blob/58f365ba0eb5761a182f1925e4654cc75212b8ac/layout/style/test/property_database.js
 export const shorthandToLonghand = {
   animation: [
     'animationDelay',
@@ -49,6 +49,15 @@ export const shorthandToLonghand = {
     'borderTopStyle',
     'borderTopWidth',
   ],
+  borderBlock: [
+    'borderBlockEndColor',
+    'borderBlockEndStyle',
+    'borderBlockEndWidth',
+    'borderBlockStartColor',
+    'borderBlockStartStyle',
+    'borderBlockStartWidth',
+  ],
+  borderBlockColor: ['borderBlockEndColor', 'borderBlockStartColor'],
   borderBlockEnd: [
     'borderBlockEndColor',
     'borderBlockEndStyle',
@@ -59,6 +68,8 @@ export const shorthandToLonghand = {
     'borderBlockStartStyle',
     'borderBlockStartWidth',
   ],
+  borderBlockStyle: ['borderBlockEndStyle', 'borderBlockStartStyle'],
+  borderBlockWidth: ['borderBlockEndWidth', 'borderBlockStartWidth'],
   borderBottom: ['borderBottomColor', 'borderBottomStyle', 'borderBottomWidth'],
   borderColor: [
     'borderBottomColor',
@@ -73,6 +84,15 @@ export const shorthandToLonghand = {
     'borderImageSource',
     'borderImageWidth',
   ],
+  borderInline: [
+    'borderInlineEndColor',
+    'borderInlineEndStyle',
+    'borderInlineEndWidth',
+    'borderInlineStartColor',
+    'borderInlineStartStyle',
+    'borderInlineStartWidth',
+  ],
+  borderInlineColor: ['borderInlineEndColor', 'borderInlineStartColor'],
   borderInlineEnd: [
     'borderInlineEndColor',
     'borderInlineEndStyle',
@@ -83,6 +103,8 @@ export const shorthandToLonghand = {
     'borderInlineStartStyle',
     'borderInlineStartWidth',
   ],
+  borderInlineStyle: ['borderInlineEndStyle', 'borderInlineStartStyle'],
+  borderInlineWidth: ['borderInlineEndWidth', 'borderInlineStartWidth'],
   borderLeft: ['borderLeftColor', 'borderLeftStyle', 'borderLeftWidth'],
   borderRadius: [
     'borderBottomLeftRadius',
@@ -104,8 +126,11 @@ export const shorthandToLonghand = {
     'borderRightWidth',
     'borderTopWidth',
   ],
+  colorAdjust: ['printColorAdjust'],
   columnRule: ['columnRuleColor', 'columnRuleStyle', 'columnRuleWidth'],
   columns: ['columnCount', 'columnWidth'],
+  containIntrinsicSize: ['containIntrinsicHeight', 'containIntrinsicWidth'],
+  container: ['containerName', 'containerType'],
   flex: ['flexBasis', 'flexGrow', 'flexShrink'],
   flexFlow: ['flexDirection', 'flexWrap'],
   font: [
@@ -127,6 +152,12 @@ export const shorthandToLonghand = {
     'fontWeight',
     'lineHeight',
   ],
+  fontSynthesis: [
+    'fontSynthesisPosition',
+    'fontSynthesisSmallCaps',
+    'fontSynthesisStyle',
+    'fontSynthesisWeight',
+  ],
   fontVariant: [
     'fontVariantAlternates',
     'fontVariantCaps',
@@ -155,8 +186,13 @@ export const shorthandToLonghand = {
     'gridTemplateColumns',
     'gridTemplateRows',
   ],
+  inset: ['bottom', 'left', 'right', 'top'],
+  insetBlock: ['insetBlockEnd', 'insetBlockStart'],
+  insetInline: ['insetInlineEnd', 'insetInlineStart'],
   listStyle: ['listStyleImage', 'listStylePosition', 'listStyleType'],
   margin: ['marginBottom', 'marginLeft', 'marginRight', 'marginTop'],
+  marginBlock: ['marginBlockEnd', 'marginBlockStart'],
+  marginInline: ['marginInlineEnd', 'marginInlineStart'],
   marker: ['markerEnd', 'markerMid', 'markerStart'],
   mask: [
     'maskClip',
@@ -170,23 +206,57 @@ export const shorthandToLonghand = {
     'maskSize',
   ],
   maskPosition: ['maskPositionX', 'maskPositionY'],
+  offset: [
+    'offsetAnchor',
+    'offsetDistance',
+    'offsetPath',
+    'offsetPosition',
+    'offsetRotate',
+  ],
   outline: ['outlineColor', 'outlineStyle', 'outlineWidth'],
   overflow: ['overflowX', 'overflowY'],
+  overscrollBehavior: ['overscrollBehaviorX', 'overscrollBehaviorY'],
   padding: ['paddingBottom', 'paddingLeft', 'paddingRight', 'paddingTop'],
+  paddingBlock: ['paddingBlockEnd', 'paddingBlockStart'],
+  paddingInline: ['paddingInlineEnd', 'paddingInlineStart'],
+  pageBreakAfter: ['breakAfter'],
+  pageBreakBefore: ['breakBefore'],
+  pageBreakInside: ['breakInside'],
   placeContent: ['alignContent', 'justifyContent'],
   placeItems: ['alignItems', 'justifyItems'],
   placeSelf: ['alignSelf', 'justifySelf'],
+  scrollMargin: [
+    'scrollMarginBottom',
+    'scrollMarginLeft',
+    'scrollMarginRight',
+    'scrollMarginTop',
+  ],
+  scrollMarginBlock: ['scrollMarginBlockEnd', 'scrollMarginBlockStart'],
+  scrollMarginInline: ['scrollMarginInlineEnd', 'scrollMarginInlineStart'],
+  scrollPadding: [
+    'scrollPaddingBottom',
+    'scrollPaddingLeft',
+    'scrollPaddingRight',
+    'scrollPaddingTop',
+  ],
+  scrollPaddingBlock: ['scrollPaddingBlockEnd', 'scrollPaddingBlockStart'],
+  scrollPaddingInline: ['scrollPaddingInlineEnd', 'scrollPaddingInlineStart'],
   textDecoration: [
     'textDecorationColor',
     'textDecorationLine',
     'textDecorationStyle',
+    'textDecorationThickness',
   ],
   textEmphasis: ['textEmphasisColor', 'textEmphasisStyle'],
+  textWrap: ['textWrapMode', 'textWrapStyle'],
   transition: [
+    'transitionBehavior',
     'transitionDelay',
     'transitionDuration',
     'transitionProperty',
     'transitionTimingFunction',
   ],
+  verticalAlign: ['alignmentBaseline', 'baselineShift', 'baselineSource'],
+  whiteSpace: ['textWrapMode', 'whiteSpaceCollapse'],
   wordWrap: ['overflowWrap'],
 };
PATCH

echo "Patch applied successfully"
