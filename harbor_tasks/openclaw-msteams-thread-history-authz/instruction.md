# MS Teams: Thread history bypasses sender allowlist

## Bug

When the MS Teams channel plugin is configured with `groupPolicy: "allowlist"`, incoming channel messages from non-allowlisted senders are correctly rejected. However, when a channel message is a reply inside a thread, the handler fetches the full thread history (parent message + replies) and includes **all** of it in the `BodyForAgent` context payload — regardless of whether each historical message was sent by an allowlisted user.

This means a non-allowlisted user can post a message in a channel thread, and that message content will be forwarded to the agent as part of the thread context when an allowlisted user replies in the same thread.

## Impact

An attacker who is not on the allowlist can inject arbitrary content into the agent's context by posting in a channel thread, then waiting for an allowlisted user to reply. This defeats the purpose of the sender allowlist as a security boundary.

## Where to look

- `extensions/msteams/src/monitor-handler/message-handler.ts` — the handler function that processes incoming messages. Look at the section that fetches thread history (around the `fetchChannelMessage` / `fetchThreadReplies` calls) and constructs the thread context before dispatching.
- `extensions/msteams/src/policy.ts` — contains the allowlist matching logic already used for gating the incoming message sender.

## Expected behavior

When `groupPolicy` is `"allowlist"`, thread history messages should be filtered through the same sender allowlist before being included in `BodyForAgent`. Messages from non-allowlisted users should be excluded from the thread context.

The existing allowlist matching logic (including `dangerouslyAllowNameMatching` for display-name-based matching) should be reused for consistency.
