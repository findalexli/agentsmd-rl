# fix(multimodal): trim oldest images instead of hard-failing

## Problem

When a conversation accumulates more images than the configured `max_images` limit, `prepare_messages_for_provider()` returns a hard error (`MultimodalError::TooManyImages`). This makes conversations permanently stuck once the cumulative image count crosses the threshold, since old images can never be removed.

## Root Cause

`prepare_messages_for_provider()` in `src/multimodal.rs` counts all image markers across all messages and immediately returns an error if the count exceeds `max_images`. There is no mechanism to gracefully handle the excess by trimming older images.

## Expected Fix

1. Instead of returning an error when `total_images > max_images`, implement a `trim_old_images()` function that strips image markers from the oldest user messages first, preserving the most recent (most relevant) images.
2. The trimming should:
   - Only strip images from user messages (leave assistant messages untouched)
   - Remove images from oldest messages first
   - Keep the text content of trimmed messages (replace image-only messages with a placeholder like `"[image removed from history]"`)
   - Work at message granularity (strip all images from a message, not individual images)
3. After trimming, proceed with normal image normalization for surviving images.

## Files to Modify

- `src/multimodal.rs`
