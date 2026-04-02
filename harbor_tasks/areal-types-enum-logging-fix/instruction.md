# Bug: String concatenation bug in log message and logging convention violations

## Context

AReaL is a distributed RL training framework for LLM alignment. The `areal/experimental/openai/types.py` file defines `InteractionWithTokenLogpReward`, a dataclass that manages completions/responses with their rewards. The `areal/reward/clevr_count_70k.py` file implements a reward function for the CLEVR counting dataset.

## Issues

### 1. Implicit string concatenation bug in `types.py`

In the `to_tensor_dict` method of `InteractionWithTokenLogpReward`, there is a multi-line f-string log message where two adjacent string literals are implicitly concatenated without a space. This results in garbled log output where one sentence runs directly into the next (e.g., `"properly.Ignoring"`). Look at the `logger.warning()` call around the parent input length comparison logic.

### 2. Bare `print()` in reward function

In `areal/reward/clevr_count_70k.py`, the `clevr_count_70k_reward_fn` function uses a bare `print()` call to log correct matches. The project's logging conventions require using `areal.utils.logging.getLogger()` instead. Other reward modules like `gsm8k.py` and `geometry3k.py` already follow this convention.

### 3. String literals used where enums are expected

The `api_type` and `input_name_for_logging` properties in `InteractionWithTokenLogpReward` return raw string literals. There are existing TODO comments indicating these should use proper enum types (using `str, Enum` for backward compatibility). The lack of enum types makes the code less type-safe and harder to refactor.

## Files to modify

- `areal/experimental/openai/types.py`
- `areal/reward/clevr_count_70k.py`
