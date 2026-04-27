# Add cf-proxy skill: free VLESS proxy on Cloudflare Pages

Source: [davepoon/buildwithclaude#112](https://github.com/davepoon/buildwithclaude/pull/112)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/cf-proxy/SKILL.md`

## What to add / change

## Summary

- Adds a new **cf-proxy** skill that automates deploying a free VLESS proxy node on Cloudflare Pages using edgetunnel
- Walks users through the full setup: code download, credential generation, Pages deployment, free domain registration (DNSExit), DNS configuration, custom domain binding, and client setup
- Key insight: uses Cloudflare **Pages** instead of Workers because Pages supports CNAME-based custom domains from any DNS provider

## Component Details

- **Name**: cf-proxy
- **Type**: Skill
- **Category**: infrastructure-operations
- **Location**: `plugins/all-skills/skills/cf-proxy/SKILL.md`

## Example Usages

1. "Help me set up a free Cloudflare proxy node" — runs the full 7-phase automated setup
2. "Fix my Cloudflare proxy — Shadowrocket can't connect" — triggers troubleshooting workflow
3. "Deploy edgetunnel with my own domain" — skips free domain registration, uses user's domain

## Testing Checklist

- [x] SKILL.md follows the required frontmatter format (name, category, description)
- [x] Tested the full deployment workflow end-to-end
- [x] No overlap with existing skills in the repository
- [x] Documentation includes architecture diagram, limitations, troubleshooting, and tips

## Source

- GitHub repo: https://github.com/LewisLiu007/cf-proxy
- Also available via: `npx skills add LewisLiu007/cf-proxy`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
