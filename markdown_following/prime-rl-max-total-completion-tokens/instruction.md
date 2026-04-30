# Add a per-environment total-completion-token budget and rename sampling `max_tokens`

You are working in the `prime-rl` repository. Two related schema changes need to be made to the orchestrator config classes in `src/prime_rl/configs/orchestrator.py`, and one consumer in `src/prime_rl/orchestrator/eval_utils.py` must be updated to match.

## 1. New `EnvConfig.max_total_completion_tokens` field

Each environment in an RL run can already pass arbitrary kwargs through `extra_env_kwargs`. Add a first-class field on `EnvConfig` (and therefore inherited by `EvalEnvConfig`) so users can cap the total completion tokens across all turns in a multi-turn rollout without manually editing `extra_env_kwargs`.

Requirements:

- Field name: `max_total_completion_tokens`, type `int`.
- Default: `-1` (disabled).
- Auto-population: after the model is constructed, `extra_env_kwargs["max_total_completion_tokens"]` must equal the value of the field. The field is the source of truth — if the user sets both, the field wins. Plain field defaults must also be reflected (i.e. a default-constructed `EnvConfig` ends up with `extra_env_kwargs == {"max_total_completion_tokens": -1}`).
- This auto-population must apply to `EvalEnvConfig` as well (it's a subclass of `EnvConfig`, so inheriting is sufficient).

## 2. Rename sampling `max_tokens` → `max_completion_tokens`

Both `SamplingConfig` and `EvalSamplingConfig` currently have a field called `max_tokens`. Rename it to `max_completion_tokens` for consistency with the OpenAI API surface, while preserving backwards compatibility:

- The new field name is `max_completion_tokens` (same type and default as before: `int | None`, default `None`).
- Configs that still pass the legacy keyword `max_tokens` must continue to load successfully — the value must end up in `max_completion_tokens`. Use a Pydantic validation alias to accept both names.
- When a config is loaded with the legacy `max_tokens` keyword (and not `max_completion_tokens`), a **deprecation warning** must be emitted that:
  - mentions the deprecated name `max_tokens`,
  - contains the word "deprecated" (any reasonable casing/inflection is fine), and
  - points users to the new name `max_completion_tokens`.
  Use the project logger (`prime_rl.utils.logger.get_logger`).
- The legacy name `max_tokens` must NOT remain as a separate field on the model. There is exactly one field — `max_completion_tokens`. `max_tokens` lives on as an input alias only.

## 3. Update `get_eval_sampling_args` in `src/prime_rl/orchestrator/eval_utils.py`

The function builds a dict of sampling arguments that is sent to an OpenAI-compatible chat-completions endpoint. Update it so that:

- It reads from `sampling_config.max_completion_tokens` (the renamed field).
- The output dict key is `"max_completion_tokens"` (not `"max_tokens"`).
- Behavior is otherwise unchanged: still gated on `is not None`.

## 4. Documentation

Add a `CHANGELOG.md` entry describing both user-visible changes (new field, renamed field with backwards-compatible alias). Match the existing CHANGELOG entry style (a one-paragraph bullet under the topmost entries).

## Code Style Requirements

- Follow the project's `AGENTS.md`. In particular:
  - **Git dependency pins**: any `[tool.uv.sources]` git dependency in `pyproject.toml` must use a 7-character commit hash for the `rev` field.
  - **Minimal try/except**: don't swallow exceptions silently.
  - **Targeted comments**: don't add narrative comments about the change.
- Follow the project's `skills/config/SKILL.md` rule on **deprecation**: when renaming or removing config fields, emit a deprecation warning with a clear migration path.
- Tests, if any, must be plain functions with pytest fixtures (no class-based tests) — but you do not need to add any tests; behavioral verification is automated.
