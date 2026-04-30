# feat(cf-crawl): add modifiedSince support for incremental crawls

Source: [davila7/claude-code-templates#410](https://github.com/davila7/claude-code-templates/pull/410)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/utilities/cf-crawl/SKILL.md`

## What to add / change

Add diff detection between crawls using Cloudflare's modifiedSince parameter.
This enables daily doc-syncing by only re-crawling pages that changed since
the last crawl, instead of re-fetching everything.

- Add modifiedSince to parameter reference table
- Add --since argument for date/timestamp input
- Add incremental crawl usage example
- Add curl example with modifiedSince in Step 3
- Add skipped pages query in Step 5 for unchanged pages

https://claude.ai/code/session_01Qxuwmbk6PmooVat6XxizRZ

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds incremental crawl support to the `cf-crawl` skill using Cloudflare’s `modifiedSince` parameter. This speeds daily doc-syncs by only crawling pages changed since a given date.

- Area: components (`cli-tool/components/`) — updated `cf-crawl` docs
- Adds `--since` flag (date or Unix timestamp) mapped to `modifiedSince`; includes curl example and a query to list skipped (unchanged) pages
- No new components; catalog (`docs/components.json`) does not need regeneration
- No new environment variables or secrets

<sup>Written for commit e9403d137a31692b895d15cbaa2efa5096cf6436. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
