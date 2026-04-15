# Fix: Reply directive stripping destroys indentation

## Problem

Assistant replies that include inline reply directives such as `[[reply_to_current]]` are parsed through `parseInlineDirectives()`. That function replaces stripped directive tags and then runs a whitespace normalization pass. As a result, leading indentation is flattened before the reply payload reaches the Discord outbound layer.

This causes:
- Reply-tagged plain text lines to lose intended leading spaces
- Fenced code blocks routed through the reply-directive parser to lose indentation
- Python/YAML-style examples to become visually flattened before delivery

## Expected Behavior

`parseInlineDirectives()` returns an object with two fields:
- `hasReplyTag` — boolean indicating whether a reply tag was found
- `text` — string with all directive tags stripped

Behavior requirements:

1. **Return fields**: For `[[reply_to_current]] hello world`, return `{hasReplyTag: true, text: "hello world"}`. For `[[reply_to: msg-123]] greetings`, return `{hasReplyTag: true, text: "greetings"}`. For untagged `just plain text`, return `{hasReplyTag: false, text: "just plain text"}`.

2. **Indentation preservation**: The `text` field must preserve leading indentation on content lines. `[[reply_to_current]]    indented text` must produce `text` containing `"    indented text"` (4-space indent intact). `[[reply_to_current]]  line one\n      line two\n  line three` must preserve 2-space and 6-space indentation. Code blocks (Python, JS, YAML, tab-indented) must retain their nested indentation after tag stripping.

3. **Word-boundary space insertion**: When a tag appears between two non-whitespace characters, the tag is replaced with a single space. `see[[reply_to_current]]now` → `"see now"`. When the tag is at the start of input with no preceding character, no leading space is added. When the tag is at the end with no trailing character, no trailing space is added.

4. **Leading blank line stripping**: Empty lines introduced by tag removal at the start are stripped, but interior blank lines are preserved. `[[reply_to_current]]\n\ntext after blanks` → `"text after blanks"`.

5. **Real implementation**: The file must contain substantial logic (not a stub); it must export `parseInlineDirectives`. The solution must pass the repo's lint, format-check, typecheck, and unit tests for this file.

## Files to Modify

- `src/utils/directive-tags.ts`