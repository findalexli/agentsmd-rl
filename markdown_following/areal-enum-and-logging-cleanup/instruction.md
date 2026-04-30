# AReaL: Replace string literals with enums and fix logging issues

The AReaL repository at `/workspace/AReaL` (commit `4f5a2944f0`) contains
three small but distinct issues across two files that need to be cleaned up.

## Issue 1 — string literals where enums belong (`areal/experimental/openai/types.py`)

The `InteractionWithTokenLogpReward` dataclass exposes two `@property`
methods that currently return raw string literals (with corresponding
`TODO: replace … value with enum` comments):

- `api_type` returns one of `"completion"`, `"response"`, or `"none"`.
- `input_name_for_logging` returns one of `"messages"`, `"input_data"`, or
  `"none"`.

These string returns are used in f-string interpolation inside `logger.warning`
calls and must remain string-compatible for any existing call sites. Resolve
the TODOs by introducing two enums in the same module and updating the two
properties to return enum members:

- An enum named **`ApiType`** with members **`COMPLETION = "completion"`**,
  **`RESPONSE = "response"`**, **`NONE = "none"`**.
- An enum named **`InputName`** with members **`MESSAGES = "messages"`**,
  **`INPUT_DATA = "input_data"`**, **`NONE = "none"`**.

Both enums must be **`str`-mixin enums** (i.e. they inherit from both `str`
and `Enum`, like `class ApiType(str, Enum): ...`) so that f-string formatting
and string comparisons against the literal values continue to work without
any caller changes. The two properties' return-type annotations should be
updated accordingly.

## Issue 2 — missing space in a `logger.warning` message (`areal/experimental/openai/types.py`)

Inside `InteractionWithTokenLogpReward.to_tensor_dict`, the warning that is
emitted when a child interaction's input length does not exceed its parent's
length is built from two adjacent f-string literals. Adjacent Python string
literals concatenate without inserting whitespace, so the rendered message
runs the period directly into the next sentence:

> `…constructed properly.Ignoring the parent…`

Fix the formatting so that the rendered message reads
`…constructed properly. Ignoring the parent…` (a single space between the
period and `Ignoring`). The fix should be made at the source-string level
(not by post-processing the formatted message).

## Issue 3 — `print()` instead of logger; integer reward instead of float (`areal/reward/clevr_count_70k.py`)

`clevr_count_70k_reward_fn` currently:

1. Calls `print(f"completions: {completions}, answer: {answer}")` when the
   prediction matches the ground truth, bypassing the project's logging
   infrastructure.
2. Returns Python `int` values (`0` and `1`) instead of `float`s. Other
   reward functions in `areal/reward/` (e.g. `gsm8k.py`, `geometry3k.py`)
   return `float` and use `areal.utils.logging`.

Update `areal/reward/clevr_count_70k.py` so that:

- A module-level logger is registered via
  `areal.utils.logging.getLogger("CLEVR70KReward")`. The logger name must be
  exactly the PascalCase string `"CLEVR70KReward"` to match the project's
  logging conventions.
- The `print(...)` call inside `clevr_count_70k_reward_fn` is replaced by a
  call to that logger's `info(...)` method (with the same message body).
- `clevr_count_70k_reward_fn` returns `float` values in every branch
  (`0.0` and `1.0`), and its return-type annotation reflects this
  (`-> float`).
- `extract_answer` is **not** part of this task and must keep its current
  behaviour (e.g. returns `"2.5"` from `"foo [1] bar [2.5] baz"`, or `""`
  when no brackets are found).

## Code Style Requirements

The repository uses **ruff 0.14.9** for both linting and formatting, with
configuration in `pyproject.toml` (rules `E`, `W`, `F`, `I`, `UP`; line
length 88; isort with a custom `areal` first-party section). Your final
edits to both files must pass:

- `ruff check --config pyproject.toml areal/experimental/openai/types.py areal/reward/clevr_count_70k.py`
- `ruff format --check --config pyproject.toml areal/experimental/openai/types.py areal/reward/clevr_count_70k.py`

Per the repository's `AGENTS.md`, do **not** introduce wildcard imports, and
follow the existing module-level import ordering (future, stdlib,
third-party, areal first-party).

## What is out of scope

- Do not modify any other files in the repository.
- Do not change the public name or signature of `clevr_count_70k_reward_fn`,
  `InteractionWithTokenLogpReward`, or any of its existing properties.
- Do not change the *values* the two new enums map to (the `.value` of each
  enum member must equal the original string literal, so f-string output is
  byte-identical to the pre-fix output).
