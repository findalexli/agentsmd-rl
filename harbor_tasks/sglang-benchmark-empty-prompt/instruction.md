# Fix: Benchmark generates empty prompts when random_input_len is small

## Problem

The benchmark dataset generator in `python/sglang/benchmark/datasets/random.py` has a bug in the `sample_random_requests` function. When `random_input_len` is small enough that subtracting the number of special tokens results in a value of 0, the function generates empty prompts (zero-length token sequences). This causes downstream failures when the benchmark tries to run with these empty inputs.

## Root Cause

The function adjusts input lengths by subtracting the number of special tokens from the tokenizer, but uses `max(0, ...)` to clamp the result. This means the adjusted length can be exactly 0, producing an empty prompt.

## Expected Fix

Ensure that input lengths after adjusting for special tokens are always at least 1 token long, so that no empty prompts are ever generated.

## File to Modify

- `python/sglang/benchmark/datasets/random.py` -- the `sample_random_requests` function
