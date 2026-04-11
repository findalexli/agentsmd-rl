# Fix PDF Worker Configuration Error with TurboPack

## Problem

PDF rendering in the application breaks with a "No GlobalWorkerOptions.workerSrc specified" error when using TurboPack as the bundler. The error occurs because the current approach relies on side-effect imports (`import '@/libs/pdfjs/worker'`) which TurboPack may optimize away, making the module execution order unpredictable with `'use client'` components.

## Files Involved

- `src/libs/pdfjs/` — PDF.js worker configuration module
- `src/features/FileViewer/Renderer/PDF/index.tsx` — PDF file viewer component
- `src/features/ShareModal/SharePdf/PdfPreview.tsx` — PDF preview in share modal
- `CLAUDE.md` — Project instructions (needs documentation update)

## Task

1. **Fix the PDF worker configuration** so that `pdfjs.GlobalWorkerOptions.workerSrc` is guaranteed to be set before any `Document` component renders. The current side-effect import approach is unreliable with TurboPack. Create a unified module that wraps the `Document` component and ensures worker configuration happens before render. Remove the old unreliable worker files.

2. **Update `CLAUDE.md`** — The Linear Issue Management section needs to be restructured. The current section is a single paragraph with vague instructions. It should be split into explicit **trigger conditions** (when to apply the workflow) and a clear numbered **workflow** with specific steps. Also update the section title to remove the parenthetical qualifier.

After fixing the code, update the relevant documentation in `CLAUDE.md` to reflect the improved Linear workflow instructions.
