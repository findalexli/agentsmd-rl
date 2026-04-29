# Agent Evaluation Framework Grading Schema Comparison

Comparison of task and grading schemas across 8 leading agent evaluation frameworks, with a recommended schema for agentsmd-rl.

## 1. Framework-by-Framework Analysis

### 1.1 Anthropic — "Demystifying Evals for AI Agents"

Source: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

| Term | Definition |
|---|---|
| **Task** | A single test with defined inputs and success criteria |
| **Trial** | One execution attempt of a task |
| **Grader** | Logic that scores some aspect of performance; one task may have multiple graders, each containing multiple **assertions** (checks) |
| **Transcript** | Complete record of a trial (outputs, tool calls, reasoning) |
| **Outcome** | Final environment state at trial end |

| Grader type | Sub-methods | Strengths | Weaknesses |
|---|---|---|---|
| **Code-based** | String match (exact/regex/fuzzy), binary tests (fail-to-pass / pass-to-pass), static analysis, outcome verification, tool-call verification, transcript analysis | Fast, cheap, reproducible, objective | Brittle to valid variations |
| **Model-based** | Rubric-based scoring, NL assertions, pairwise comparison, reference-based, multi-judge consensus | Flexible, captures nuance, handles open-ended | Non-deterministic, expensive, needs calibration |
| **Human** | SME review, crowdsourced, spot-check, A/B, inter-annotator agreement | Gold standard | Expensive, slow, doesn't scale |

Composition modes: **weighted** (combined scores hit threshold), **binary** (all must pass), **hybrid** (some gated, rest weighted).

Recommendations: grade outcome, not transcript; build in partial credit; deterministic first, LLM where necessary, human for calibration; isolate dimensions with separate LLM judges; calibrate against human experts; provide an "Unknown" escape hatch.

Schema is informal — no formal spec published.

```
task:
  inputs: ...
  success_criteria: ...
  graders:
    - type: code_based | model_based | human
      assertions: [...]
  composition: weighted | binary | hybrid
  reference_solution: ...
```

### 1.2 Harbor Framework

Source: https://harborframework.com/docs/tasks

```
task-directory/
  instruction.md          # Agent prompt
  task.toml               # Metadata + config
  environment/Dockerfile  # Or docker-compose.yaml
  solution/solve.sh       # Reference solution (for validation)
  tests/test.sh           # Writes reward to /logs/verifier/
```

```toml
version = "1.0"

[metadata]
author_name = "string"
author_email = "string"
difficulty_explanation = "string"
category = "string"
tags = ["string"]

[verifier]
timeout_sec = 120.0
env = { KEY = "value" }
user = "string | int | null"

[agent]
timeout_sec = 120.0
user = "string | int | null"

[solution]
env = { KEY = "value" }

[environment]
build_timeout_sec = 600.0
docker_image = "string | null"
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
gpu_types = ["string"] | null
allow_internet = true
env = { KEY = "value" }

[[environment.mcp_servers]]
name = "string"
transport = "streamable-http" | "sse" | "stdio"
url = "string"
```

Reward output: `reward.txt` (single float, read first) or `reward.json` (dict of named float metrics, e.g. `{"behavioral": 0.6, "regression": 0.2}`).

Harbor is grader-agnostic — `test.sh` computes its own weighted score. No built-in multi-grader orchestration. No source attribution.

### 1.3 SWE-bench / SWE-bench Verified

Source: https://www.swebench.com/SWE-bench/guides/datasets/

| Field | Type | Description |
|---|---|---|
| `instance_id` | str | `owner__repo-PR_number` |
| `repo` | str | `owner/repo` |
| `issue_id` | int | GitHub issue number |
| `base_commit` | str | Repo HEAD before solution PR |
| `problem_statement` | str | Issue title + body |
| `hints_text` | str | Issue comments before PR |
| `created_at` | str | PR creation date |
| `patch` | str | Gold patch (minus tests) |
| `test_patch` | str | Test file patch from solution PR |
| `version` | str | Repo package version |
| `environment_setup_commit` | str | Commit for env setup |
| `FAIL_TO_PASS` | str (JSON list) | Tests that must go from failing to passing |
| `PASS_TO_PASS` | str (JSON list) | Tests that must remain passing |
| `issue_url`, `pr_url` | str | GitHub URLs |

SWE-bench Verified adds `difficulty` (str).

Grading is strictly binary: resolved iff all `FAIL_TO_PASS` pass AND all `PASS_TO_PASS` still pass. No partial credit, no multi-signal composition, no LLM judge, no source attribution.

```json
{
  "total_instances": 300,
  "submitted_instances": 295,
  "completed_instances": 290,
  "resolved_instances": 147,
  "resolution_rate": 0.49
}
```

Per-instance results in `instance_results.jsonl`.

OpenAI critique: 35.5% of failed instances use narrow tests rejecting valid solutions; 18.8% use wide tests checking things outside the problem statement; binary scoring loses partial-progress signal.

### 1.4 METR Task Standard

Source: https://github.com/METR/task-standard/blob/main/STANDARD.md

```
task_family_name/
  task_family_name.py     # Defines TaskFamily class
  manifest.yaml           # Resource requirements
  *.py, *.sh, assets
```

```python
class TaskFamily:
    standard_version = "0.5.0"
    required_environment_variables: list[str] = []

    @staticmethod
    def get_tasks() -> dict[str, Task]: ...
    @staticmethod
    def get_instructions(t: Task) -> str: ...
    @staticmethod
    def get_permissions(t: Task) -> list[str]: ...
    @staticmethod
    def get_aux_vm_spec(t: Task) -> VMSpec | None: ...
    @staticmethod
    def install() -> None: ...
    @staticmethod
    def start(t: Task) -> None: ...
    @staticmethod
    def score(t: Task, submission: str) -> float | None:
        # MUST NOT coexist with intermediate_score
    @staticmethod
    def intermediate_score(t: Task, submission: str) -> float | None:
        # MUST NOT coexist with score
    @staticmethod
    def aggregate_scores(...) -> float | None:
        # MUST NOT coexist with score
    @staticmethod
    def teardown(t: Task) -> None: ...
```

```yaml
$schema: 'http://json-schema.org/draft-07/schema#'
type: object
patternProperties:
  '^\[a-zA-Z0-9\_\]+$':   # task name
    type: object
    properties:
      resources:
        type: object
        properties:
          gpu:
            count_range: [min, max]
            model: string
          cpus: integer (min: 1)
          memory_gb: integer (min: 1)
```

Single `score()` per task returning `float | None` in [0, 1] (None = manual). No built-in multi-grader composition; no source attribution. Quality guidance: "incompetent agent ≤ 0.1, competent agent ≥ 0.9". Continuous scoring preferred over binary.

### 1.5 Inspect AI (UK AISI)

Source: https://inspect.aisi.org.uk/

```python
Task(
    dataset: Dataset | Sequence[Sample] | None = None,
    setup: Solver | list[Solver] | None = None,
    solver: Solver | Agent | list[Solver] = generate(),
    cleanup: Callable[[TaskState], Awaitable[None]] | None = None,
    scorer: Scorers | None = None,
    metrics: list[Metric | dict[str, list[Metric]]] | None = None,
    model: str | Model | None = None,
    config: GenerateConfig = GenerateConfig(),
    sandbox: SandboxEnvironmentType | None = None,
    epochs: int | Epochs | None = None,
    fail_on_error: bool | float | None = None,
    message_limit: int | None = None,
    token_limit: int | None = None,
    time_limit: int | None = None,
    cost_limit: float | None = None,
    name: str | None = None,
    version: int | str = 0,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
)
```

```python
@dataclass
class Score:
    value: Value      # str | int | float | bool | Sequence | Mapping
    answer: str
    explanation: str
    metadata: dict[str, Any]
```

| Scorer | Type | Description |
|---|---|---|
| `includes()` | Deterministic | Target substring in output |
| `match()` | Deterministic | Target at beginning/end |
| `exact()` | Deterministic | Normalized exact match |
| `pattern()` | Deterministic | Regex extraction |
| `answer()` | Deterministic | "ANSWER:" marker extraction |
| `f1()` | Deterministic | Token-level F1 |
| `choice()` | Deterministic | Multiple choice |
| `math()` | Deterministic | SymPy expression equivalence |
| `model_graded_qa()` | Model-based | LLM correctness judge |
| `model_graded_fact()` | Model-based | LLM fact-presence judge |

Three multi-scorer patterns:

```python
# 1. List of scorers (independent)
Task(scorer=[scorer_a(), scorer_b()])

# 2. Single scorer yielding dict (shared computation)
@scorer(metrics={"dim_a": [mean()], "dim_b": [mean()]})
def multi_dim():
    async def score(state, target):
        return Score(value={"dim_a": 0.8, "dim_b": 0.6})
    return score

# 3. multi_scorer with reducer (voting/aggregation)
multi_scorer(
    scorers=[model_graded_qa(model=m) for m in models],
    reducer="mode"  # or "mean", "median", "max"
)
```

Epoch reducers: `mean`, `median`, `mode`, `max`, `pass_at_{k}`, `at_least_{k}`. Metrics: `accuracy()`, `mean()`, `var()`, `std()`, `stderr()`, `bootstrap_stderr()`, `grouped(metric, field)`.

UK AISI Evaluation Standard: primary scorer must be binary (pass/fail); auxiliary scorers provide richer signals; model grading restricted to content matching (not numerical ratings); custom scorers must have unit tests; QA via frontier model or human completion logs.

### 1.6 Vivaria (METR)

Source: https://vivaria.metr.org/

Runtime for METR Task Standard tasks. Server (TS + PostgreSQL) creates task environments and runs agents; CLI (Python) is the user interface; pyhooks (Python) is the agent-to-server interface for LLM API calls and trace entries.

Vivaria does not define its own schema; it consumes METR tasks and uses whatever `TaskFamily.score()` returns. No additional grader composition, source attribution, or multi-signal reward.

### 1.7 SWE-RM (Execution-Free Reward Model)

Source: https://arxiv.org/abs/2512.21919

Mixture-of-experts, 30B total / 3B active (DeepSeek base), 256k context for full multi-turn trajectories.

Verifier emits "Yes" / "No" and the score is computed from logits:

```
r = exp(l_y) / (exp(l_y) + exp(l_n))
```

Hybrid reward (Equation 1):

```
r(q, tau_i) = ExecutionBucket(q, tau_i) + Score_EF(q, tau_i, patch_i)
```

| Outcome | ExecutionBucket |
|---|---:|
| Issue resolved (all tests pass) | +1.0 |
| Tests fail (otherwise) | 0.0 |
| Unfinished (no patch) | -0.5 |

`Score_EF` is the continuous [0, 1] from the logprobs formula above. Combination is **additive**, not weighted-average — the bucket coarse-classifies; the RM differentiates within the bucket.

Key finding: **TTS ≠ RL quality**. Two verifiers with nearly identical test-time scaling produced strikingly different RL training behavior. The differentiator was classification accuracy (AUC) and calibration (ECE), not just ranking.

```
AUC = Pr(r(tau_+) > r(tau_-))
ECE = sum_m (|B_m|/n) * |acc(B_m) - conf(B_m)|
```

Data findings: optimal positive:negative is 2:1; 256k context lifts RM@32 from 66.8% (16k) to 74.4%; hybrid reward (SWE-RM + execution) gives smoothest learning + highest pass@1.

### 1.8 AgentBench

Source: https://github.com/THUDM/AgentBench (ICLR 2024)

Client-server with three components: Task Server (hosts environment, gives feedback), Agent Server (inference interface), Client (coordinates via max-flow assignment).

```yaml
# configs/tasks/kg.yaml
import: definition.yaml

task_name:
  module: "src.tasks.kg"
  workers: 2
  config:
    dataset: "path/to/data"
    ...
```

Extended YAML keywords: `import`, `default`, `overwrite`.

Per-environment scoring functions, not standardized across environments. 8 environments (OS, DB, KG, Card Game, Lateral Thinking, HouseHolding, WebShopping, WebBrowsing). Predominantly rule-based, no LLM judge, no source attribution.

Distinct project at github.com/agentbench uses layered scoring: Layer 0 structural (40%), Layer 1 metrics (40%), Layer 2 behavioral (20%) — all rule-based.

## 2. Comparison Table

| Feature | Anthropic Blog | Harbor | SWE-bench | METR | Inspect AI | Vivaria | SWE-RM | AgentBench |
|---|---|---|---|---|---|---|---|---|
| **Task definition format** | Informal | TOML+MD+Dockerfile | JSON/JSONL | Python class+YAML | Python `@task` | (uses METR) | N/A (RM) | YAML config |
| **Grader types** | code/model/human | Script-defined | Pytest (binary) | Single `score()` | Scorer plugins | (uses METR) | Logprobs + exec | Per-environment |
| **Multiple graders per task** | Yes (recommended) | By convention | No | No | Yes (list or dict) | No | Yes (hybrid) | No |
| **Grader composition** | weighted/binary/hybrid | Manual in `test.sh` | AND (all tests pass) | N/A (single float) | Reducers | N/A | Additive (bucket + RM) | Layered weights |
| **Partial credit** | Recommended | Possible (float) | No | Yes (0–1 float) | Yes (float Score) | Yes | Yes (continuous) | Yes (layered) |
| **Source attribution** | Not formalized | None | `test_patch` field | None | None | None | None | None |
| **LLM judge support** | Recommended | Not built-in | No | Via `score()` | `model_graded_qa/fact` | Via `score()` | Core (logprobs) | No |
| **Deterministic tests** | Recommended primary | `test.sh` | Pytest-only | Via `score()` | includes/match/exact/f1 | Via `score()` | ExecutionBucket | Rule-based |
| **Multi-signal reward** | Conceptual | `reward.json` dict | No | No | Dict-valued Score | No | Yes (formal) | Layered |
| **Calibration guidance** | Yes (vs human) | No | No | Yes (0.1–0.9) | Yes (binary primary) | No | Yes (AUC + ECE) | No |
| **Formal schema spec** | No | Partial (`task.toml`) | HF dataset card | Python template | Python types | N/A | Paper formulas | Partial (YAML) |

## 3. Key Design Insights

### 3.1 Nobody has a clean grader-composition standard

| Framework | Multi-grader composition |
|---|---|
| Anthropic | Conceptual; no schema published |
| Harbor | Pushed into ad-hoc bash |
| SWE-bench | Binary AND (simplest possible) |
| METR | Single float; composition lives inside `score()` |
| Inspect AI | Multi-scorer + reducer, but Q&A-oriented |
| SWE-RM | Most principled (additive bucket + continuous RM); reward-model paper, not a benchmark spec |

**Opportunity: a clean, declarative schema for grader composition would be novel.**

### 3.2 Source attribution: only this project does it

None of the 8 frameworks trace test checks or rubric rules to specific source files and line ranges. SWE-bench's `test_patch` records which file the tests came from, but no per-check attribution. The `SourceRef` model in this project's `rubric.py` is genuinely novel.

### 3.3 SWE-RM's hybrid insight maps to our architecture

| SWE-RM | This project |
|---|---|
| ExecutionBucket (reliable, coarse) | `test.sh` deterministic score |
| Score_EF (nuanced, continuous) | LLM rubric ICR score |
| Additive — RM shifts within bucket, never overrides | Same property |
| For RL: high AUC + low ECE | Same target |

### 3.4 Anthropic's dimensional isolation

Each LLM dimension graded by a separate judge — not one monolithic judge. Aligns with our `rubric.yaml` design, where each `RubricRule` is evaluated independently.

### 3.5 UK AISI's binary-primary + auxiliary pattern

Binary primary scorer + richer auxiliary metrics avoids the "what does 0.73 mean?" problem while preserving useful signal.

## 4. Recommended Schema

### 4.1 Provenance

| Source | Borrowed from |
|---|---|
| Anthropic | Three grader types, grade-outcome-not-transcript, partial credit, dimensional isolation |
| Harbor | File-based task structure, `test.sh` entry point, `reward.json` named metrics |
| SWE-bench | `FAIL_TO_PASS` / `PASS_TO_PASS`, `instance_id` format |
| METR | Single float final score (0–1), Python-defined scoring |
| Inspect AI | Typed `Score`, multi-scorer + reducers, dict-valued scores, epoch reducers |
| SWE-RM | Additive composition (bucket + continuous RM), AUC/ECE for RM quality |
| UK AISI | Binary primary + auxiliary, mandatory unit tests |
| Novel | `SourceRef` attribution, `RubricRule` with applicability filters |

### 4.2 Data Model (Pydantic)

```python
"""Recommended multi-grader evaluation schema for agentsmd-rl.

Combines:
- Harbor's file-based task structure
- SWE-bench's FAIL_TO_PASS / PASS_TO_PASS
- Anthropic's three grader types with composition modes
- SWE-RM's additive hybrid reward
- Inspect AI's typed Score with dict values
- METR's 0.0-1.0 final score
- Novel SourceRef attribution
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, computed_field


# ── Source Attribution (novel to this project) ────────────────────────

class SourceRef(BaseModel):
    """Traces a check or rule to its origin in the repository."""
    file: str = Field(description="Path relative to repo root")
    lines: tuple[int, int] = Field(description="Inclusive (start, end) line range")
    commit: Optional[str] = Field(default=None, description="Git SHA at extraction time")


class CheckOrigin(str, Enum):
    """Where a grader check was derived from."""
    PR_DIFF = "pr_diff"             # From the PR's behavioral change
    REPO_TESTS = "repo_tests"       # Existing test suite (pass-to-pass)
    AGENT_CONFIG = "agent_config"   # From CLAUDE.md / AGENTS.md / .cursorrules
    STATIC_ANALYSIS = "static"      # Linter/type-checker rules
    CUSTOM = "custom"               # Task-specific custom check


# ── Grader Type Taxonomy (from Anthropic) ─────────────────────────────

class GraderType(str, Enum):
    """Three-tier grader taxonomy per Anthropic's guidance."""
    DETERMINISTIC = "deterministic"   # Code-based: fast, cheap, reproducible
    MODEL_BASED = "model_based"       # LLM judge: flexible, needs calibration
    HUMAN = "human"                   # Gold standard, expensive


class GraderMethod(str, Enum):
    """Specific grading methods within each type."""
    # Deterministic methods
    FAIL_TO_PASS = "fail_to_pass"           # SWE-bench style behavioral test
    PASS_TO_PASS = "pass_to_pass"           # Regression guard
    STATIC_ANALYSIS = "static_analysis"     # ruff/mypy/eslint on changed files
    OUTCOME_VERIFICATION = "outcome_verify" # Check final state (files, DB, env)
    STRING_MATCH = "string_match"           # Exact/regex/fuzzy
    AST_CHECK = "ast_check"                 # Structural code analysis
    # Model-based methods
    RUBRIC_SCORING = "rubric_scoring"       # Per-rule LLM evaluation
    NATURAL_LANGUAGE = "nl_assertion"       # Free-form LLM assertion
    PAIRWISE_COMPARISON = "pairwise"        # Compare two outputs
    MULTI_JUDGE = "multi_judge"             # Consensus across models
    # Human methods
    SME_REVIEW = "sme_review"
    SPOT_CHECK = "spot_check"


# ── Individual Check (granular assertion) ─────────────────────────────

class Check(BaseModel):
    """One atomic assertion within a grader.

    Inspired by Anthropic's "assertions (sometimes called checks)" and
    this project's existing TestCheck model, with added method typing.
    """
    id: str = Field(description="Stable slug, e.g. 'constructor-crash-no-unbound'")
    description: str = Field(description="What this check verifies")
    weight: float = Field(ge=0.0, description="Relative weight within its grader")
    origin: CheckOrigin = CheckOrigin.PR_DIFF
    source: Optional[SourceRef] = Field(
        default=None,
        description="Where this check was derived from (file + lines in repo)"
    )
    tags: list[str] = Field(default_factory=list)


# ── Grader (group of related checks) ─────────────────────────────────

class CompositionMode(str, Enum):
    """How checks within a grader combine (from Anthropic)."""
    WEIGHTED = "weighted"   # Weighted sum of check scores
    ALL_PASS = "all_pass"   # Binary AND: all checks must pass
    ANY_PASS = "any_pass"   # Binary OR: at least one check passes
    CUSTOM = "custom"       # Custom reducer (specified in test.sh or scorer code)


class Grader(BaseModel):
    """A named grader containing one or more checks.

    Maps to Anthropic's definition: 'Logic that scores some aspect of the
    agent's performance. A task can have multiple graders, each containing
    multiple assertions.'
    """
    id: str = Field(description="e.g. 'behavioral', 'regression', 'style_rubric'")
    grader_type: GraderType
    method: GraderMethod
    checks: list[Check]
    composition: CompositionMode = CompositionMode.WEIGHTED
    weight: float = Field(
        ge=0.0,
        description="This grader's weight in the task-level score"
    )

    @computed_field
    @property
    def check_weight_total(self) -> float:
        return sum(c.weight for c in self.checks)


# ── Task-Level Scoring (multi-grader composition) ─────────────────────

class TaskComposition(str, Enum):
    """How multiple graders compose into the final task score.

    From Anthropic: 'scoring can be weighted, binary, or hybrid.'
    From SWE-RM: additive bucketing is a fourth option.
    """
    WEIGHTED = "weighted"       # Weighted average of grader scores
    BINARY = "binary"           # All graders must pass (AND)
    HYBRID = "hybrid"           # Some graders gated (must pass), rest weighted
    ADDITIVE_BUCKET = "additive_bucket"  # SWE-RM style: bucket + continuous offset


class GatePolicy(str, Enum):
    """For hybrid composition: which graders are gates vs weighted."""
    GATE = "gate"           # Must pass (score > 0) or entire task fails
    WEIGHTED = "weighted"   # Contributes to weighted score
    BONUS = "bonus"         # Adds to score but doesn't reduce it


# ── Task Evaluation Manifest ──────────────────────────────────────────

class TaskEvalManifest(BaseModel):
    """Complete evaluation specification for one task.

    This is the declarative schema that lives alongside the task,
    declaring what test.sh contains and how graders compose.
    Analogous to SWE-bench's instance fields + Harbor's task.toml +
    METR's TaskFamily, but with formal multi-grader composition.
    """
    # Identity (from SWE-bench)
    task_id: str = Field(description="e.g. 'sglang-detokenizer-unbound-fix'")
    repo: str = Field(description="e.g. 'sgl-project/sglang'")
    base_commit: str
    pr_url: Optional[str] = None
    version: str = Field(default="1.0")

    # Graders (from Anthropic + this project)
    graders: list[Grader]
    task_composition: TaskComposition = TaskComposition.HYBRID

    # Hybrid composition config
    gate_graders: list[str] = Field(
        default_factory=list,
        description="Grader IDs that must pass (score > 0) for any reward"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    difficulty: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def total_weight(self) -> float:
        return sum(g.weight for g in self.graders)

    @computed_field
    @property
    def grader_type_weights(self) -> dict[str, float]:
        """Weight breakdown by grader type (for auditing)."""
        breakdown: dict[str, float] = {}
        for g in self.graders:
            key = g.grader_type.value
            breakdown[key] = breakdown.get(key, 0.0) + g.weight
        return breakdown

    def compute_score(self, grader_scores: dict[str, float]) -> float:
        """Compute final task score from per-grader scores.

        Implements the hybrid composition logic:
        1. Check gates — if any gate grader scores 0, return 0
        2. Compute weighted average of remaining graders
        3. Clamp to [0.0, 1.0]
        """
        # Gate check
        for gate_id in self.gate_graders:
            if grader_scores.get(gate_id, 0.0) <= 0.0:
                return 0.0

        # Weighted combination
        total_w = 0.0
        total_score = 0.0
        for g in self.graders:
            s = grader_scores.get(g.id, 0.0)
            total_score += g.weight * s
            total_w += g.weight

        if total_w == 0:
            return 0.0
        return max(0.0, min(1.0, total_score / total_w))


# ── LLM Rubric (model-based grader detail) ────────────────────────────
# Kept from existing rubric.py, integrated into grader framework

class RuleScope(str, Enum):
    REPO = "repo"       # Applies to all tasks in this repo
    TASK = "task"        # Task-specific

class Applicability(BaseModel):
    path_globs: Optional[list[str]] = None
    path_excludes: Optional[list[str]] = None
    languages: Optional[list[str]] = None

class RubricRule(BaseModel):
    """One rule for the LLM judge. Maps to a Check in the model_based grader."""
    id: str
    text: str = Field(description="Rule statement the LLM evaluates against")
    source: SourceRef
    scope: RuleScope = RuleScope.REPO
    weight: float = Field(default=1.0, ge=0.0)
    applicability: Applicability = Field(default_factory=Applicability)
    tags: list[str] = Field(default_factory=list)


# ── Evaluation Results ────────────────────────────────────────────────

class CheckResult(BaseModel):
    """Result of one check execution."""
    check_id: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0, description="0.0 or 1.0 for binary, continuous for partial")
    detail: str = Field(default="")
    evidence: Optional[str] = Field(default=None, description="Quoted output/snippet")

class GraderResult(BaseModel):
    """Result of one grader execution."""
    grader_id: str
    check_results: list[CheckResult]
    score: float = Field(ge=0.0, le=1.0)
    grader_type: GraderType
    method: GraderMethod

class TaskEvalResult(BaseModel):
    """Full evaluation result for one (task, trial) pair.

    This is what test.sh ultimately produces — both the detailed
    per-grader results and the final composed score.
    """
    task_id: str
    agent_id: str
    trial_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    grader_results: list[GraderResult]
    final_score: float = Field(ge=0.0, le=1.0)

    # SWE-RM style breakdown for RL training
    execution_score: Optional[float] = Field(
        default=None,
        description="Deterministic grader score (execution bucket analog)"
    )
    model_score: Optional[float] = Field(
        default=None,
        description="Model-based grader score (Score_EF analog)"
    )
    hybrid_score: Optional[float] = Field(
        default=None,
        description="Combined score for RL reward shaping"
    )


# ── Reward Output (Harbor-compatible) ─────────────────────────────────

class RewardOutput(BaseModel):
    """What gets written to /logs/verifier/reward.json.

    Harbor reads reward.txt (single float) or reward.json (dict of floats).
    We write both: reward.txt with final_score, reward.json with breakdown.
    """
    # Primary score (goes into reward.txt too)
    reward: float = Field(ge=0.0, le=1.0)

    # Named component scores (for reward.json)
    components: dict[str, float] = Field(
        default_factory=dict,
        description="e.g. {'behavioral': 0.6, 'regression': 0.2, 'style': 0.1}"
    )

    # RL-specific signals
    execution_bucket: Optional[float] = Field(
        default=None,
        description="SWE-RM style: +1.0 resolved, 0.0 failed, -0.5 unfinished"
    )
    model_reward: Optional[float] = Field(
        default=None,
        description="Continuous LLM judge score for RL reward shaping"
    )
```

### 4.3 Mapping to existing test.sh

The current `test.sh` pattern already follows this design implicitly:

```bash
WEIGHTS[behavioral_unbound]=0.35     # -> Grader{id="behavioral", type=DETERMINISTIC, method=FAIL_TO_PASS}
WEIGHTS[behavioral_except]=0.30      #    with two Checks inside it
WEIGHTS[passtopass]=0.10             # -> Grader{id="regression", type=DETERMINISTIC, method=PASS_TO_PASS}
WEIGHTS[structural]=0.10             # -> Grader{id="structural", type=DETERMINISTIC, method=AST_CHECK}
WEIGHTS[antistub]=0.05               # -> Check within "regression" grader
WEIGHTS[config]=0.10                 # -> Grader{id="style_rubric", type=MODEL_BASED, method=RUBRIC_SCORING}
```

The schema makes this structure explicit, auditable, and machine-readable.

### 4.4 reward.json Output Format

```json
{
    "reward": 0.85,
    "components": {
        "behavioral": 0.65,
        "regression": 0.10,
        "structural": 0.05,
        "style_rubric": 0.05
    },
    "execution_bucket": 1.0,
    "model_reward": 0.72
}
```

Harbor reads `reward.txt` (containing `0.85`) as the primary signal. RL pipelines read `reward.json` for the hybrid decomposition.

### 4.5 Sidecar Manifest File

Each task gets an `eval_manifest.yaml` alongside `task.toml`:

```yaml
task_id: sglang-detokenizer-unbound-fix
repo: sgl-project/sglang
base_commit: "17f43d15"
pr_url: "https://github.com/sgl-project/sglang/pull/21471"
task_composition: hybrid
gate_graders: [behavioral]

graders:
  - id: behavioral
    grader_type: deterministic
    method: fail_to_pass
    weight: 0.65
    composition: weighted
    checks:
      - id: constructor-crash-no-unbound
        description: "Constructor failure does not raise UnboundLocalError"
        weight: 0.35
        origin: pr_diff
      - id: except-block-completes
        description: "Except block runs to completion without crashing"
        weight: 0.30
        origin: pr_diff

  - id: regression
    grader_type: deterministic
    method: pass_to_pass
    weight: 0.10
    composition: all_pass
    checks:
      - id: syntax-valid
        description: "Target file parses without SyntaxError"
        weight: 1.0
        origin: repo_tests
      - id: antistub
        description: "File is not a stub/minimal replacement"
        weight: 1.0
        origin: repo_tests

  - id: structural
    grader_type: deterministic
    method: static_analysis
    weight: 0.10
    composition: weighted
    checks:
      - id: ruff-clean
        description: "ruff check passes on changed files"
        weight: 1.0
        origin: static
        source:
          file: "CLAUDE.md"
          lines: [12, 12]
          commit: "17f43d15"

  - id: style_rubric
    grader_type: model_based
    method: rubric_scoring
    weight: 0.15
    composition: weighted
    checks:
      - id: defensive-teardown
        description: "Error handling uses defensive patterns (hasattr/null checks)"
        weight: 2.0
        origin: agent_config
        source:
          file: ".claude/skills/write-sglang-test/SKILL.md"
          lines: [9, 9]
          commit: "17f43d15"
      - id: match-surrounding-style
        description: "New code matches surrounding file style"
        weight: 1.0
        origin: agent_config
        source:
          file: ".claude/skills/write-sglang-test/SKILL.md"
          lines: [8, 8]
          commit: "17f43d15"
```

## 5. Answers to Specific Research Questions

**Q: What does the Anthropic blog say about grader composition?**
Three modes: weighted (combined scores hit threshold), binary (all must pass), hybrid (some gated, rest weighted). Recommendations: grade outcome over transcript, build in partial credit, deterministic first then LLM for nuance, isolate dimensions across separate LLM judges.

**Q: How does SWE-RM combine `ExecutionBucket` with softmax(YES/NO logprobs)?**
Additive, not weighted: `r(q, tau) = ExecutionBucket(q, tau) + Score_EF(q, tau, patch)`. ExecutionBucket: +1 (resolved), 0 (failed), -0.5 (unfinished). `Score_EF = exp(l_y) / (exp(l_y) + exp(l_n))` ∈ [0, 1]. Bucket coarse-classifies; RM differentiates within bucket. For RL, classification accuracy (AUC) and calibration (ECE) matter more than raw ranking.

**Q: METR's recommended success-criteria definition?**
Single `score()` returning `float | None` ∈ [0.0, 1.0]; `None` means manual scoring. Quality guidance: incompetent agents below 0.1, competent above 0.9, scoring on a continuum. Multi-signal composition must happen inside `score()`; no built-in mechanism.

## 6. Sources

- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Harbor Framework: Task Structure](https://harborframework.com/docs/tasks)
- [SWE-bench Datasets Guide](https://www.swebench.com/SWE-bench/guides/datasets/)
- [SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/)
- [METR Task Standard (STANDARD.md)](https://github.com/METR/task-standard/blob/main/STANDARD.md)
- [METR Task Standard (template.py)](https://github.com/METR/task-standard/blob/main/template/template.py)
- [METR Task Development Guide](https://taskdev.metr.org/specification/)
- [Inspect AI: Scorers](https://inspect.aisi.org.uk/scorers.html)
- [Inspect AI: Tasks](https://inspect.aisi.org.uk/tasks.html)
- [Inspect AI API Reference](https://inspect.aisi.org.uk/reference/inspect_ai.html)
- [UK AISI Autonomous Systems Evaluation Standard](https://ukgovernmentbeis.github.io/as-evaluation-standard/)
- [Vivaria](https://vivaria.metr.org/)
- [SWE-RM Paper](https://arxiv.org/abs/2512.21919)
- [SWE-RL Paper](https://arxiv.org/abs/2502.18449)
- [AgentBench (THUDM)](https://github.com/THUDM/AgentBench)
- [AgentBench Config Guide](https://github.com/THUDM/AgentBench/blob/main/docs/Config_en.md)
