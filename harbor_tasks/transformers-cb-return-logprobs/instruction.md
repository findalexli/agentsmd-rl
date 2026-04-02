# Continuous Batching: Log Probabilities Not Returned

## Problem

The continuous batching generation pipeline in `src/transformers/generation/continuous_batching/` does not support returning log probabilities alongside generated tokens. When a user calls `generate_batch()`, the resulting output objects always contain an empty `logprobs` list, even though the `GenerationOutput` dataclass has a `logprobs` field.

There was a prior attempt to add this via a `log_prob_generation` flag on the generation config, but it was never completed — it currently raises `NotImplementedError` in `ContinuousBatchingManager.__init__`.

## Expected Behavior

Users should be able to request log probabilities from the continuous batching pipeline. When enabled, the log probability of each generated token (i.e., the log of its softmax probability) should be computed during sampling and propagated through the pipeline so that `GenerationOutput.logprobs` contains the per-token log probabilities.

## Key Files

- `src/transformers/generation/configuration_utils.py` — `ContinuousBatchingConfig` dataclass (where the opt-in flag should live)
- `src/transformers/generation/continuous_batching/continuous_api.py` — `BatchProcessor._sample()` performs sampling, `BatchProcessor.update_batch()` distributes results to requests
- `src/transformers/generation/continuous_batching/input_outputs.py` — `ContinuousBatchingIOs` manages static tensors and batched I/O; `prepare_batch_update()` extracts generated tokens
- `src/transformers/generation/continuous_batching/requests.py` — `RequestState` tracks per-request state and produces `GenerationOutput` via `to_generation_output()`

## Hints

- The sampling method currently discards probability information after picking the next token. You'll need to retain and store it.
- The output tensor infrastructure needs to accommodate an additional row of data alongside token IDs.
- Log probabilities should flow from sampling → I/O manager → batch update → per-request state → generation output.
- The `fork()` and `create_equivalent_initial_request()` methods on `RequestState` must preserve any accumulated log probabilities.
- Consider that log probabilities are floats while token IDs are integers — the output storage currently uses integer tensors.
