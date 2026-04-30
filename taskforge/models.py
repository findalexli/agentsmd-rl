"""Core data models for taskforge."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# PR candidate (scouting / prefilter)
# ---------------------------------------------------------------------------

class PRCandidate(BaseModel):
    """A GitHub PR candidate for task generation."""
    repo: str                          # "owner/repo"
    pr_number: int
    title: str = ""
    pr_body: str = ""
    changed_files: int = 0
    additions: int = 0
    deletions: int = 0
    merged_at: str = ""
    merge_sha: str = ""
    file_paths: list[str] = Field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions

    @property
    def repo_short(self) -> str:
        return self.repo.split("/")[-1]


# ---------------------------------------------------------------------------
# Eval manifest — per-task grading specification
# ---------------------------------------------------------------------------

class CheckType(str, Enum):
    """How a check relates to the gold patch."""
    FAIL_TO_PASS = "fail_to_pass"   # Must fail on base, pass on fix
    PASS_TO_PASS = "pass_to_pass"   # Must pass before AND after fix


class CheckOrigin(str, Enum):
    """Where the check was derived from."""
    PR_DIFF = "pr_diff"             # Directly from the PR's behavioral change
    REPO_TESTS = "repo_tests"       # Pre-existing repo test suite
    AGENT_CONFIG = "agent_config"   # Rule from CLAUDE.md / AGENTS.md / etc.
    STATIC = "static"               # Anti-gaming, anti-stub, syntax gates


class SourceRef(BaseModel):
    """Points to the exact location a rule was extracted from."""
    path: str                        # Repo-relative, e.g. "AGENTS.md"
    lines: str = ""                  # e.g. "43" or "30-35"
    commit: str = ""                 # SHA at extraction time


class Check(BaseModel):
    """A single verifiable assertion in test.sh."""
    id: str                          # Slug, e.g. "empty_stem_gets_fallback"
    type: CheckType
    origin: CheckOrigin
    description: str                 # One-line human-readable
    source: SourceRef | None = None  # Required when origin == agent_config

    @model_validator(mode="after")
    def _agent_config_needs_source(self) -> Check:
        if self.origin == CheckOrigin.AGENT_CONFIG and self.source is None:
            raise ValueError("agent_config checks must have a source ref")
        return self


class VerificationMethod(str, Enum):
    """How a rubric rule is verified at eval time."""
    PROGRAMMATIC = "programmatic"    # grep/AST check baked into test.sh (deterministic)
    LLM_JUDGE = "llm_judge"         # Gemini/Claude evaluates diff vs rule (soft)
    SEMANTIC_DIFF = "semantic_diff"  # Gemini compares gold config vs agent config (Track 2)


class RubricRule(BaseModel):
    """A positive rubric: convention the gold solution FOLLOWS.

    Must be derived from an actual agent config file (CLAUDE.md, AGENTS.md, etc.)
    with specific evidence from the gold diff demonstrating compliance.

    verification controls HOW the rule is checked at eval time:
    - programmatic: baked into test.sh (grep, AST check, etc.) — deterministic
    - llm_judge: Gemini reads agent diff + rule, decides pass/fail — soft
    - semantic_diff: Gemini compares gold config edit vs agent edit — Track 2
    """
    rule: str                        # What the agent should do
    source: SourceRef | None = None  # Where rule came from (required for quality)
    reference: str | None = None     # Gold answer for agentmd-edit tasks (optional)
    evidence: str | None = None      # How the gold solution demonstrates compliance
    category: str | None = None      # naming, style, architecture, testing, etc.
    verification: VerificationMethod = VerificationMethod.LLM_JUDGE  # default: LLM
    check_cmd: str | None = None     # For programmatic: shell command that exits 0 on pass


class DistractorRule(BaseModel):
    """A negative rubric: convention that creates a COLLISION.

    Rules from config files that SEEM relevant but following them would produce
    worse code, wasted effort, or bugs for this specific PR. Only genuine
    collisions — not merely irrelevant rules.

    Collision types:
    - rule_conflict: two valid rules conflict, agent must choose
    - scope_ambiguity: rule's applicability is genuinely ambiguous
    - meta_confusion: writing ABOUT a pattern vs applying it
    - architecture_boundary: applying a pattern beyond its intended scope
    - would_cause_bug: following the rule introduces an error
    """
    rule: str                        # The distracting convention
    source: SourceRef | None = None  # Where rule came from
    collision_type: str = ""         # rule_conflict, scope_ambiguity, etc.
    why_distracting: str = ""        # What goes wrong if agent follows this
    severity: str = "medium"         # high (bug), medium (wasted effort), low (minor)


class GoldConfigEdit(BaseModel):
    """A config/doc file change extracted from the gold solution.

    For agentmd-edit tasks, the gold patch modifies config files alongside
    code files. This captures the EXACT expected config change — deterministic,
    no LLM hallucination. Used by the judge to evaluate whether the agent
    made the right config edits.
    """
    path: str                        # Repo-relative path, e.g. "AGENTS.md"
    tier: int = 1                    # 1 = agent instruction, 2 = documentation
    gold_added: str = ""             # Lines added by gold solution
    gold_removed: str = ""           # Lines removed by gold solution
    diff_hunk: str = ""              # Full diff hunk for context (optional)


class SourcePR(BaseModel):
    """Provenance: which PR this task was derived from."""
    repo: str                        # "owner/repo"
    pr: int
    base_commit: str
    merge_commit: str = ""


class TaskKind(str, Enum):
    """Task shape — drives folder placement and per-track expectations.

    code_fix              — agent fixes a bug; behavioral fail_to_pass tests are required.
                            Track 1 is the canonical signal. (markdown_following/)
    code_with_config      — bundled: agent fixes code AND updates an instruction
                            markdown. Tracks 1 + 2 both required.
                            (markdown_edits/)
    markdown_authoring    — PR only modifies SKILL.md / AGENTS.md / CLAUDE.md.
                            No behavioral test exists; Track 2 (semantic diff vs
                            gold markdown) is the only meaningful score.
                            (markdown_authoring/)
    """
    CODE_FIX = "code_fix"
    CODE_WITH_CONFIG = "code_with_config"
    MARKDOWN_AUTHORING = "markdown_authoring"


class TaskMeta(BaseModel):
    """The `task:` block in eval_manifest.yaml.

    Optional today for back-compat; new scaffolds set it explicitly.
    """
    name: str | None = None
    kind: TaskKind = TaskKind.CODE_FIX
    difficulty: str | None = None
    tags: list[str] = Field(default_factory=list)


class EvalManifest(BaseModel):
    """Per-task evaluation specification.

    Scoring is binary: all checks pass → reward 1.0, any fail → 0.0.

    Four evaluation tracks:
      1. checks (hard tests)  — test.sh, deterministic pass/fail
      2. config_edits         — gold config changes, Gemini semantic comparison
      3. rubric               — positive: conventions the gold solution follows
      4. distractors          — negative: collision rules the gold deliberately ignores

    Per-kind contract (see TaskKind):
      - code_fix:           checks REQUIRED (≥1 fail_to_pass)
      - code_with_config:   checks REQUIRED + config_edits REQUIRED
      - markdown_authoring: config_edits REQUIRED; checks may be empty
    """
    version: Literal["2.0"] = "2.0"
    source: SourcePR
    task: TaskMeta = Field(default_factory=TaskMeta)
    checks: list[Check] = Field(default_factory=list)
    config_edits: list[GoldConfigEdit] = Field(default_factory=list)  # Track 2
    rubric: list[RubricRule] = Field(default_factory=list)            # Track 3 positive
    distractors: list[DistractorRule] = Field(default_factory=list)   # Track 4 negative

    @model_validator(mode="after")
    def _kind_contract(self) -> EvalManifest:
        """Best-effort kind contract. Loose for back-compat — strict checks
        belong in a dedicated lint pass, not in model load.
        """
        kind = self.task.kind
        if kind == TaskKind.MARKDOWN_AUTHORING and not self.config_edits:
            # Pure md-authoring with no gold edits has nothing to score.
            raise ValueError("markdown_authoring requires config_edits")
        if kind == TaskKind.CODE_WITH_CONFIG and not self.config_edits:
            raise ValueError("code_with_config requires config_edits")
        return self

    # -- helpers --

    def to_yaml(self) -> str:
        """Serialize to YAML for eval_manifest.yaml."""
        import yaml
        return yaml.dump(
            self.model_dump(mode="json", exclude_none=True),
            default_flow_style=False,
            sort_keys=False,
        )

    @classmethod
    def from_yaml(cls, path: str) -> EvalManifest:
        """Load from an eval_manifest.yaml file."""
        import yaml
        from pathlib import Path
        data = yaml.safe_load(Path(path).read_text())
        return cls.model_validate(data)

    @classmethod
    def from_task_dir(cls, task_dir: str) -> EvalManifest | None:
        """Load from a task directory (tries eval_manifest.yaml)."""
        from pathlib import Path
        manifest = Path(task_dir) / "eval_manifest.yaml"
        if manifest.exists():
            return cls.from_yaml(str(manifest))
        return None
