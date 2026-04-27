# Task: Add an `installation` skill and an `fp8-inference` dependency group

The repo is `prime-rl`, a reinforcement-learning training framework. To run certain FP8 models (e.g. GLM-5-FP8) inference workloads need the `deep-gemm` library. There is currently no documentation for this, and no opt-in mechanism for installing it.

You will do two things:

1. **Add an `fp8-inference` dependency group** to `pyproject.toml` so users can opt into installing `deep-gemm`.
2. **Author a new agent skill** at `skills/installation/SKILL.md` documenting the project's install commands.

Both pieces are required.

## Part 1 — `fp8-inference` dependency group

In `pyproject.toml`, add a new group named `fp8-inference` under the `[dependency-groups]` table. The group must contain a single dependency: `deep-gemm`, sourced from this prebuilt wheel URL:

```
https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl
```

Use the PEP 508 direct-URL form (`deep-gemm @ <url>`). The group will be installed via `uv sync --group fp8-inference`.

You may regenerate `uv.lock` if you have network access; it is not required for grading, but the lockfile must remain a valid uv lockfile if you do touch it.

## Part 2 — `skills/installation/SKILL.md`

Skills live under `skills/` and follow the same structure as the existing `skills/inference-server/SKILL.md` and `skills/toml-config/SKILL.md` (look at one for a style template). They are markdown files with YAML frontmatter; each skill teaches an agent how to handle a specific workflow.

Create a new skill file at `skills/installation/SKILL.md` that covers all of the following:

- **YAML frontmatter** with:
  - `name: installation`
  - a `description:` field explaining what the skill is for (when an agent should invoke it). The description should be a real sentence and reference setting up the project / installing optional extras like `deep-gemm` for FP8 models.
- **`# Installation`** top-level heading.
- A **basic install** section showing a fenced bash code block containing the bare `uv sync` command. Briefly explain that this installs core dependencies from `pyproject.toml`.
- An **all-extras** section showing `uv sync --all-extras`, recommending it as the path most users should take, and noting it installs all optional extras (e.g. flash-attn, flash-attn-cute) at once.
- An **FP8 inference / deep-gemm** section that:
  - Mentions GLM-5-FP8 (or equivalent FP8 model) as the motivating use case.
  - Names the `deep-gemm` package.
  - Shows the exact command `uv sync --group fp8-inference`.
  - Notes that the wheel is prebuilt so no CUDA build step is required.
- A **dev dependencies** section with `uv sync --group dev`, briefly listing what's inside (pytest, ruff, pre-commit, etc.).
- A **key files** section that points to `pyproject.toml` and `uv.lock`.

The skill is read by other agents — write it so a future agent landing on this file can pick the right install command without reading any other source.

## Project conventions

- Follow the AGENTS.md guidance: terse, no try/except where unnecessary, no narrative comments. The skill itself is documentation; keep its language tight.
- Match the prose style and section depth of the existing skills under `skills/`.
- Do NOT remove or alter `skills/inference-server/SKILL.md` or `skills/toml-config/SKILL.md`.
- `pyproject.toml` must remain valid TOML.
