# Bug: Slash command selection clears image attachments

## Summary

When a user has image attachments in the prompt input and then selects a slash command (either custom or built-in), all image attachments are silently removed from the prompt state. This means users lose their pasted screenshots or uploaded images whenever they invoke a slash command.

## Reproduction

1. Paste or attach one or more images into the prompt input
2. Type `/` to open the slash command popover
3. Select any slash command (custom or built-in)
4. Observe that the image attachments are gone

## Relevant Code

The issue is in `packages/app/src/components/prompt-input.tsx`, specifically in the `handleSlashSelect` function. This function handles what happens when a user picks a slash command from the popover.

The prompt state is managed through a `prompt.set()` call that accepts an array of `ContentPart` items and a cursor position. Image attachments are stored as `ImageAttachmentPart` entries in the prompt's content parts array.

The prompt context (`packages/app/src/context/prompt.tsx`) defines the `ContentPart` types including `ImageAttachmentPart`, and a `DEFAULT_PROMPT` constant used for resetting state.

## Expected Behavior

Selecting a slash command should preserve any existing image attachments in the prompt. Only the text portion of the prompt should be modified by the slash command selection.
