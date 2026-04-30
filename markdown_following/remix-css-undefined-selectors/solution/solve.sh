#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency check
if grep -q 'Allow at-rules to be conditionally disabled' packages/component/src/lib/style/lib/style.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/component/src/lib/style/lib/style.ts b/packages/component/src/lib/style/lib/style.ts
index 9f59b813d88..290df1a9bc4 100644
--- a/packages/component/src/lib/style/lib/style.ts
+++ b/packages/component/src/lib/style/lib/style.ts
@@ -16,6 +16,8 @@ export interface CSSProps extends DOMStyleProperties {
   [key: string]: CSSProps | string | number | null | undefined
 }

+type StyleObject = Record<string, unknown>
+
 // Convert camelCase CSS properties to kebab-case
 function camelToKebab(str: string): string {
   return str.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)
@@ -94,7 +96,7 @@ function hashStyle(obj: any): string {
 }

 // Convert style object to CSS text
-function styleToCss(styles: CSSProps, selector: string = ''): string {
+function styleToCss(styles: StyleObject, selector: string = ''): string {
   let baseDeclarations: string[] = []
   let nestedBlocks: string[] = []
   let atRules: string[] = []
@@ -103,10 +105,15 @@ function styleToCss(styles: CSSProps, selector: string = ''): string {
   for (let [key, value] of Object.entries(styles)) {
     if (isComplexSelector(key)) {
       if (key.startsWith('@')) {
+        // Allow at-rules to be conditionally disabled.
+        // e.g. { '@media (min-width: 600px)': condition ? undefined : { ... } }
+        let record = toRecord(value)
+        if (!record) continue
+
         // Some at-rules (e.g., @media) scope declarations to the selector.
         // Others (e.g., @function) must NOT include the selector in their body.
         if (key.startsWith('@function')) {
-          let body = atRuleBodyToCss(value as CSSProps)
+          let body = atRuleBodyToCss(record)
           if (body.trim().length > 0) {
             preludeAtRules.push(`${key} {\n${indent(body, 2)}\n}`)
           } else {
@@ -115,7 +122,7 @@ function styleToCss(styles: CSSProps, selector: string = ''): string {
         } else if (isKeyframesAtRule(key)) {
           // Keyframes definitions must not be wrapped with the element selector.
           // Emit them before the class rule so animations can be referenced.
-          let body = keyframesBodyToCss(value)
+          let body = keyframesBodyToCss(record)
           if (body.trim().length > 0) {
             preludeAtRules.push(`${key} {\n${indent(body, 2)}\n}`)
           } else {
@@ -123,7 +130,7 @@ function styleToCss(styles: CSSProps, selector: string = ''): string {
           }
         } else {
           // Default: keep at-rules nested with the element selector
-          let inner = styleToCss(value as CSSProps, selector)
+          let inner = styleToCss(record, selector)
           if (inner.trim().length > 0) {
             atRules.push(`${key} {\n${indent(inner, 2)}\n}`)
           } else {
@@ -135,8 +142,13 @@ function styleToCss(styles: CSSProps, selector: string = ''): string {
       }

       // For nested selectors, keep them wholesale inside the base block
+      // Allow nested selectors to be conditionally disabled.
+      // e.g. { '&:hover': condition ? undefined : { ... } }
+      let record = toRecord(value)
+      if (!record) continue
+
       let nestedContent = ''
-      for (let [prop, propValue] of Object.entries(value as Record<string, any>)) {
+      for (let [prop, propValue] of Object.entries(record)) {
         if (propValue != null) {
           let normalizedValue = normalizeCssValue(prop, propValue)
           nestedContent += `    ${camelToKebab(prop)}: ${normalizedValue};\n`
@@ -187,13 +199,15 @@ function indent(text: string, spaces: number): string {

 // Narrow unknown values to plain record objects
 function isRecord(value: unknown): value is Record<string, unknown> {
-  return typeof value === 'object' && value !== null
+  return typeof value === 'object' && value !== null && !Array.isArray(value)
 }

-// Build the body of a @keyframes rule (without wrapping selector)
-function keyframesBodyToCss(frames: unknown): string {
-  if (!isRecord(frames)) return ''
+function toRecord(value: unknown): Record<string, unknown> | null {
+  return isRecord(value) ? value : null
+}

+// Build the body of a @keyframes rule (without wrapping selector)
+function keyframesBodyToCss(frames: StyleObject): string {
   let blocks: string[] = []

   for (let [frameSelector, frameValue] of Object.entries(frames)) {
@@ -222,7 +236,7 @@ function keyframesBodyToCss(frames: unknown): string {
 }

 // Build the body for at-rules that should not include a selector wrapper (e.g., @function)
-function atRuleBodyToCss(styles: CSSProps): string {
+function atRuleBodyToCss(styles: StyleObject): string {
   let declarations: string[] = []
   let nested: string[] = []

@@ -230,7 +244,9 @@ function atRuleBodyToCss(styles: CSSProps): string {
     if (isComplexSelector(key)) {
       if (key.startsWith('@')) {
         // Nested at-rules inside definition blocks; render their bodies recursively without selectors
-        let inner = atRuleBodyToCss(value as CSSProps)
+        let record = toRecord(value)
+        if (!record) continue
+        let inner = atRuleBodyToCss(record)
         if (inner.trim().length > 0) {
           nested.push(`${key} {\n${indent(inner, 2)}\n}`)
         } else {
PATCH

echo "Patch applied successfully."
