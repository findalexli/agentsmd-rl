# Fix Zulip URL parsing for near-links and update agent instructions

## Problem

The `fetch-zulip-web-public-messages` script in `.claude/skills/fetch-zulip-messages/` fails to parse Zulip narrow URLs that use the `near/MSG_ID` format. Zulip generates these URLs when linking to a specific message in context (as opposed to `with/MSG_ID` which highlights a single message). For example:

```
https://chat.zulip.org/#narrow/channel/101-design/topic/feature.20request/near/54321
```

The script exits with an error like "Could not parse Zulip narrow URL" for these links, even though they are valid Zulip URLs.

## Expected Behavior

The URL parser should accept both `with/MSG_ID` and `near/MSG_ID` anchor formats, extracting the message ID correctly in both cases. The error message shown on parse failure should also document the `near` format so users know it's supported.

## Additional Change

The project's `.claude/CLAUDE.md` should be updated to give agents guidance on how to handle Zulip chat link URLs — specifically, that they should use the `/fetch-zulip-messages` skill rather than `WebFetch`, which cannot access Zulip message content.

## Files to Look At

- `.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages` — the URL parsing script with the `parse_zulip_url` function
- `.claude/CLAUDE.md` — the main agent instruction file for the project
