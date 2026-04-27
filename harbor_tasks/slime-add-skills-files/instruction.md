# Author slime agent skills

The slime training framework lives at `/workspace/slime`. It currently has
no `.claude/skills/` directory — agents working on slime have nothing to
guide them through the framework's customization extension points. Author
a set of skill files that capture how slime is meant to be extended.

## Required skills

Create exactly the following five skill files, each a valid Markdown
document with YAML frontmatter:

| Path | `name` (frontmatter) |
|---|---|
| `.claude/skills/add-dynamic-filter/SKILL.md` | `add-dynamic-filter` |
| `.claude/skills/add-eval-dataset-config/SKILL.md` | `add-eval-dataset-config` |
| `.claude/skills/add-reward-function/SKILL.md` | `add-reward-function` |
| `.claude/skills/add-rollout-function/SKILL.md` | `add-rollout-function` |
| `.claude/skills/add-tests-and-ci/SKILL.md` | `add-tests-and-ci` |

Each `SKILL.md` MUST start with frontmatter delimited by `---` lines
containing at least:

- `name`: the slug (matching the directory name)
- `description`: a one-sentence description of when to invoke this skill

Each skill body MUST contain (at minimum) these two `##` sections, in
addition to whatever else you find useful:

- `## When to Use`
- `## Step-by-Step Guide`

## Make the skills usable to a Codex agent too

slime is being onboarded for both Claude and Codex agent ecosystems.
Both ecosystems should resolve the same skill files. Add a `.agents/skills`
entry in the repo so that, from the `.agents/` directory, the path
`.agents/skills` resolves to the same content as `.claude/skills`.

The path `.agents/skills` MUST be a **symlink** (not a copy and not a
directory) whose target is the relative path `../.claude/skills`.

## Required content per skill

The five skills exist to teach an agent *how slime extends* in five
specific places. Each skill must reference the exact CLI flags and
source files the agent will need to touch — this is what makes the
skill load-bearing rather than decorative.

### `add-dynamic-filter`

This skill teaches how to add filtering hooks in slime's rollout/buffer
stages. It must mention all four hook flags slime exposes:

- `--dynamic-sampling-filter-path`
- `--buffer-filter-path`
- `--rollout-sample-filter-path`
- `--rollout-all-samples-process-path`

It must reference the source-file locations these hooks plug into:

- `slime/rollout/filter_hub/base_types.py` (filter output dataclasses)
- `slime/rollout/sglang_rollout.py` (where dynamic sampling filter is invoked)
- `slime/rollout/data_source.py` (where the buffer filter is invoked)

### `add-eval-dataset-config`

This skill teaches how to configure evaluation datasets. It must
mention the relevant CLI flags:

- `--eval-config` (structured YAML)
- `--eval-prompt-data` (legacy CLI pairs)
- `--eval-interval` (the trigger that requires eval datasets to be set)

And the source files involved in eval-config resolution:

- `slime/utils/eval_config.py`
- `slime/utils/arguments.py`

### `add-reward-function`

This skill teaches how to plug in a custom reward model. It must
mention both relevant CLI flags:

- `--custom-rm-path` (the reward function entry)
- `--custom-reward-post-process-path` (optional post-processing hook)

Because slime supports both per-sample and group reward modes, the skill
must mention the `--group-rm` switch that toggles between them.

It must reference the dispatch and post-process source locations:

- `slime/rollout/rm_hub/__init__.py`
- `slime/ray/rollout.py`

### `add-rollout-function`

This skill teaches how to write a custom rollout function. It must
mention the wiring flag:

- `--rollout-function-path`

It must name the two output dataclasses a rollout function returns:

- `RolloutFnTrainOutput`
- `RolloutFnEvalOutput`

And it must reference these source files (which together define what
"a rollout" looks like in slime):

- `slime/rollout/sglang_rollout.py` (default async rollout)
- `slime/rollout/sft_rollout.py` (simple SFT-style rollout reference)
- `slime/rollout/base_types.py` (output dataclasses)

### `add-tests-and-ci`

This skill teaches how to add tests and update slime's CI. The slime CI
workflow is generated from a Jinja template, so this skill must point
at both pieces of the template/regeneration loop:

- `.github/workflows/pr-test.yml.j2` (the template)
- `.github/workflows/generate_github_workflows.py` (the generator script)

## Notes on style

The skills are reference material agents will read at task time, not
prose for a human audience. Prefer short bullet lists, code fences with
the relevant language tag, and imperative section titles. Keep each
file to a single page of structured guidance — the value is in
*specificity* (real flags, real paths, real function signatures), not
in length.
