# Continuous Batching: Log Probabilities Not Returned

## Problem

The continuous batching generation pipeline in `src/transformers/generation/continuous_batching/` does not support returning log probabilities alongside generated tokens. When a user calls `generate_batch()`, the resulting output objects always contain an empty `logprobs` list, even though the `GenerationOutput` dataclass has a `logprobs` field.

There was a prior attempt to add this via a flag on the generation config, but it was never completed — it currently raises `NotImplementedError` in `ContinuousBatchingManager.__init__`.

## Expected Behavior

Users should be able to request log probabilities from the continuous batching pipeline. When enabled via configuration, the log probability of each generated token (i.e., the log of its softmax probability) should be computed during sampling and propagated through the pipeline so that `GenerationOutput.logprobs` contains the per-token log probabilities.

## Key Files

- `src/transformers/generation/configuration_utils.py` — `ContinuousBatchingConfig` dataclass (where the opt-in flag should live)
- `src/transformers/generation/continuous_batching/continuous_api.py` — `BatchProcessor._sample()` performs sampling, `BatchProcessor.update_batch()` distributes results to requests
- `src/transformers/generation/continuous_batching/input_outputs.py` — `ContinuousBatchingIOs` manages static tensors and batched I/O; `prepare_batch_update()` extracts generated tokens
- `src/transformers/generation/continuous_batching/requests.py` — `RequestState` tracks per-request state and produces `GenerationOutput` via `to_generation_output()`

## Specific Requirements

The following attribute names, method signatures, and behaviors must be implemented exactly as specified:

1. **Configuration flag**: `ContinuousBatchingConfig` must expose an attribute named `return_logprobs` that defaults to `False`. Users can set `return_logprobs=True` to enable log probability computation.

2. **Request state storage**: `RequestState` must store accumulated log probabilities in an attribute named `logprobs`. This attribute should be initialized appropriately when a `RequestState` is created.

3. **Update method signature**: The `update_and_check_completion` method on `RequestState` must accept a two-argument signature `(token_id, logprob)` where:
   - `token_id` is the generated token ID (integer)
   - `logprob` is the log probability of that token (float), or `None` when logprobs are disabled

4. **Logprob propagation**: Log probabilities must flow from sampling → I/O manager → batch update → per-request state → generation output. Each step in this chain must be updated to handle the additional logprob data alongside token IDs.

5. **Fork preservation**: The `fork()` method on `RequestState` must copy accumulated log probabilities to the new state, maintaining independence (modifications to the fork's logprobs should not affect the original).

6. **Equivalent request preservation**: The `create_equivalent_initial_request()` method on `RequestState` must preserve accumulated log probabilities in the returned request, also maintaining independence.

7. **Output generation**: The `to_generation_output()` method must include the accumulated log probabilities in the returned `GenerationOutput` object's `logprobs` field.

8. **Backward compatibility**: When `logprob=None` is passed to `update_and_check_completion`, the system should handle it gracefully without breaking token generation.

## Hints

- The sampling method currently discards probability information after picking the next token. You'll need to retain and store it.
- The output tensor infrastructure needs to accommodate an additional row of data alongside token IDs.
- Consider that log probabilities are floats while token IDs are integers — the output storage currently uses integer tensors.
- When `RequestStatus` is `DECODING`, the request is actively generating new tokens and receiving logprobs.
