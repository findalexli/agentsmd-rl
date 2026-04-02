# Bug: `debug.num_layers` crashes for vision-language models

## Summary

The `get_model()` function in `src/prime_rl/trainer/model.py` has a `debug.num_layers` feature that lets you truncate the model to fewer layers for quick validation runs. This works fine for standard language models, but crashes with an `AttributeError` when used with vision-language models (VLMs).

## Reproduction

Set `debug.num_layers` to any value (e.g., `4`) in a config for a VLM model like Qwen2-VL or any model whose HuggingFace config nests `num_hidden_layers` inside a `text_config` sub-config rather than at the top level.

The trainer will crash during model setup:

```
AttributeError: 'SomeVLMConfig' object has no attribute 'num_hidden_layers'
```

## Root cause

The `debug.num_layers` code block (around line 250 in `model.py`) reads and writes `model_config.num_hidden_layers` directly. For standard language models this works because `num_hidden_layers` is a top-level attribute. But VLM model configs from HuggingFace store the text model's layer count under `model_config.text_config.num_hidden_layers` — the top-level config object doesn't have this attribute at all.

The same code also logs a warning message referencing the layer count, and that log line has the same problem.

## Expected behavior

The `debug.num_layers` feature should work for both standard language models and VLMs. For VLMs, it should read and write the layer count on the correct sub-config object.

## Relevant files

- `src/prime_rl/trainer/model.py` — the `get_model()` function, specifically the `debug.num_layers` block
