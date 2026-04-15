# Bug: String concatenation bug in log message and logging convention violations

## Context

AReaL is a distributed RL training framework for LLM alignment. The `areal/experimental/openai/types.py` file defines `InteractionWithTokenLogpReward`, a dataclass that manages completions/responses with their rewards. The `areal/reward/clevr_count_70k.py` file implements a reward function for the CLEVR counting dataset.

## Issues

### 1. Missing space in log message

In the `to_tensor_dict` method of `InteractionWithTokenLogpReward`, the warning message about parent input length has adjacent string literals that run together without a space. When the parent length check fails, the log output shows something like `"constructed properly.Ignoring"` instead of having a space between sentences. Locate the `logger.warning()` call in `to_tensor_dict` and ensure a space separates the sentences.

### 2. Bare `print()` instead of logger in reward function

In `areal/reward/clevr_count_70k.py`, the `clevr_count_70k_reward_fn` function uses a bare `print()` call to log correct matches. The project's logging conventions require using `areal.utils.logging.getLogger()` instead, with a PascalCase logger name (e.g., `"CLEVR70KReward"` or similar, at least 3 characters). Other reward modules like `gsm8k.py` and `geometry3k.py` already follow this convention. The logger must be imported from `areal.utils`, not from the standard library.

### 3. Properties returning bare strings instead of enums

The `api_type` and `input_name_for_logging` properties in `InteractionWithTokenLogpReward` return raw string literals. These should be proper enum types for type safety. Two new enum classes are needed:

- **`ApiType`** (a `str, Enum` subclass) with members whose string values are:
  - `"completion"` — for completion interactions
  - `"response"` — for response interactions

- **`InputName`** (a `str, Enum` subclass) with members whose string values are:
  - `"messages"` — for completion input data
  - `"input_data"` — for response input data

The `api_type` property should return type `ApiType` and the `input_name_for_logging` property should return type `InputName`.

### 4. Missing return type annotation

The `clevr_count_70k_reward_fn` function must have an explicit `-> float` return type annotation.

## Files to modify

- `areal/experimental/openai/types.py`
- `areal/reward/clevr_count_70k.py`