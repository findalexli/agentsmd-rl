# feat(skill): channel-aware text formatting for WhatsApp, Telegram, Slack, and Signal

Source: [qwibitai/nanoclaw#1448](https://github.com/qwibitai/nanoclaw/pull/1448)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/channel-formatting/SKILL.md`

## What to add / change

## What

Adds a `channel-formatting` feature skill that converts Claude's Markdown output to each channel's native text syntax before delivery. Zero external dependencies — pure regex/string processing in a single new file (`src/text-styles.ts`).

| Channel | Native format | Transformation |
|---------|--------------|---------------|
| WhatsApp | `*bold*`, `_italic_` | `**bold**` → `*bold*`, `*italic*` → `_italic_`, headings → `*bold*`, links → `text (url)` |
| Telegram | `*bold*`, `_italic_` (Markdown v1) | same as WhatsApp |
| Slack | `*bold*`, `_italic_`, `<url\|text>` (mrkdwn) | same as WhatsApp, links → `<url\|text>` |
| Discord | Markdown | passthrough (renders Markdown natively) |
| Signal | native style ranges via signal-cli | passthrough — Signal channel calls `parseSignalStyles` directly |
| Emacs, Gmail, others | varies | passthrough — unknown channels are always passthrough |

Code blocks (fenced and inline) are always protected from transformation.

## Why

Claude outputs standard Markdown (`**bold**`, `*italic*`). WhatsApp, Telegram, and Slack each use a related but distinct syntax for native rendering. This skill converts Claude's output to the documented format for each platform at the pipeline level, so individual channel skills don't need to handle it independently.

For Signal, the conversion is different in kind: `src/text-styles.ts` exports `parseSignalStyles(text)`, which strips Markdown markers and returns `{ text: string, textStyle: SignalTextStyle[] }

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
