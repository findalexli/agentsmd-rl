# Megatron-to-HF conversion drops weights not in the Megatron checkpoint

## Problem

When converting partial Megatron-format model weights back to Hugging Face format using `tools/convert_torch_dist_to_hf.py`, the output checkpoint is incomplete. If only a subset of model layers was included in the Megatron checkpoint (e.g., a partial conversion of Qwen3.5), the remaining weights from the original HF model are silently dropped. The user already supplies `--origin-hf-dir` pointing at the full HF checkpoint, but the tool only uses that directory to copy non-weight files (tokenizer, config, etc.) — it never reads the `.safetensors` weight files from it.

## Expected Behavior

When the user opts in, `save_tensors` should look at the origin HF checkpoint's `.safetensors` files and include any weight tensors that were **not** produced by the Megatron conversion. Already-converted weights must keep their converted values; only genuinely missing weights should be pulled from the origin. The tool should also expose a CLI flag so users can enable this behavior.

## Files to Look At

- `tools/convert_torch_dist_to_hf.py` — the conversion script; `save_tensors()` writes the output safetensors files, and the `argparse` block at the bottom defines CLI arguments.
