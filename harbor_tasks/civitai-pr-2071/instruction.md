# Article Attachment Download Bug Fix

## Problem

Article attachment downloads on Civitai are serving **incorrect file content** when a `File.id` collides with a `ModelFile.id` in the storage resolver's `file_locations` table.

### Example Scenario

When a `.json` workflow attachment on article 24793 is downloaded, users receive a `.safetensors` model file instead — despite the `content-disposition` header showing the correct attachment filename. The file *name* is correct but the file *content* is wrong.

### Root Cause

The storage resolver's `file_locations` table only tracks `ModelFile` records. It does **not** sync `File` table records (which include article attachments, bounty files, etc.). When a `File.id` happens to match a `ModelFile.id`, the resolver matches against the wrong record and returns the wrong S3 URL — but the filename from the attachment record is preserved in headers.

### Affected Endpoint

`src/pages/api/download/attachments/[fileId].ts` — the API route for downloading article attachments.

## Your Task

Fix the attachment download endpoint so that the correct file content is served, even when a `File.id` happens to match a `ModelFile.id`.

### Constraints

- The fix must not break model file downloads (which should continue to use `resolveDownloadUrl`)
- The delivery worker (`src/utils/delivery-worker.ts`) already has a function that resolves by URL, not by ID — use it directly

### Verification

After applying your fix:
1. Article attachment downloads must serve the correct file content (URL resolves via the file's actual S3 URL, not via storage resolver ID matching)
2. Model file downloads must remain unaffected

### Files to Examine

- `src/pages/api/download/attachments/[fileId].ts` — the attachment download endpoint
- `src/utils/delivery-worker.ts` — the delivery worker utility functions

Look at the function signatures in `delivery-worker.ts` to understand which function resolves by URL rather than by ID.
