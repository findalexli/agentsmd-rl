# Add upsert-pr-comment.mjs script for PR bundle-size comments

## Problem

The repository needs a Node.js CLI script to manage PR comments on GitHub for bundle-size benchmark reporting. This script doesn't exist yet and needs to be created at `scripts/benchmarks/common/upsert-pr-comment.mjs`.

## Requirements

Create a script that:

1. **Parses CLI arguments** using Node.js's built-in `util.parseArgs`:
   - `--pr` (required): PR number as integer
   - `--body-file` (required): Path to file containing comment body
   - `--repo` (optional): Repository in `owner/repo` format (falls back to `GITHUB_REPOSITORY` env var)
   - `--token` (optional): GitHub token (falls back to `GITHUB_TOKEN` or `GH_TOKEN` env vars)
   - `--marker` (optional): Marker string to identify the comment (default: `<!-- bundle-size-benchmark -->`)
   - `--api-url` (optional): GitHub API URL (falls back to `GITHUB_API_URL` env var, default: `https://api.github.com`)

2. **Validates required arguments** and throws descriptive errors if missing or invalid.

3. **Makes authenticated GitHub API requests** with proper headers:
   - `Authorization: Bearer <token>`
   - `Accept: application/vnd.github+json`
   - `User-Agent: tanstack-router-bundle-size-bot`
   - `Content-Type: application/json`

4. **Lists issue comments** with pagination support (100 per page).

5. **Finds existing comments** by searching for the marker string in comment bodies.

6. **Creates or updates comments**:
   - If a comment with the marker exists, PATCH it
   - Otherwise, POST a new comment
   - Prepends the marker to the body if not already present

7. **Outputs status** to stdout indicating whether a comment was created or updated.

## Key Implementation Details

- The script should use ES modules (`import` syntax)
- Use `node:fs/promises` for file operations
- Use `node:path` for path resolution
- Use `node:util` for argument parsing
- Handle the GitHub API pagination pattern properly
- Include proper error handling with process.exit(1) on failure

## Files to Modify

Create the file `scripts/benchmarks/common/upsert-pr-comment.mjs` with the complete implementation.
