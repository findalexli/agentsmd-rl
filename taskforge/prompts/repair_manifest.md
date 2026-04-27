# Repair Task Manifest

You are repairing the `eval_manifest.yaml` of an existing benchmark task. The task's tests, Dockerfile, and solve.sh **already work** (Docker oracle has confirmed nop=0, gold=1). Only the metadata layer is broken — schema-drifted or missing fields.

## DO NOT

- Touch `environment/Dockerfile`
- Touch `solution/solve.sh`
- Touch `tests/test.sh` or `tests/test_outputs.py`
- Touch `instruction.md`
- Re-run Docker oracle (it already passed)

## YOUR JOB

Rewrite ONLY `/workspace/task/eval_manifest.yaml` so it passes strict Pydantic validation against the canonical schema. Preserve all real metadata (PR number, base/merge commits, rubric rule text, test ids, source SHAs) — just normalize the field names and shapes.

## Inputs available to you

- `/workspace/task/eval_manifest.yaml` — current (drifted) manifest. **MAY BE MISSING ENTIRELY** — if the file does not exist or fails to parse as YAML, you must CREATE one from scratch using the other inputs below.
- `/workspace/task/task.toml` — has PR metadata (sometimes the only place with `base_commit`)
- `/workspace/task/tests/test_outputs.py` — authoritative for `check.id` values (one per `def test_*`)
- `/workspace/task/solution/solve.sh` — the gold patch; useful for inferring config_edits
- `/workspace/task/instruction.md` — context about what's tested
- `/workspace/task/scaffold_status.json` and `status.json` — may have additional info

You can clone the source repo to inspect agent-config files at the base commit:

```bash
# Get repo info from task.toml and existing manifest
cd /workspace
mkdir -p repo && cd repo
git init -q
git remote add origin https://github.com/{OWNER}/{REPO}.git
git fetch --depth 1 origin {BASE_COMMIT} -q
git checkout {BASE_COMMIT} -q
# Now read AGENTS.md, CLAUDE.md, .cursorrules, etc. as needed
```

This lets you populate `source.path`, `source.lines`, `source.commit` for `agent_config` checks and rubric/distractor entries — enough to make validation pass and traceable to the real config text.

## Canonical schema (Pydantic-enforced — these names and enums are NOT optional)

```yaml
version: "2.0"

source:                                    # toplevel — NOT under metadata.*
  repo: "{OWNER}/{REPO}"
  pr: 12345                                # int (not "12345" string)
  base_commit: "<sha>"
  merge_commit: "<sha>"

task:
  kind: code_fix                           # code_fix | code_with_config | markdown_authoring

checks:
  - id: <slug>                             # match a `def test_*` in test_outputs.py
    type: fail_to_pass                     # fail_to_pass | pass_to_pass — ONLY these two
    origin: pr_diff                        # pr_diff | repo_tests | agent_config | static — ONLY these four
    description: "<one line>"
    source:                                # REQUIRED iff origin == agent_config
      path: "AGENTS.md"                    # field is `path`, not `file`
      lines: "30"                          # numeric line/range as a STRING. ok if "" if unknown.
      commit: "{BASE_COMMIT}"

config_edits:                              # required for code_with_config & markdown_authoring kinds
  - path: "AGENTS.md"                      # `path`, not `file`
    tier: 1                                # 1 = agent instruction, 2 = doc
    gold_added: "<text>"                   # `gold_added`, not `added`. STRING (not list/dict).
    gold_removed: "<text>"                 # may be ""

rubric:
  - rule: "<verbatim text from agent config>"   # `rule`, not `description`
    source:                                # DICT, not free-form string
      path: "AGENTS.md"
      lines: "45"
      commit: "{BASE_COMMIT}"
    evidence: "<how gold demonstrates this>"
    category: naming                       # naming | style | architecture | testing | etc.
    verification: llm_judge                # programmatic | llm_judge | semantic_diff

distractors:                               # negative rubric — collisions
  - rule: "<verbatim text>"
    source: { path: "...", lines: "...", commit: "..." }
    collision_type: rule_conflict          # rule_conflict | scope_ambiguity | meta_confusion | architecture_boundary | would_cause_bug
    why_distracting: "<one line>"
    severity: medium                       # high | medium | low
```

## Common drift to fix (in priority order)

1. `source.pr_url` or `source.pr_number` (without `pr` int) → derive `pr: <int>` from URL
2. `metadata.source_pr` block → move to toplevel `source`
3. `origin: pr_behavior | behavioral | gold_diff | structural | task_specific | ...` → map to one of the canonical 4. Anything behavioral/PR-derived → `pr_diff`. Anything from existing repo CI → `repo_tests`. Anything anti-stub/syntax → `static`. Anything from CLAUDE.md/AGENTS.md → `agent_config`.
4. Rubric `description:` → `rule:`
5. Rubric `source` as a free-form string `"AGENTS.md (base commit XXX, lines 30-45)"` → parse to `{path: AGENTS.md, lines: "30-45", commit: XXX}`
6. Source `file:` → `path:` (every place — checks, rubric, config_edits)
7. Source `ref:` → `commit:`
8. `config_edits.added/removed` → `gold_added/gold_removed`
9. Missing `source` field on `agent_config` checks → READ the relevant config file and populate path/lines/commit. If you genuinely cannot determine the source, change the `origin` to a non-`agent_config` value (e.g. `pr_diff`).
10. Missing `rubric.rule` text — find the rule in the agent-config file (CLAUDE.md/AGENTS.md/SKILL.md) it should reference and put the verbatim text. If no plausible rule exists, drop the entry rather than invent one.

## Self-validate before declaring success

```bash
cd /workspace && python3 -c "
import yaml
from taskforge.models import EvalManifest
data = yaml.safe_load(open('/workspace/task/eval_manifest.yaml').read())
EvalManifest.model_validate(data)
print('SCHEMA OK')
"
```

If that errors, READ the error, fix the manifest, and re-run. Do NOT write your verdict until `SCHEMA OK`. The pipeline will reject your work otherwise.

## Final verdict

Write to `/workspace/task/scaffold_status.json`:

```json
{"scaffolded": true, "nop_reward": 0, "gold_reward": 1, "repair_only": true}
```

The `repair_only: true` marker is just a hint — the pipeline still trusts the same scaffolded/nop/gold contract. Set `nop_reward: 0` and `gold_reward: 1` (not running Docker; trusting prior validation).

If the manifest is unfixable (e.g. agent-config files have moved, original PR's commits don't exist, no PR metadata recoverable), abandon honestly:

```json
{"abandoned": true, "reason": "<one-sentence cause>"}
```

Do not write `scaffolded: true` if `EvalManifest.model_validate` did not pass. The schema gate in the pipeline will reject your work and waste a sandbox.
