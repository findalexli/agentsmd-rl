## Bug: Article attachment downloads serve wrong file content

### Symptom

When downloading article attachments through the `/api/download/attachments/[fileId]` endpoint, the server sometimes returns the wrong file. The issue occurs when an attachment's `File.id` happens to match a `ModelFile.id` that is tracked in the storage resolver's `file_locations` table.

In that case, the download response contains the model file's content (e.g., a `.safetensors` model) while the `Content-Disposition` header shows the correct attachment filename. The user sees the right filename but downloads the wrong data.

For example, on article 24793, a `.json` workflow attachment was downloading a `.safetensors` model file because the attachment's `File.id` matched a `ModelFile.id` in the storage resolver.

### Root Cause

The attachment download endpoint resolves the download URL through the storage resolver, which only tracks `ModelFile` records in its `file_locations` table. General `File` table records (article attachments, bounty files) are never synced there. When a `File.id` collides with a `ModelFile.id`, the resolver returns the model file's location instead of the attachment's actual S3 URL.

The `src/utils/delivery-worker.ts` module provides two URL resolution functions:

- One that queries the storage resolver by numeric file ID (for model file downloads)
- One that resolves directly via the delivery worker using the file's S3 URL (for any file type)

The attachment endpoint currently uses the first approach, but attachments should use the second since `File` table records are not tracked by the storage resolver.

### Expected Behavior

- Attachment downloads must resolve using the file's actual S3 URL (the `File.url` column), not through the storage resolver lookup by numeric ID
- The function call should pass the file URL and filename only — do not pass the numeric `fileId` to the download URL resolver
- Model file downloads (other endpoints) should continue using the storage resolver as before — only the attachment endpoint needs to change

### Files to Investigate

- `src/pages/api/download/attachments/[fileId].ts` — the attachment download endpoint
- `src/utils/delivery-worker.ts` — download URL resolution utilities (exports both approaches)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
