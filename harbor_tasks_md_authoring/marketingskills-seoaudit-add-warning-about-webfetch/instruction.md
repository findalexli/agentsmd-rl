# seo-audit: Add warning about web_fetch unable to detect JS-rendered schema markup

Source: [coreyhaines31/marketingskills#53](https://github.com/coreyhaines31/marketingskills/pull/53)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/seo-audit/SKILL.md`

## What to add / change

## Problem

`web_fetch` strips `<script>` tags during HTML→markdown conversion, which silently discards JSON-LD schema blocks. Additionally, many CMS plugins (AIOSEO, Yoast, RankMath) inject schema via client-side JavaScript, making it invisible to both `web_fetch` and `curl`.

## Real-world impact

We ran an automated SEO audit on a client site (noladetox.com) using this skill. The audit reported **"zero structured data / schema markup on the entire site."** The site actually has Organization, Article, BreadcrumbList, LocalBusiness, FAQPage, and more — all injected via AIOSEO.

This led to an incorrect audit finding that had to be manually corrected after the client validated with Google Rich Results Test and Screaming Frog.

## Changes

1. Added a **⚠️ Important** warning section in the Audit Framework, before the Priority Order, explaining the limitation and listing reliable alternatives (browser tool, Rich Results Test, Screaming Frog)
2. Added a note in the **Tools Referenced** section highlighting that Rich Results Test renders JavaScript and should be used for schema validation

## Related

- OpenClaw issue: https://github.com/openclaw/openclaw/issues/17137 (requesting web_fetch preserve JSON-LD)

Thanks for the great skills library — this is a small but important accuracy fix for anyone doing SEO audits with AI agents.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
