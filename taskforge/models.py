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


class RubricRule(BaseModel):
    """A soft rule evaluated by LLM judge — not programmatically verifiable."""
    rule: str                        # Verbatim text from config file
    source: SourceRef                # Where it came from


class SourcePR(BaseModel):
    """Provenance: which PR this task was derived from."""
    repo: str                        # "owner/repo"
    pr: int
    base_commit: str
    merge_commit: str = ""


class EvalManifest(BaseModel):
    """Per-task evaluation specification.

    Scoring is binary: all checks pass → reward 1.0, any fail → 0.0.
    Check types (f2p/p2p) and origins are for analysis, not weighted scoring.
    """
    version: Literal["2.0"] = "2.0"
    source: SourcePR
    checks: list[Check] = Field(default_factory=list)
    rubric: list[RubricRule] = Field(default_factory=list)  # LLM judge only

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
