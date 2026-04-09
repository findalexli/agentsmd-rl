#!/bin/bash
set -e

cd /workspace/ant-design

# Check if patch is already applied (idempotency)
if grep -q "colorShadow" components/theme/interface/maps/colors.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch for shadow token dark theme fix
patch -p1 <<'PATCH'
diff --git a/components/dropdown/__tests__/__snapshots__/demo-extend.test.ts.snap b/components/dropdown/__tests__/__snapshots__/demo-extend.test.ts.snap
index f5e649fc529e..2f23d8fd0fa3 100644
--- a/components/dropdown/__tests__/__snapshots__/demo-extend.test.ts.snap
+++ b/components/dropdown/__tests__/__snapshots__/demo-extend.test.ts.snap
@@ -2143,9 +2143,9 @@ Array [
     style="--arrow-x: 0px; --arrow-y: 0px; left: -1000vw; top: -1000vh; right: auto; bottom: auto; box-sizing: border-box;"
   >
     <div
-      style="background-color: rgb(255, 255, 255); border-radius: 8px; box-shadow: 0 6px 16px 0 rgba(0, 0, 0, 0.08),
-      0 3px 6px -4px rgba(0, 0, 0, 0.12),
-      0 9px 28px 8px rgba(0, 0, 0, 0.05);"
+      style="background-color: rgb(255, 255, 255); border-radius: 8px; box-shadow: 0 6px 16px 0 rgba(0,0,0,0.08),
+      0 3px 6px -4px rgba(0,0,0,0.12),
+      0 9px 28px 8px rgba(0,0,0,0.05);"
     >
       <ul
         class="ant-dropdown-menu ant-dropdown-menu-root ant-dropdown-menu-vertical ant-dropdown-menu-light css-var-test-id ant-dropdown-css-var css-var-test-id ant-dropdown-menu-css-var"
diff --git a/components/menu/__tests__/__snapshots__/demo-extend.test.ts.snap b/components/menu/__tests__/__snapshots__/demo-extend.test.ts.snap
index 782ab24494e7..b573486bfa99 100644
--- a/components/menu/__tests__/__snapshots__/demo-extend.test.ts.snap
+++ b/components/menu/__tests__/__snapshots__/demo-extend.test.ts.snap
@@ -2624,7 +2624,7 @@ Array [
         style="--arrow-x: 0px; --arrow-y: 0px; left: -1000vw; top: -1000vh; right: auto; bottom: auto; box-sizing: border-box;"
       >
         <div
-          class="acss-kuniwg ant-flex css-var-test-id ant-flex-align-stretch ant-flex-gap-medium ant-flex-vertical"
+          class="acss-1bjei0t ant-flex css-var-test-id ant-flex-align-stretch ant-flex-gap-medium ant-flex-vertical"
         >
           <h3
             class="ant-typography acss-1s688k3 css-var-test-id"
diff --git a/components/theme/__tests__/token.test.tsx b/components/theme/__tests__/token.test.tsx
index da4ac1514af9..a1327579c46a 100644
--- a/components/theme/__tests__/token.test.tsx
+++ b/components/theme/__tests__/token.test.tsx
@@ -315,6 +315,23 @@ describe('Theme', () => {
     });
   });

+  it('shadow tokens should adapt to dark theme', () => {
+    const { token } = getHookToken();
+    const { token: darkToken } = getHookToken({
+      algorithm: [theme.darkAlgorithm],
+    });
+    const { token: darkCustomTextBaseToken } = getHookToken({
+      algorithm: [theme.darkAlgorithm],
+      token: { colorTextBase: '#ff0000' },
+    });
+
+    expect(token.boxShadow).toMatch(/rgba\(0,\s*0,\s*0,\s*0\.08\)/);
+    expect(token.boxShadowCard).toMatch(/rgba\(0,\s*0,\s*0,\s*0\.16\)/);
+    expect(darkToken.boxShadow).toMatch(/rgba\(255,\s*255,\s*255,\s*0\.016\)/);
+    expect(darkToken.boxShadowCard).toMatch(/rgba\(255,\s*255,\s*255,\s*0\.032\)/);
+    expect(darkCustomTextBaseToken.boxShadowCard).toMatch(/rgba\(255,\s*255,\s*255,\s*0\.032\)/);
+  });
+
   it('component token should support algorithm', () => {
     const Demo: React.FC<{ algorithm?: boolean | typeof theme.darkAlgorithm }> = (props) => {
       const { algorithm } = props;
diff --git a/components/theme/interface/maps/colors.ts b/components/theme/interface/maps/colors.ts
index 520405ebe546..b6306400691c 100644
--- a/components/theme/interface/maps/colors.ts
+++ b/components/theme/interface/maps/colors.ts
@@ -9,6 +9,11 @@ export interface ColorNeutralMapToken {
    */
   colorBgBase: string;

+  /**
+   * @internal
+   */
+  colorShadow: string;
+
   // ----------   Text   ---------- //

   /**
diff --git a/components/theme/themes/ColorMap.ts b/components/theme/themes/ColorMap.ts
index 0a6821076736..1345c33fed30 100644
--- a/components/theme/themes/ColorMap.ts
+++ b/components/theme/themes/ColorMap.ts
@@ -14,7 +14,9 @@ export interface ColorMap {
 }

 export type GenerateColorMap = (baseColor: string) => ColorMap;
+
 export type GenerateNeutralColorMap = (
   bgBaseColor: string,
   textBaseColor: string,
+  shadowColor?: string,
 ) => ColorNeutralMapToken;
diff --git a/components/theme/themes/dark/colors.ts b/components/theme/themes/dark/colors.ts
index 789f22061dd1..886798547093 100644
--- a/components/theme/themes/dark/colors.ts
+++ b/components/theme/themes/dark/colors.ts
@@ -22,13 +22,16 @@ export const generateColorPalettes: GenerateColorMap = (baseColor: string) => {
 export const generateNeutralColorPalettes: GenerateNeutralColorMap = (
   bgBaseColor: string,
   textBaseColor: string,
+  shadowColor?: string,
 ) => {
   const colorBgBase = bgBaseColor || '#000';
   const colorTextBase = textBaseColor || '#fff';
+  const colorShadow = shadowColor || 'rgba(255, 255, 255, 0.2)';

   return {
     colorBgBase,
     colorTextBase,
+    colorShadow,

     colorText: getAlphaColor(colorTextBase, 0.85),
     colorTextSecondary: getAlphaColor(colorTextBase, 0.65),
diff --git a/components/theme/themes/default/colors.ts b/components/theme/themes/default/colors.ts
index 5c876968d80c..76d821c9d822 100644
--- a/components/theme/themes/default/colors.ts
+++ b/components/theme/themes/default/colors.ts
@@ -22,13 +22,16 @@ export const generateColorPalettes: GenerateColorMap = (baseColor: string) => {
 export const generateNeutralColorPalettes: GenerateNeutralColorMap = (
   bgBaseColor: string,
   textBaseColor: string,
+  shadowColor?: string,
 ) => {
   const colorBgBase = bgBaseColor || '#fff';
   const colorTextBase = textBaseColor || '#000';
+  const colorShadow = shadowColor || '#000';

   return {
     colorBgBase,
     colorTextBase,
+    colorShadow,

     colorText: getAlphaColor(colorTextBase, 0.88),
     colorTextSecondary: getAlphaColor(colorTextBase, 0.65),
diff --git a/components/theme/util/alias.ts b/components/theme/util/alias.ts
index 458bb2acefd4..70678502f845 100644
--- a/components/theme/util/alias.ts
+++ b/components/theme/util/alias.ts
@@ -24,6 +24,13 @@ export default function formatToken(derivativeToken: RawMergedToken): AliasToken
     ...restToken,
     ...overrideTokens,
   };
+  const shadowBaseColor = new FastColor(mergedToken.colorShadow);
+  const shadowBaseAlpha = shadowBaseColor.a;
+  const getShadowColor = (alpha: number) =>
+    shadowBaseColor
+      .clone()
+      .setA(shadowBaseAlpha * alpha)
+      .toRgbString();

   const screenXS = 480;
   const screenSM = 576;
@@ -133,19 +140,19 @@ export default function formatToken(derivativeToken: RawMergedToken): AliasToken
     marginXXL: mergedToken.sizeXXL,

     boxShadow: `
-      0 6px 16px 0 rgba(0, 0, 0, 0.08),
-      0 3px 6px -4px rgba(0, 0, 0, 0.12),
-      0 9px 28px 8px rgba(0, 0, 0, 0.05)
+      0 6px 16px 0 ${getShadowColor(0.08)},
+      0 3px 6px -4px ${getShadowColor(0.12)},
+      0 9px 28px 8px ${getShadowColor(0.05)}
     `,
     boxShadowSecondary: `
-      0 6px 16px 0 rgba(0, 0, 0, 0.08),
-      0 3px 6px -4px rgba(0, 0, 0, 0.12),
-      0 9px 28px 8px rgba(0, 0, 0, 0.05)
+      0 6px 16px 0 ${getShadowColor(0.08)},
+      0 3px 6px -4px ${getShadowColor(0.12)},
+      0 9px 28px 8px ${getShadowColor(0.05)}
     `,
     boxShadowTertiary: `
-      0 1px 2px 0 rgba(0, 0, 0, 0.03),
-      0 1px 6px -1px rgba(0, 0, 0, 0.02),
-      0 2px 4px 0 rgba(0, 0, 0, 0.02)
+      0 1px 2px 0 ${getShadowColor(0.03)},
+      0 1px 6px -1px ${getShadowColor(0.02)},
+      0 2px 4px 0 ${getShadowColor(0.02)}
     `,

     screenXS,
@@ -169,36 +176,36 @@ export default function formatToken(derivativeToken: RawMergedToken): AliasToken
     screenXXXL,
     screenXXXLMin: screenXXXL,

-    boxShadowPopoverArrow: '2px 2px 5px rgba(0, 0, 0, 0.05)',
+    boxShadowPopoverArrow: `2px 2px 5px ${getShadowColor(0.05)}`,
     boxShadowCard: `
-      0 1px 2px -2px ${new FastColor('rgba(0, 0, 0, 0.16)').toRgbString()},
-      0 3px 6px 0 ${new FastColor('rgba(0, 0, 0, 0.12)').toRgbString()},
-      0 5px 12px 4px ${new FastColor('rgba(0, 0, 0, 0.09)').toRgbString()}
+      0 1px 2px -2px ${getShadowColor(0.16)},
+      0 3px 6px 0 ${getShadowColor(0.12)},
+      0 5px 12px 4px ${getShadowColor(0.09)}
     `,
     boxShadowDrawerRight: `
-      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
-      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
-      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
+      -6px 0 16px 0 ${getShadowColor(0.08)},
+      -3px 0 6px -4px ${getShadowColor(0.12)},
+      -9px 0 28px 8px ${getShadowColor(0.05)}
     `,
     boxShadowDrawerLeft: `
-      6px 0 16px 0 rgba(0, 0, 0, 0.08),
-      3px 0 6px -4px rgba(0, 0, 0, 0.12),
-      9px 0 28px 8px rgba(0, 0, 0, 0.05)
+      6px 0 16px 0 ${getShadowColor(0.08)},
+      3px 0 6px -4px ${getShadowColor(0.12)},
+      9px 0 28px 8px ${getShadowColor(0.05)}
     `,
     boxShadowDrawerUp: `
-      0 6px 16px 0 rgba(0, 0, 0, 0.08),
-      0 3px 6px -4px rgba(0, 0, 0, 0.12),
-      0 9px 28px 8px rgba(0, 0, 0, 0.05)
+      0 6px 16px 0 ${getShadowColor(0.08)},
+      0 3px 6px -4px ${getShadowColor(0.12)},
+      0 9px 28px 8px ${getShadowColor(0.05)}
     `,
     boxShadowDrawerDown: `
-      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
-      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
-      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
+      0 -6px 16px 0 ${getShadowColor(0.08)},
+      0 -3px 6px -4px ${getShadowColor(0.12)},
+      0 -9px 28px 8px ${getShadowColor(0.05)}
     `,
-    boxShadowTabsOverflowLeft: 'inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)',
-    boxShadowTabsOverflowRight: 'inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)',
-    boxShadowTabsOverflowTop: 'inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)',
-    boxShadowTabsOverflowBottom: 'inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)',
+    boxShadowTabsOverflowLeft: `inset 10px 0 8px -8px ${getShadowColor(0.08)}`,
+    boxShadowTabsOverflowRight: `inset -10px 0 8px -8px ${getShadowColor(0.08)}`,
+    boxShadowTabsOverflowTop: `inset 0 10px 8px -8px ${getShadowColor(0.08)}`,
+    boxShadowTabsOverflowBottom: `inset 0 -10px 8px -8px ${getShadowColor(0.08)}`,

     // Override AliasToken
     ...overrideTokens,
PATCH

echo "Patch applied successfully"
