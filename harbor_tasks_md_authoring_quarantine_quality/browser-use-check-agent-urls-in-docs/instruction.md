# Check agent urls in docs

Source: [browser-use/browser-use#3714](https://github.com/browser-use/browser-use/pull/3714)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Convert all shortcut and relative URLs to full URLs in `AGENTS.md` for consistency and robustness.

---
[Slack Thread](https://browser-use.slack.com/archives/C08SZRT860M/p1764777500203789?thread_ts=1764777500.203789&cid=C08SZRT860M)

<a href="https://cursor.com/background-agent?bcId=bc-d05fbe93-a8fa-4df6-bacf-38d9aae8db3d"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/open-in-cursor-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/open-in-cursor-light.svg"><img alt="Open in Cursor" src="https://cursor.com/open-in-cursor.svg"></picture></a>&nbsp;<a href="https://cursor.com/agents?id=bc-d05fbe93-a8fa-4df6-bacf-38d9aae8db3d"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/open-in-web-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/open-in-web-light.svg"><img alt="Open in Web" src="https://cursor.com/open-in-web.svg"></picture></a>





<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Replaced all relative and shortcut links in AGENTS.md with full absolute URLs to ensure links work reliably across GitHub and the docs site. Prevents broken or ambiguous links, improving doc consistency.

<sup>Written for commit a7498839ac933c27bc5e62723506be83419e874f. Summary will update automatically on new commits.</sup>

<!-- End of auto-generated description by cubic. -->



<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Convert rela

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
