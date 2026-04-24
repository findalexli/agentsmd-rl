# Bug: String concatenation bug in log message and logging convention violations

## Context

AReaL is a distributed RL training framework for LLM alignment. Two files need fixes:

- `areal/experimental/openai/types.py` — defines `InteractionWithTokenLogpReward`, a dataclass managing completions/responses with rewards
- `areal/reward/clevr_count_70k.py` — implements a reward function for the CLEVR counting dataset

## Issues to Fix

### 1. Missing space in warning message

In `types.py`, when a warning is logged about parent input length being too small, the message sentences run together without a space — e.g., `"constructed properly.Ignoring"` instead of `"constructed properly. Ignoring"`. Find and fix this concatenation bug.

### 2. Bare `print()` instead of logger in reward function

In `clevr_count_70k.py`, a `print()` call outputs correct-match information. The project requires using `areal.utils.logging.getLogger()` (imported from `areal.utils`, not stdlib) with a PascalCase descriptive name (at least 3 characters). Compare with other reward modules like `gsm8k.py` or `geometry3k.py` for the expected pattern.

### 3. Properties returning bare strings instead of enums

The `api_type` and `input_name_for_logging` properties return raw string literals. These should be proper `str`-compatible enum types for type safety.

Define two enum classes:

- **`ApiType`** — a `str, Enum` subclass with values:
  - `"completion"` — for completion interactions
  - `"response"` — for response interactions
  - `"none"` — for the else case

- **`InputName`** — a `str, Enum` subclass with values:
  - `"messages"` — for completion input data
  - `"input_data"` — for response input data
  - `"none"` — for the else case

Both properties must return their respective enum types (not bare strings), including the `"none"` case.

### 4. Missing return type annotation

The `clevr_count_70k_reward_fn` function needs an explicit `-> float` return type annotation.

## Files to modify

- `areal/experimental/openai/types.py`
- `areal/reward/clevr_count_70k.py`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
