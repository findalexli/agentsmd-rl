# Fix: Flux2-Klein prompt tokenization truncated at 77 tokens

## Problem

Flux2-Klein uses a Qwen3/Mistral-style text encoder path where the inherited Flux1 CLIP-style `max_length=77` is incorrect and truncates long prompts. The old behavior came from inherited `text_encoder_extra_args` from the parent `FluxPipelineConfig`.

## Root Cause

`Flux2PipelineConfig` inherits `text_encoder_extra_args` from `FluxPipelineConfig`, which sets `max_length=77` (appropriate for CLIP). The `Flux2KleinPipelineConfig.tokenize_prompt` method also accepts an inbound `max_length` from merged kwargs that can silently reintroduce the 77 limit.

## Expected Behavior

1. Override `text_encoder_extra_args` in `Flux2PipelineConfig` to use `max_length=512`
2. Harden `Flux2KleinPipelineConfig.tokenize_prompt` to explicitly enforce `max_length=512` and ignore conflicting inbound max_length values

## Files to Modify

- `python/sglang/multimodal_gen/configs/pipeline_configs/flux.py`
