# Fix: Reply directive stripping destroys indentation

## Problem

Assistant replies that include inline reply directives such as `[[reply_to_current]]` are parsed through `parseInlineDirectives()`. That function replaces stripped directive tags with a space and then runs a broad whitespace normalization pass that collapses repeated spaces and trims both ends of the message. As a result, leading indentation is flattened before the reply payload reaches the Discord outbound layer.

This causes:
- Reply-tagged plain text lines to lose intended leading spaces
- Fenced code blocks routed through the reply-directive parser to lose indentation
- Python/YAML-style examples to become visually flattened before delivery

## Root Cause

The `normalizeDirectiveWhitespace()` function in `src/utils/directive-tags.ts` applies aggressive whitespace normalization:
- `/ +/g` replaces all multiple spaces with a single space
- Trims both ends of the message

The tag replacement itself always inserts a single space, even when the tag is at the start of a line where preserving surrounding whitespace matters.

## Expected Behavior

1. Replace directive tags with a word-boundary-aware replacement (space only when both sides are non-whitespace)
2. Update `normalizeDirectiveWhitespace()` to preserve leading indentation while still cleaning up directive-adjacent whitespace
3. Strip leading blank lines introduced by removed tags, but preserve indentation on content lines

## Files to Modify

- `src/utils/directive-tags.ts`
