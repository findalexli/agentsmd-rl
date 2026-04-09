#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'appendRepeatEachIndexAnnotation' packages/html-reporter/src/testCaseView.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/html-reporter/src/testCaseView.tsx b/packages/html-reporter/src/testCaseView.tsx
index 2e8e71cf11b2c..11a031fb365f8 100644
--- a/packages/html-reporter/src/testCaseView.tsx
+++ b/packages/html-reporter/src/testCaseView.tsx
@@ -43,6 +43,7 @@ export const TestCaseView: React.FC<{
   const searchParams = useSearchParams();

   const visibleTestAnnotations = test.annotations.filter(a => !a.type.startsWith('_')) ?? [];
+  appendRepeatEachIndexAnnotation(visibleTestAnnotations, test.repeatEachIndex);

   return <>
     <HeaderView
@@ -78,6 +79,7 @@ export const TestCaseView: React.FC<{
         </div>,
         render: () => {
           const visibleAnnotations = result.annotations.filter(annotation => !annotation.type.startsWith('_'));
+          appendRepeatEachIndexAnnotation(visibleAnnotations, test.repeatEachIndex);
           return <>
             {!!visibleAnnotations.length && <AutoChip header='Annotations' dataTestId='test-case-annotations'>
               {visibleAnnotations.map((annotation, index) => <TestCaseAnnotationView key={index} annotation={annotation} />)}
@@ -98,6 +100,11 @@ function TestCaseAnnotationView({ annotation: { type, description } }: { annotat
   );
 }

+function appendRepeatEachIndexAnnotation(annotations: TestAnnotation[], repeatEachIndex: number | undefined) {
+  if (repeatEachIndex)
+    annotations.push({ type: 'repeatEachIndex', description: String(repeatEachIndex) });
+}
+
 function retryLabel(index: number) {
   if (!index)
     return 'Run';
diff --git a/packages/html-reporter/src/types.d.ts b/packages/html-reporter/src/types.d.ts
index dd7927e09d254..ca2ecec64dd3b 100644
--- a/packages/html-reporter/src/types.d.ts
+++ b/packages/html-reporter/src/types.d.ts
@@ -84,6 +84,7 @@ export type TestCaseSummary = {
   duration: number;
   ok: boolean;
   results: TestResultSummary[];
+  repeatEachIndex?: number;
 };

 export type TestResultSummary = {
diff --git a/packages/playwright/src/reporters/html.ts b/packages/playwright/src/reporters/html.ts
index e9c3ca8393cfd..cff686e038a0f 100644
--- a/packages/playwright/src/reporters/html.ts
+++ b/packages/playwright/src/reporters/html.ts
@@ -451,6 +451,7 @@ class HtmlBuilder {
         outcome: test.outcome(),
         path,
         results,
+        repeatEachIndex: test.repeatEachIndex || undefined, // Do not include zero.
         ok: test.outcome() === 'expected' || test.outcome() === 'flaky',
       },
       testCaseSummary: {
@@ -464,6 +465,7 @@ class HtmlBuilder {
         outcome: test.outcome(),
         path,
         ok: test.outcome() === 'expected' || test.outcome() === 'flaky',
+        repeatEachIndex: test.repeatEachIndex || undefined, // Do not include zero.
         results: results.map(result => {
           return {
             attachments: result.attachments.map(a => ({ name: a.name, contentType: a.contentType, path: a.path })),

PATCH

echo "Patch applied successfully."
