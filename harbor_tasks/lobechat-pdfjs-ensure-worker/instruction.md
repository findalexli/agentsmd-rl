# Fix PDF Worker Configuration Error with TurboPack

## Problem

PDF rendering in the application breaks with a "No GlobalWorkerOptions.workerSrc specified" error when using TurboPack as the bundler. The current approach relies on side-effect imports (`import '@/libs/pdfjs/worker'`) to configure the PDF.js worker, but TurboPack may optimize away these imports, making the module execution order unpredictable with `'use client'` components.

Two PDF viewer components are affected:
- The PDF file viewer at `src/features/FileViewer/Renderer/PDF/index.tsx`
- The PDF preview at `src/features/ShareModal/SharePdf/PdfPreview.tsx`

Both currently import `Document` and `Page` directly from `react-pdf` and use a side-effect import from `@/libs/pdfjs/worker` to set up the worker — a pattern that is unreliable with TurboPack.

## Task

### Part 1: Fix PDF Worker Configuration

Create a unified PDF.js module at `src/libs/pdfjs/index.tsx` that guarantees the PDF.js worker is configured before any `Document` component renders. The module should:

- Set `pdfjs.GlobalWorkerOptions.workerSrc` to a worker URL pointing to `pdf.worker.min.mjs` from `pdfjs-dist` on the npmmirror CDN (`registry.npmmirror.com/pdfjs-dist`), with the installed pdfjs version interpolated into the URL path via a template literal.
- Export a `Document` wrapper component that applies the worker configuration before rendering the underlying PDF document.
- Re-export `Page` and `pdfjs` from `react-pdf` so consuming components have a single import source.

Update the affected PDF viewer components to:
- Import `Document`, `Page`, (and `pdfjs` where needed) from the unified `@/libs/pdfjs` module instead of directly from `react-pdf`
- Remove the old side-effect worker imports (`@/libs/pdfjs/worker`)

Delete the old worker files that are no longer needed:
- `src/libs/pdfjs/worker.ts`
- `src/libs/pdfjs/pdf.worker.ts`

### Part 2: Update CLAUDE.md Documentation

Restructure the Linear Issue Management section in `CLAUDE.md`. Replace the current paragraph-style description with a structured format that includes:
- Trigger conditions listing when the Linear workflow should be applied (e.g., issue ID mentions like `LOBE-XXX`, "linear" keyword usage, PR references to Linear issues)
- A "Workflow:" subsection with numbered steps, starting with using `ToolSearch` to confirm the `linear-server` MCP tool is available
