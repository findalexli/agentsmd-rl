#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'ensureWorker' src/libs/pdfjs/index.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'GOLDPATCH_END'
diff --git a/CLAUDE.md b/CLAUDE.md
index 65d5cbbff8a..6ddaaea7799 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -61,11 +61,19 @@ see @.cursor/rules/typescript.mdc
 - **Dev**: Translate `locales/zh-CN/namespace.json` and `locales/en-US/namespace.json` locales file only for dev preview
 - DON'T run `pnpm i18n`, let CI auto handle it

-## Linear Issue Management (search tools first; ignore if not installed)
+## Linear Issue Management

-ClaudeCode may not inject MCP tools until they are discovered/used.\
-Before applying Linear workflows, **use tool search** to confirm `linear-server` exists (e.g. search `linear` / `mcp__linear-server__`). If not found, treat it as not installed.\
-Then read `@.cursor/rules/linear.mdc` when working with Linear issues.
+**Trigger conditions** - when ANY of these occur, apply Linear workflow:
+
+- User mentions issue ID like `LOBE-XXX`
+- User says "linear", "link linear", "linear issue"
+- Creating PR that references a Linear issue
+
+**Workflow:**
+
+1. Use `ToolSearch` to confirm `linear-server` MCP exists (search `linear` or `mcp__linear-server__`)
+2. If found, read `.cursor/rules/linear.mdc` and follow the workflow
+3. If not found, skip Linear integration (treat as not installed)

 ## Rules Index

diff --git a/src/features/FileViewer/Renderer/PDF/index.tsx b/src/features/FileViewer/Renderer/PDF/index.tsx
index 5218c310699..16338ed9ca1 100644
--- a/src/features/FileViewer/Renderer/PDF/index.tsx
+++ b/src/features/FileViewer/Renderer/PDF/index.tsx
@@ -2,12 +2,11 @@

 import { Flexbox } from '@lobehub/ui';
 import { Fragment, memo, useCallback, useState } from 'react';
-import { Document, Page, pdfjs } from 'react-pdf';
 import 'react-pdf/dist/Page/AnnotationLayer.css';
 import 'react-pdf/dist/Page/TextLayer.css';

 import NeuralNetworkLoading from '@/components/NeuralNetworkLoading';
-import '@/libs/pdfjs/worker';
+import { Document, Page, pdfjs } from '@/libs/pdfjs';
 import { lambdaQuery } from '@/libs/trpc/client';

 import HighlightLayer from './HighlightLayer';
@@ -71,7 +70,7 @@ const PDFViewer = memo<PDFViewerProps>(({ url, fileId }) => {
           onLoadSuccess={onDocumentLoadSuccess}
           options={options}
         >
-          {Array.from({ length: numPages }, (el, index) => {
+          {Array.from({ length: numPages }, (_, index) => {
             const width = containerWidth ? Math.min(containerWidth, maxWidth) : maxWidth;

             return (
diff --git a/src/features/ShareModal/SharePdf/PdfPreview.tsx b/src/features/ShareModal/SharePdf/PdfPreview.tsx
index 6909e02b77a..d2ac7cbc6f8 100644
--- a/src/features/ShareModal/SharePdf/PdfPreview.tsx
+++ b/src/features/ShareModal/SharePdf/PdfPreview.tsx
@@ -7,10 +7,9 @@ import { createStaticStyles, cx } from 'antd-style';
 import { ChevronLeft, ChevronRight, Expand, FileText } from 'lucide-react';
 import { memo, useState } from 'react';
 import { useTranslation } from 'react-i18next';
-import { Document, Page } from 'react-pdf';

 import { useIsMobile } from '@/hooks/useIsMobile';
-import '@/libs/pdfjs/worker';
+import { Document, Page } from '@/libs/pdfjs';

 import { containerStyles } from '../style';

diff --git a/src/libs/pdfjs/index.tsx b/src/libs/pdfjs/index.tsx
new file mode 100644
index 00000000000..c95a6612ae3
--- /dev/null
+++ b/src/libs/pdfjs/index.tsx
@@ -0,0 +1,25 @@
+'use client';
+
+import type { ComponentProps } from 'react';
+import { Document as PdfDocument, Page as PdfPage, pdfjs } from 'react-pdf';
+
+const workerSrc = `https://registry.npmmirror.com/pdfjs-dist/${pdfjs.version}/files/build/pdf.worker.min.mjs`;
+
+function ensureWorker() {
+  if (!pdfjs.GlobalWorkerOptions.workerSrc) {
+    pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;
+  }
+}
+
+export type DocumentProps = ComponentProps<typeof PdfDocument>;
+export type PageProps = ComponentProps<typeof PdfPage>;
+
+export const Document = (props: DocumentProps) => {
+  ensureWorker();
+  return <PdfDocument {...props} />;
+};
+
+
+
+
+export {Page, pdfjs} from 'react-pdf';
\ No newline at end of file
diff --git a/src/libs/pdfjs/pdf.worker.ts b/src/libs/pdfjs/pdf.worker.ts
deleted file mode 100644
index fa2a939a6a0..00000000000
--- a/src/libs/pdfjs/pdf.worker.ts
+++ /dev/null
@@ -1 +0,0 @@
-import 'pdfjs-dist/build/pdf.worker.min.mjs';
diff --git a/src/libs/pdfjs/worker.ts b/src/libs/pdfjs/worker.ts
deleted file mode 100644
index 89cd3563d22..00000000000
--- a/src/libs/pdfjs/worker.ts
+++ /dev/null
@@ -1,12 +0,0 @@
-'use client';
-
-import { pdfjs } from 'react-pdf';
-
-pdfjs.GlobalWorkerOptions.workerSrc = `https://registry.npmmirror.com/pdfjs-dist/${pdfjs.version}/files/build/pdf.worker.min.mjs`;
-
-// TODO: Re-enable module worker when fully on Turbopack.
-// if (typeof Worker !== 'undefined' && !pdfjs.GlobalWorkerOptions.workerPort) {
-//   pdfjs.GlobalWorkerOptions.workerPort = new Worker(new URL('./pdf.worker.ts', import.meta.url), {
-//     type: 'module',
-//   });
-// }

GOLDPATCH_END

echo "Patch applied successfully."
