# Qwen-VL FSDP Rope Index Failures

## Bug Report

When running GRPO multimodal training with Qwen-VL models (e.g., Qwen2.5-VL or Qwen3-VL) using the FSDP engine, training crashes during the micro-batch preparation step with one of two errors depending on the model variant:

### Error 1: Argument binding ambiguity

The `get_rope_index` method has different signatures across Qwen-VL model variants. One variant accepts `second_per_grid_ts` as the 4th positional parameter while another does not. The current code in `_prepare_mb_list` passes arguments positionally, which can cause the 4th argument (`attention_mask`) to be bound to the wrong parameter depending on which model is loaded.

### Error 2: Dtype mismatch

```
RuntimeError: Index put requires the source and destination dtypes match,
got Int for the destination and Long for the source.
```

When `input_ids` has dtype `int32`, the `position_ids` tensor returned by `get_rope_index` inherits that dtype. However, internal indexed-assignment operations within the method use `int64` sources, causing a dtype mismatch crash.

## Affected Code

- File: `areal/engine/fsdp_engine.py`
- Method: `FSDPEngine._prepare_mb_list`
- Look for the `is_qwen_vl_model` branch that calls `self.model.model.get_rope_index(...)`

## Expected Behavior

- The `get_rope_index` call should work correctly regardless of which Qwen-VL model variant is loaded
- `input_ids` dtype should be normalized before passing to `get_rope_index` to prevent dtype mismatch in indexed assignment operations
