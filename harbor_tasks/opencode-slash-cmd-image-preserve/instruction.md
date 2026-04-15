# Bug: Slash command selection clears image attachments

## Summary

When a user has image attachments in the prompt input and then selects a slash command (either custom or built-in), all image attachments are silently removed from the prompt state. Users lose their pasted screenshots or uploaded images whenever they invoke a slash command.

## Reproduction

1. Paste or attach one or more images into the prompt input
2. Type `/` to open the slash command popover
3. Select any slash command (custom or built-in)
4. Observe that the image attachments are gone

## Technical Context

The prompt input component manages its content as an array of typed parts. Each content part has a `type` field — the relevant types are:

- `"text"` — text content with `content`, `start`, and `end` fields
- `"image_attachment"` — image attachments with a `url` field (and `start`/`end`)

The component provides these key functions used during slash command handling:

- `imageAttachments()` — returns the current array of image attachment content parts
- `prompt.set(parts, cursorPosition)` — sets the prompt's content parts array and cursor position
- `closePopover()` — closes the slash command popover
- `clearEditor()` — clears the editor text
- `setEditorText(text)` — sets the editor text to the given string
- `focusEditorEnd()` — moves focus to the end of the editor
- `promptProbe.select(id)` — selects a command probe by id
- `command.trigger(id, source)` — triggers a command by id with a source string
- `DEFAULT_PROMPT` — a constant representing the default prompt content (an array with a single empty text part)

When a slash command is selected with `undefined` or no argument, the handler should return early without calling `prompt.set`, `closePopover`, or any other side-effect functions.

For built-in commands, `command.trigger` must be called with the command's `id` and the string `"slash"`.

## Expected Behavior

Selecting a slash command should preserve any existing image attachments in the prompt. Only the text portion of the prompt should be modified by the slash command selection. After the fix, `prompt.set` should be called with a parts array that includes both the new text content and all existing `"image_attachment"` parts.
