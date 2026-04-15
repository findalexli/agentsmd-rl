# Fix PDF Worker Configuration Error with TurboPack

## Problem

PDF rendering in the application breaks with a "No GlobalWorkerOptions.workerSrc specified" error when using TurboPack as the bundler. The error occurs because the current approach relies on side-effect imports (`import '@/libs/pdfjs/worker'`) which TurboPack may optimize away, making the module execution order unpredictable with `'use client'` components.

## Files Involved

- `src/libs/pdfjs/index.tsx` — PDF.js worker configuration module (to be created)
- `src/libs/pdfjs/worker.ts` — Old side-effect worker file (to be removed)
- `src/libs/pdfjs/pdf.worker.ts` — Unused worker entry (to be removed)
- `src/features/FileViewer/Renderer/PDF/index.tsx` — PDF file viewer component
- `src/features/ShareModal/SharePdf/PdfPreview.tsx` — PDF preview in share modal
- `CLAUDE.md` — Project instructions (needs documentation update)

## Task

### Part 1: Fix PDF Worker Configuration

Create a unified module at `src/libs/pdfjs/index.tsx` that wraps the `Document` component and ensures `pdfjs.GlobalWorkerOptions.workerSrc` is set before any `Document` renders. The module must:

1. Define a `const workerSrc` template literal using the format `https://registry.npmmirror.com/pdfjs-dist/${pdfjs.version}/files/build/pdf.worker.min.mjs` (interpolate the pdfjs version)
2. Define an `ensureWorker()` function that checks if `pdfjs.GlobalWorkerOptions.workerSrc` is set, and if not, assigns it the `workerSrc` value
3. Export a wrapper `Document` component that calls `ensureWorker()` in its body before rendering
4. Export `Page` and `pdfjs` from react-pdf

Update the PDF viewer components to:
- Import `Document` and `Page` from `@/libs/pdfjs` instead of directly from `react-pdf`
- Remove any imports of `@/libs/pdfjs/worker` (the old side-effect import)

Remove the old unreliable worker files:
- Delete `src/libs/pdfjs/worker.ts`
- Delete `src/libs/pdfjs/pdf.worker.ts`

### Part 2: Update CLAUDE.md Documentation

The Linear Issue Management section needs restructuring to match the format used elsewhere in the documentation:

1. Update the section heading to remove the parenthetical qualifier
2. Add a "Trigger condition" subsection listing when to apply the Linear workflow (issue ID mentions, "linear" keyword, PR references)
3. Add a "Workflow:" subsection with numbered steps
4. Step 1 must mention using `ToolSearch` to discover the `linear-server` MCP tool

The restructured section should provide explicit criteria for when to apply the workflow and clear steps to follow.
