# Agent Evaluation Framework Grading Schema Comparison

Exhaustive comparison of task and grading schemas across 8 leading agent evaluation
frameworks, with a recommended schema for agentsmd-rl.

## 1. Framework-by-Framework Analysis

---

### 1.1 Anthropic — "Demystifying Evals for AI Agents"

**Source:** https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

#### Core Vocabulary

| Term | Definition |
|------|-----------|
| **Task** | A single test with defined inputs and success criteria |
| **Trial** | One execution attempt of a task (multiple trials for consistency) |
| **Grader** | Logic that scores some aspect of performance; a task can have multiple graders, each containing multiple **assertions** (aka checks) |
| **Transcript** | Complete record of a trial (outputs, tool calls, reasoning, intermediate results) |
| **Outcome** | Final state in the environment at trial end |

#### Three Grader Types

| Type | Sub-methods | Strengths | Weaknesses |
|------|-------------|-----------|------------|
| **Code-based** | String match (exact/regex/fuzzy), binary tests (fail-to-pass, pass-to-pass), static analysis (lint/type/security), outcome verification, tool call verification, transcript analysis (turns/tokens) | Fast, cheap, reproducible, objective | Brittle to valid variations, no nuance |
| **Model-based** | Rubric-based scoring, natural language assertions, pairwise comparison, reference-based evaluation, multi-judge consensus | Flexible, captures nuance, handles open-ended tasks | Non-deterministic, expensive, needs calibration |
| **Human** | SME review, crowdsourced judgment, spot-check sampling, A/B testing, inter-annotator agreement | Gold standard quality | Expensive, slow, doesn't scale |

#### Grader Composition

Three modes: **weighted** (combined scores hit a threshold), **binary** (all graders must pass), or **hybrid** (some binary-required, others weighted).

#### Key Recommendations

- **Grade outcome, not transcript** — checking specific tool call sequences is too rigid
- **Partial credit** — a multi-component task should reflect continuum of success
- **Priority:** deterministic first, LLM where necessary, human for calibration
- **Dimensional isolation** — grade each dimension with an isolated LLM judge, not one monolithic judge
- **Calibrate LLM graders** against human experts; provide "Unknown" escape hatch

#### Schema (informal, no formal spec published)

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

---

### 1.2 Harbor Framework

**Source:** https://harborframework.com/docs/tasks

#### Task Schema

```
task-directory/
  instruction.md          # Agent prompt
  task.toml               # Metadata + config
  environment/
    Dockerfile            # Or docker-compose.yaml
  solution/
    solve.sh              # Reference solution (for validation)
  tests/
    test.sh               # Writes reward to /logs/verifier/
```

#### task.toml Schema

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

#### Reward Output

Two formats (Harbor reads `reward.txt` first, falls back to `reward.json`):

- **reward.txt** — single float (e.g. `0.85`)
- **reward.json** — dict of named float metrics: `{"behavioral": 0.6, "regression": 0.2}`

#### Grader Composition

Harbor itself is grader-agnostic — the test.sh script computes its own weighted score.
There is no built-in multi-grader orchestration; that lives in the test script.

#### Source Attribution

None built-in. No standard mechanism for tracing test checks to source files.

---

### 1.3 SWE-bench / SWE-bench Verified

**Source:** https://www.swebench.com/SWE-bench/guides/datasets/

#### Instance Schema

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | str | `owner__repo-PR_number` |
| `repo` | str | `owner/repo` |
| `issue_id` | int | GitHub issue number |
| `base_commit` | str | Repository HEAD before solution PR |
| `problem_statement` | str | Issue title + body |
| `hints_text` | str | Issue comments before PR creation |
| `created_at` | str | PR creation date |
| `patch` | str | Gold patch (minus test code) |
| `test_patch` | str | Test file patch from solution PR |
| `version` | str | Repository package version |
| `environment_setup_commit` | str | Commit for environment setup |
| `FAIL_TO_PASS` | str (JSON list) | Tests that must go from failing to passing |
| `PASS_TO_PASS` | str (JSON list) | Tests that must remain passing |
| `issue_url` | str | GitHub issue URL |
| `pr_url` | str | GitHub PR URL |

SWE-bench Verified adds: `difficulty` (str).

#### Grading

Strictly binary: an instance is "resolved" iff ALL `FAIL_TO_PASS` tests now pass AND
all `PASS_TO_PASS` tests still pass. No partial credit. No multi-signal composition.
No LLM judge. No source attribution.

#### Evaluation Output

```json
{
  "total_instances": 300,
  "submitted_instances": 295,
  "completed_instances": 290,
  "resolved_instances": 147,
  "resolution_rate": 0.49
}
```

Per-instance: `instance_results.jsonl` with pass/fail per test.

#### Limitations (per OpenAI's critique)

- 35.5% of failed instances use narrow tests that reject valid solutions
- 18.8% use wide tests checking things not in the problem statement
- Binary scoring loses all signal about partial progress

---

### 1.4 METR Task Standard

**Source:** https://github.com/METR/task-standard/blob/main/STANDARD.md

#### Task Family Structure

```
task_family_name/
  task_family_name.py     # Defines TaskFamily class
  manifest.yaml           # Resource requirements
  *.py, *.sh, assets      # Supporting files
```

#### TaskFamily Class

```python
class TaskFamily:
    standard_version = "0.5.0"
    required_environment_variables: list[str] = []

    @staticmethod
    def get_tasks() -> dict[str, Task]:
        """Returns mapping of task_name -> task data dict."""

    @staticmethod
    def get_instructions(t: Task) -> str:
        """Agent instructions for this task."""

    @staticmethod
    def get_permissions(t: Task) -> list[str]:
        """e.g. ['full_internet']"""

    @staticmethod
    def get_aux_vm_spec(t: Task) -> VMSpec | None:
        """Auxiliary VM specification (declarative)."""

    @staticmethod
    def install() -> None:
        """Customize build of main container."""

    @staticmethod
    def start(t: Task) -> None:
        """Move assets, start processes, setup services."""

    @staticmethod
    def score(t: Task, submission: str) -> float | None:
        """Returns 0.0-1.0 or None (manual scoring needed)."""
        # MUST NOT coexist with intermediate_score

    @staticmethod
    def intermediate_score(t: Task, submission: str) -> float | None:
        """For ongoing scoring during task execution."""
        # MUST NOT coexist with score

    @staticmethod
    def aggregate_scores(...) -> float | None:
        """Combine intermediate scores."""
        # MUST NOT coexist with score

    @staticmethod
    def teardown(t: Task) -> None:
        """Cleanup."""
```

#### manifest.yaml Schema

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
            count_range: [min, max]  # integer array
            model: string
          cpus: integer (min: 1)
          memory_gb: integer (min: 1)
```

#### Scoring Model

- `score()` returns `float | None` (0.0-1.0, None = manual)
- Single score per task — no built-in multi-grader composition
- No source attribution mechanism
- Scoring quality guidance: "a very incompetent agent shouldn't get more than 0.1,
  a very competent agent should be able to get at least 0.9"
- Tasks should score on a continuum (not just binary)

---

### 1.5 Inspect AI (UK AISI)

**Source:** https://inspect.aisi.org.uk/

#### Task Constructor

```python
Task(
    dataset: Dataset | Sequence[Sample] | None = None,
    setup: Solver | list[Solver] | None = None,
    solver: Solver | Agent | list[Solver] = generate(),
    cleanup: Callable[[TaskState], Awaitable[None]] | None = None,
    scorer: Scorers | None = None,  # Single scorer or list
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

#### Score Type

```python
@dataclass
class Score:
    value: Value      # str | int | float | bool | Sequence | Mapping
    answer: str       # Extracted answer text
    explanation: str   # Reasoning
    metadata: dict[str, Any]
```

#### Built-in Scorers

| Scorer | Type | Description |
|--------|------|-------------|
| `includes()` | Deterministic | Target substring in output |
| `match()` | Deterministic | Target at beginning/end |
| `exact()` | Deterministic | Normalized exact match |
| `pattern()` | Deterministic | Regex extraction |
| `answer()` | Deterministic | "ANSWER:" marker extraction |
| `f1()` | Deterministic | Token-level F1 score |
| `choice()` | Deterministic | Multiple choice |
| `math()` | Deterministic | SymPy expression equivalence |
| `model_graded_qa()` | Model-based | LLM assesses correctness |
| `model_graded_fact()` | Model-based | LLM assesses factual presence |

#### Multi-Scorer Composition

Three patterns:

1. **List of scorers** (independent):
```python
Task(scorer=[scorer_a(), scorer_b()])
```

2. **Single scorer yielding dict** (shared computation):
```python
@scorer(metrics={"dim_a": [mean()], "dim_b": [mean()]})
def multi_dim():
    async def score(state, target):
        return Score(value={"dim_a": 0.8, "dim_b": 0.6})
    return score
```

3. **multi_scorer with reducer** (voting/aggregation):
```python
multi_scorer(
    scorers=[model_graded_qa(model=m) for m in models],
    reducer="mode"  # or "mean", "median", "max"
)
```

#### Epoch Reducers

Built-in: `mean`, `median`, `mode`, `max`, `pass_at_{k}`, `at_least_{k}`

#### Metrics

Built-in: `accuracy()`, `mean()`, `var()`, `std()`, `stderr()`,
`bootstrap_stderr()`, `grouped(metric, field)`

#### UK AISI Evaluation Standard Requirements

- **Primary scorer must be binary** (pass/fail)
- **Auxiliary scorers** provide richer signals beyond binary
- Model grading restricted to **content matching** (not numerical ratings)
- Custom tools/scorers MUST have unit tests
- Quality assurance via frontier model or human completion logs

---

### 1.6 Vivaria (METR)

**Source:** https://vivaria.metr.org/

Vivaria is the runtime for METR Task Standard tasks. It adds:

- **Server** (TypeScript + PostgreSQL): creates task environments, runs agents
- **CLI** (Python): user interface to server
- **pyhooks** (Python): agent-to-server interface for LLM API calls, trace entries

Vivaria does not define its own task schema — it consumes METR Task Standard tasks.
The scoring mechanism is whatever the TaskFamily class implements.

No additional grader composition, source attribution, or multi-signal reward beyond
what the TaskFamily.score() method returns.

---

### 1.7 SWE-RM (Execution-Free Reward Model)

**Source:** https://arxiv.org/abs/2512.21919

#### Architecture

Mixture-of-experts, 30B total / 3B active parameters, based on Qwen3-30B-A3B.
Supports 256k context windows for full multi-turn trajectories.

#### Probability from Logprobs

The verifier generates "Yes" or "No" tokens. Score is computed as:

```
r = exp(l_y) / (exp(l_y) + exp(l_n))
```

where `l_y`, `l_n` are logits for YES/NO tokens. Produces continuous [0,1] score.

#### Hybrid Reward Formula (Equation 1)

```
r(q, tau_i) = ExecutionBucket(q, tau_i) + Score_EF(q, tau_i, patch_i)
```

where ExecutionBucket maps to:

| Outcome | ExecutionBucket Value |
|---------|----------------------|
| Issue resolved (all tests pass) | +1.0 |
| Unfinished (no patch produced) | -0.5 |
| Otherwise (tests fail) | 0.0 |

Score_EF is the continuous [0,1] output from the reward model logprobs formula above.

This is an **additive** combination, not weighted-average. The execution signal provides
coarse bucketing (+1, 0, -0.5) while the RM provides fine-grained differentiation
within each bucket.

#### Key Finding: TTS != RL Quality

Two verifiers with nearly identical test-time scaling improvements produced
strikingly different RL training behavior. The critical difference was
**classification accuracy (AUC)** and **calibration (ECE)**, not just ranking quality.

```
AUC = Pr(r(tau_+) > r(tau_-))
ECE = sum_m (|B_m|/n) * |acc(B_m) - conf(B_m)|
```

A good RL reward model needs high AUC AND low ECE.

#### Data Findings

- Optimal positive:negative ratio is 2:1
- 256k context improves RM@32 from 66.8% (at 16k) to 74.4%
- Hybrid reward (SWE-RM + execution) achieves smoothest learning + highest pass@1

---

### 1.8 AgentBench

**Source:** https://github.com/THUDM/AgentBench (ICLR 2024)

#### Architecture

Client-server with three components:
- **Task Server**: hosts environment, provides descriptions, gives feedback
- **Agent Server**: inference interface
- **Client**: coordinates via max-flow assignment optimization

#### Task Configuration (YAML)

```yaml
# configs/tasks/kg.yaml
import: definition.yaml    # Extended YAML keyword

task_name:
  module: "src.tasks.kg"   # Python module
  workers: 2
  config:
    dataset: "path/to/data"
    ...
```

Extended YAML keywords: `import`, `default`, `overwrite`.

#### Scoring

- Per-environment scoring functions (not standardized across environments)
- 8 environments: OS, DB, KG, Digital Card Game, Lateral Thinking, HouseHolding, WebShopping, WebBrowsing
- Results aggregated into leaderboard across all environments
- Predominantly rule-based (compare agent output to expected output)

#### Alternative AgentBench (github.com/agentbench — distinct project)

Layered scoring:
- Layer 0 (40%): Structural checks (files exist, content matches)
- Layer 1 (40%): Metrics (tool call count vs expected, error rate)
- Layer 2 (20%): Behavioral (tool appropriateness, efficiency, error recovery)
- All pure rule-based, no LLM judges

#### Source Attribution

None.

---

## 2. Comparison Table

| Feature | Anthropic Blog | Harbor | SWE-bench | METR | Inspect AI | Vivaria | SWE-RM | AgentBench |
|---------|---------------|--------|-----------|------|-----------|---------|--------|-----------|
| **Task definition format** | Informal | TOML+Markdown+Dockerfile | JSON/JSONL | Python class+YAML | Python @task decorator | (uses METR) | N/A (reward model) | YAML config |
| **Grader types** | code/model/human | Script-defined | Pytest (binary) | Single score() | Scorer plugins | (uses METR) | Logprobs + exec | Per-environment |
| **Multiple graders per task** | Yes (recommended) | By convention in script | No | No | Yes (list or dict) | No | Yes (hybrid) | No |
| **Grader composition** | Weighted/binary/hybrid | Manual in test.sh | AND (all tests pass) | N/A (single float) | Reducers (mean/mode/max) | N/A | Additive (bucket + RM) | Layered weights |
| **Partial credit** | Recommended | Possible (float reward) | No | Yes (0.0-1.0 float) | Yes (float Score) | Yes | Yes (continuous) | Yes (layered) |
| **Source attribution** | Not formalized | None | test_patch field | None | None | None | None | None |
| **LLM judge support** | Recommended | Not built-in | No | Via score() code | model_graded_qa/fact | Via score() | Core (logprobs) | No |
| **Deterministic tests** | Recommended as primary | test.sh | Pytest exclusively | Via score() code | includes/match/exact/f1 | Via score() | ExecutionBucket | Rule-based |
| **Multi-signal reward** | Described conceptually | reward.json dict | No | No | Dict-valued Score | No | Yes (formal) | Layered |
| **Calibration guidance** | Yes (vs human experts) | No | No | Yes (0.1-0.9 range) | Yes (binary primary) | No | Yes (AUC+ECE) | No |
| **Formal schema spec** | No | Partial (task.toml) | HF dataset card | Python template | Python types | N/A | Paper formulas | Partial (YAML) |

---

## 3. Key Design Insights

### 3.1 Grader Composition: Nobody Has a Clean Standard

The most striking finding is that **no framework has a formal, reusable schema for
multi-grader composition**:

- Anthropic describes it conceptually but publishes no schema
- Harbor pushes it into ad-hoc bash scripts
- SWE-bench uses binary AND (simplest possible)
- METR returns a single float (pushes composition into the score() function)
- Inspect AI comes closest with its multi-scorer + reducer pattern, but it's
  oriented toward Q&A evals, not SWE tasks
- SWE-RM has the most principled approach (additive bucket + continuous RM)
  but it's a reward model paper, not a benchmark spec

**Opportunity: a clean, declarative schema for grader composition would be novel.**

### 3.2 Source Attribution: Only This Project Does It

None of the 8 frameworks trace test checks or rubric rules back to specific
source files and line ranges. SWE-bench has `test_patch` (which file the tests
came from) but no per-check attribution. The `SourceRef` model in this project's
`rubric.py` is genuinely novel.

### 3.3 The SWE-RM Hybrid Insight

The additive formula `ExecutionBucket + Score_EF` is elegant because:
- Execution provides coarse but reliable bucketing
- The RM provides fine-grained differentiation within buckets
- They are additive, not weighted — the RM score shifts within a bucket, never
  overrides the execution signal entirely
- For RL: high AUC + low ECE matter more than raw accuracy

This maps naturally to our architecture:
- `test.sh` deterministic score = our "ExecutionBucket" (reliable, coarse)
- LLM rubric ICR score = our "Score_EF" (nuanced, continuous)

### 3.4 Anthropic's Dimensional Isolation

The recommendation to grade each dimension with an isolated LLM judge (not one
monolithic evaluation) aligns with our rubric.yaml design where each RubricRule
is evaluated independently.

### 3.5 UK AISI's Binary Primary + Auxiliary Pattern

The requirement for a binary primary scorer alongside richer auxiliary metrics
is a clean pattern that avoids the "what does 0.73 mean?" problem while still
capturing useful signal.

---

## 4. Recommended Schema

Taking the best ideas from each framework:

### 4.1 Design Principles

1. **From Anthropic:** Three grader types (deterministic, model-based, human), grade outcome not transcript, partial credit, dimensional isolation for LLM judges
2. **From Harbor:** File-based task structure, test.sh as grader entry point, reward.json for named metrics
3. **From SWE-bench:** FAIL_TO_PASS / PASS_TO_PASS as first-class concepts, instance_id format
4. **From METR:** Single float final score (0.0-1.0), Python-defined scoring
5. **From Inspect AI:** Typed Score objects, multi-scorer with reducers, dict-valued scores, epoch reducers
6. **From SWE-RM:** Additive composition (execution bucket + continuous RM), AUC/ECE for RM quality
7. **From UK AISI:** Binary primary + auxiliary pattern, mandatory unit tests for scorers
8. **Novel (this project):** SourceRef attribution, RubricRule with applicability filters

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

### 4.3 How It Maps to Existing test.sh

The existing test.sh pattern in this project already follows this design implicitly:

```bash
# Current pattern in test.sh:
WEIGHTS[behavioral_unbound]=0.35     # -> Grader{id="behavioral", type=DETERMINISTIC, method=FAIL_TO_PASS}
WEIGHTS[behavioral_except]=0.30      #    with two Checks inside it
WEIGHTS[passtopass]=0.10             # -> Grader{id="regression", type=DETERMINISTIC, method=PASS_TO_PASS}
WEIGHTS[structural]=0.10            # -> Grader{id="structural", type=DETERMINISTIC, method=AST_CHECK}
WEIGHTS[antistub]=0.05              # -> Check within "regression" grader
WEIGHTS[config]=0.10                # -> Grader{id="style_rubric", type=MODEL_BASED, method=RUBRIC_SCORING}
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

Harbor reads `reward.txt` (containing `0.85`) as the primary signal.
RL training pipelines read `reward.json` for the hybrid decomposition.

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

---

## 5. Answers to Specific Research Questions

### Q: What does the Anthropic blog say about grader composition?

Three modes: **weighted** (combined grader scores must hit threshold), **binary** (all
must pass), or **hybrid** (some gated, some weighted). They recommend grading outcome
over transcript, building in partial credit, and using deterministic graders first with
LLM graders for nuance. Each LLM dimension should be graded by an isolated judge, not
a monolithic one.

### Q: How does SWE-RM combine execution_bucket with softmax(YES/NO logprobs)?

**Additive**, not weighted. The hybrid reward is:

```
r(q, tau) = ExecutionBucket(q, tau) + Score_EF(q, tau, patch)
```

ExecutionBucket: +1.0 (resolved), 0.0 (failed), -0.5 (unfinished).
Score_EF: `exp(l_y) / (exp(l_y) + exp(l_n))` from logprobs, giving [0,1].

The execution signal provides coarse bucketing while the RM provides fine-grained
differentiation within each bucket. For RL training, the critical quality metrics
for the RM are classification accuracy (AUC) and calibration (ECE), not just ranking.

### Q: What is the METR Task Standard's recommended way to define success criteria?

A single `score()` method returning `float | None` in [0.0, 1.0], where None means
manual scoring needed. Quality guidance: incompetent agents should score below 0.1,
competent agents should reach at least 0.9. Tasks should score on a continuum. The
standard explicitly supports only a single score; multi-signal composition must happen
inside the score() implementation. There is no built-in grader composition mechanism.

---

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
