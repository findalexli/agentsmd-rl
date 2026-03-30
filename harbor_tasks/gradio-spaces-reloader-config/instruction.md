# Fix: SpacesReloader does not re-assign config after swapping blocks

## Problem

When using the Gradio reload/hot-swap feature on Hugging Face Spaces, swapping blocks causes a Jinja template rendering error. The `SpacesReloader` class detects when a demo has changed and calls `swap_blocks`, but it does not regenerate the config file for the new demo. This causes the frontend to use the old config, leading to Jinja errors when the template tries to render with mismatched configuration.

## Root Cause

The `SpacesReloader` class in `gradio/utils.py` overrides the `postrun` method from its parent class. When a demo change is detected, it calls `swap_blocks(demo)` from the parent. However, it does not regenerate `demo.config` after the swap. The parent class's `swap_blocks` method does not call `get_config_file()` either, so the config becomes stale.

## Expected Fix

The `SpacesReloader` class should override `swap_blocks` to call the parent implementation and then regenerate the config by calling `demo.config = demo.get_config_file()`.

## Files to Investigate

- `gradio/utils.py` -- the `SpacesReloader` class and its `swap_blocks`/`postrun` methods
