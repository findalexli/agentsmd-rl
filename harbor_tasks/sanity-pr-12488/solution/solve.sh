#!/bin/bash
set -e

cd /workspace/sanity

# Apply the fix for read-only fields during document paste
# This patch addresses issue #7408 where read-only fields were silently overwritten

patch -p1 <<'PATCH'
diff --git a/packages/sanity/src/core/studio/copyPaste/transferValue.ts b/packages/sanity/src/core/studio/copyPaste/transferValue.ts
index 9c485ab960b9..388ec94bf6d6 100644
--- a/packages/sanity/src/core/studio/copyPaste/transferValue.ts
+++ b/packages/sanity/src/core/studio/copyPaste/transferValue.ts
@@ -131,6 +131,8 @@ export interface TransferValueOptions {
   client?: ClientWithFetch
 }

+type ReadOnlyContext = {currentUser: CurrentUser | null}
+
 /**
  * Takes the path and checks if any ancestor is read-only
  * ["a", "b", "c"] - ["a"], ["a", "b"], ["a", "b", "c"],
@@ -346,6 +348,7 @@ export async function transferValue({
     sourceSchemaTypeAtPath.jsonType === 'object' &&
     targetSchemaTypeAtPath.jsonType === 'object'
   ) {
+    const isDocumentLevelPaste = targetRootPath.length === 0
     return collateObjectValue({
       sourceValue: sourceValueAtPath as TypedObject,
       targetSchemaType: targetSchemaTypeAtPath as ObjectSchemaType,
@@ -355,6 +358,7 @@ export async function transferValue({
       errors,
       keyGenerator,
       options,
+      readOnlyContext: isDocumentLevelPaste ? {currentUser} : undefined,
     })
   }

@@ -446,6 +450,7 @@ async function collateObjectValue({
   errors,
   keyGenerator,
   options,
+  readOnlyContext,
 }: {
   sourceValue: unknown
   targetSchemaType: ObjectSchemaType
@@ -455,6 +460,7 @@ async function collateObjectValue({
   errors: TransferValueError[]
   keyGenerator: () => string
   options: TransferValueOptions
+  readOnlyContext?: ReadOnlyContext
 }) {
   if (isEmptyValue(sourceValue)) {
     return {
@@ -710,8 +716,33 @@ async function collateObjectValue({
   }

   const objectMembers = targetSchemaType.fields
+  const skippedReadOnlyFieldNames: string[] = []
+  const documentValue = readOnlyContext ? (targetRootValue as Record<string, unknown>) : undefined
+  const parentValue = documentValue
+    ? (getValueAtPath(documentValue, targetRootPath) as Record<string, unknown>)
+    : undefined

   for (const member of objectMembers) {
+    if (readOnlyContext && documentValue) {
+      const fieldPath = targetRootPath.concat(member.name)
+      const isFieldReadOnly = resolveConditionalProperty(member.type.readOnly, {
+        value: getValueAtPath(documentValue, fieldPath),
+        parent: parentValue,
+        document: documentValue,
+        currentUser: readOnlyContext.currentUser,
+        path: fieldPath,
+      })
+
+      if (isFieldReadOnly) {
+        skippedReadOnlyFieldNames.push(member.type.title ?? member.name)
+        const existingValue = parentValue?.[member.name]
+        if (existingValue !== undefined) {
+          targetValue[member.name] = existingValue
+        }
+        continue
+      }
+    }
+
     const memberSchemaType = member.type
     const memberIsArray = isArraySchemaType(memberSchemaType)
     const memberIsObject = isObjectSchemaType(memberSchemaType)
@@ -740,7 +771,7 @@ async function collateObjectValue({
         targetPath: [],
         targetSchemaType: memberSchemaType,
         targetRootValue,
-        targetRootPath,
+        targetRootPath: targetRootPath.concat(member.name),
         errors,
         options,
         keyGenerator,
@@ -788,6 +819,31 @@ async function collateObjectValue({
     }
   }

+  const MAX_DISPLAYED_READONLY_FIELDS = 3
+  if (skippedReadOnlyFieldNames.length > 0) {
+    const isTruncated = skippedReadOnlyFieldNames.length > MAX_DISPLAYED_READONLY_FIELDS
+    errors.push({
+      level: 'warning',
+      sourceValue,
+      i18n: isTruncated
+        ? {
+            key: 'copy-paste.on-paste.validation.read-only-fields-skipped-truncated.description',
+            args: {
+              fieldNames: skippedReadOnlyFieldNames
+                .slice(0, MAX_DISPLAYED_READONLY_FIELDS)
+                .join(', '),
+              count: skippedReadOnlyFieldNames.length - MAX_DISPLAYED_READONLY_FIELDS,
+            },
+          }
+        : {
+            key: 'copy-paste.on-paste.validation.read-only-fields-skipped.description',
+            args: {
+              fieldNames: skippedReadOnlyFieldNames.join(', '),
+            },
+          },
+    })
+  }
+
   const valueAtTargetPath = getValueAtPath(targetValue, targetPath)
   const resultingValue = cleanObjectKeys(valueAtTargetPath as TypedObject)
   return {
PATCH

# Apply the i18n string additions
cat >> /tmp/i18n_patch.txt <<'I18N_PATCH'
  /** The validation message that is shown when read-only fields are skipped during document paste */
  'copy-paste.on-paste.validation.read-only-fields-skipped.description':
    'Skipped read-only fields: {{fieldNames}}',
  /** The validation message for skipped read-only fields when truncated */
  'copy-paste.on-paste.validation.read-only-fields-skipped-truncated.description':
    'Skipped read-only fields: {{fieldNames}} and {{count}} more',
I18N_PATCH

# Insert the i18n strings after the existing read-only-target description line
sed -i "/'copy-paste.on-paste.validation.read-only-target.description': 'The target is read-only',/r /tmp/i18n_patch.txt" packages/sanity/src/core/i18n/bundles/copy-paste.ts

# Idempotency check: verify distinctive line from patch is present
grep -q "skippedReadOnlyFieldNames.push(member.type.title ?? member.name)" packages/sanity/src/core/studio/copyPaste/transferValue.ts
grep -q "read-only-fields-skipped.description" packages/sanity/src/core/i18n/bundles/copy-paste.ts

echo "Fix applied successfully"
