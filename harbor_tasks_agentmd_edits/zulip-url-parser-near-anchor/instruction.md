# Zulip URL parser fails on `near/` anchors

## Problem

The Zulip message fetching tool at `.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages` parses Zulip narrow URLs to extract the channel, topic, and optional anchor message ID. Currently, it only recognizes `with/ID` as the anchor syntax in URLs like:

```
https://chat.zulip.org/#narrow/channel/101-design/topic/hello/with/42
```

However, Zulip also generates URLs with `near/ID` syntax (e.g., when linking to a message within a topic). These URLs are rejected with an error, even though they carry the same meaning — pointing to a specific message in the conversation.

## Expected Behavior

The URL parser should accept both `with/ID` and `near/ID` anchor formats, returning the message ID in either case. The error message shown on invalid URLs should also reflect the updated format.

Additionally, the project's `.claude/CLAUDE.md` should be updated to document when and how to use this Zulip message fetching skill, so that AI agents know to use it instead of other tools when they encounter Zulip narrow URLs.

## Files to Look At

- `.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages` — the URL parsing script with `parse_zulip_url`
- `.claude/CLAUDE.md` — the agent instruction file that should document the Zulip URL handling guidance
