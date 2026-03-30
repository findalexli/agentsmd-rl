# Fix benchmark generating empty prompts when random_input_len is small

## Bug Description

The `sample_random_requests` function in `python/sglang/benchmark/datasets/random.py` generates empty prompts when `random_input_len` is small (e.g., 1). The function subtracts the number of special tokens from each input length using `max(0, input_lens[i] - num_special_tokens)`. When the input length equals the number of special tokens, the result is 0, producing a zero-length token sequence. The tokenizer then decodes an empty list to an empty string, and the server rejects it with:

```
ValueError: texts cannot be empty and tokenizer must be initialized
```

This was observed in CI when running `test_pp_offline_throughput_default_decode` which uses `random_input_len=1`.

## Expected Fix

Ensure that input lengths after adjusting for special tokens are always at least 1 token long, so that no empty prompts are ever generated. The fix should be minimal and contained to the adjustment loop in `sample_random_requests`.

## File to Modify

`python/sglang/benchmark/datasets/random.py` -- the `sample_random_requests` function, specifically the line that clamps `input_lens[i]`.
