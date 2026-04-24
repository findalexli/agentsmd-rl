# SmolLM3 Integration Tests Produce Non-Deterministic Output

## Problem

The `SmolLM3IntegrationTest` tests in `tests/models/smollm3/test_modeling_smollm3.py` are failing intermittently. The tests (`test_model_3b_generation` and `test_model_3b_long_prompt`) attempt to perform greedy (deterministic) text generation and compare against expected output, but the generated text doesn't match the expected strings.

## Context

The SmolLM3 model has a non-standard default generation configuration shipped on the Hub (`generation_config.json`). The integration tests attempt to perform greedy decoding, but the way they request deterministic generation does not properly account for the model's default config settings. As a result, the tests produce different outputs across runs.

## Relevant Files

- `tests/models/smollm3/test_modeling_smollm3.py` — the `SmolLM3IntegrationTest` class, specifically:
  - `test_model_3b_generation` (line ~102): calls `model.generate()` for greedy text completion
  - `test_model_3b_long_prompt` (line ~118): calls `model.generate()` twice (normal + assisted generation)

## Expected Behavior

The integration tests should produce deterministic, reproducible text generation output so that string/token comparisons are reliable across runs.

## Test Requirements

The following conditions must all be satisfied for the tests to pass:

1. **`test_model_3b_generation` expected text**: The old expected text fragment `"pulls objects toward the center of the Earth"` must not appear in the test method `test_model_3b_generation`. (This text was generated under non-deterministic conditions and must be updated.)

2. **Greedy decoding parameter**: All `generate()` calls in `test_model_3b_generation` and `test_model_3b_long_prompt` (3 or more calls total) must include `do_sample=False` as an explicit keyword argument with literal value `False`. The model's `generation_config.json` has `do_sample=True` by default; without this explicit parameter, greedy decoding is not guaranteed.

3. **No temperature parameter**: The `temperature` keyword argument must not appear in any `generate()` call in the affected test methods. Using `temperature=0` does not override `do_sample=True` from the model's default generation config.

## Hints

- Look at how the `generate()` calls request deterministic output
- Check the model's `generation_config.json` on the Hub to understand its defaults
- Consider whether the parameters passed to `generate()` fully override the model's default generation behavior
- The fix should ensure greedy decoding is explicitly and reliably requested

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
