# feat: inline markdown links on narrative citations

Source: [mvanhorn/last30days-skill#289](https://github.com/mvanhorn/last30days-skill/pull/289)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

Inverts the citation rule so every @handle, r/sub, publication, YouTube channel, TikTok/Instagram creator, and Polymarket market cited in the narrative body and KEY PATTERNS is an inline markdown link `[name](url)` — URL pulled from the raw research dump. Claude Code renders `[text](url)` as blue CMD-clickable text with the URL hidden.

Plain text remains the fallback for sources the raw data has no URL for. Raw URL strings remain forbidden. Broken empty `[name]()` links are explicitly called out as bad.

## Scope (intentionally narrow)

- CITATION PRIORITY list shows each item as a markdown link.
- URL FORMATTING rule flipped from "NEVER paste raw URLs" to "every citation is `[name](url)`, never a raw URL string".
- BAD / GOOD narrative examples updated with linked @handles and r/subs.
- What-I-learned / KEY PATTERNS template placeholders updated.
- One sentence noting the engine-emitted stats footer (LAW 5) is pass-through only — the agent does NOT format its links.

## Does NOT touch

LAWs 1-7, deterministic engine footer and PASS-THROUGH FOOTER boundaries, comparison scaffold, mandatory-badge rule, em-dash/en-dash prohibition, no-## header rule, or any other existing structural enforcement. The whole output contract hardening that landed in PR #285 and subsequent commits stays intact.

## Why a fresh branch

Prior attempt (PR #286, closed) branched off a stale main and accumulated three failed prompt-enforcement amendments — none of which were needed once I sa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
