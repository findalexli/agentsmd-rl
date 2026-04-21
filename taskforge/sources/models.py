"""Normalized external task-source models.

These models are intentionally separate from EvalManifest. External systems
produce candidate tasks; taskforge remains responsible for rendering and
validating native task artifacts.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from taskforge.models import (
    Check,
    CheckOrigin,
    CheckType,
    EvalManifest,
    SourcePR,
)


class SourceKind(str, Enum):
    """Where an external candidate task came from."""

    REBENCH_V2 = "rebench_v2"
    R2E_COMMIT = "r2e_commit"
    SWEBENCH_PR = "swebench_pr"
    SWESMITH_SYNTHETIC = "swesmith_synthetic"
    MANUAL = "manual"


class InstallConfig(BaseModel):
    """Install and test metadata from an upstream benchmark row."""

    install: list[str] = Field(default_factory=list)
    test_cmd: list[str] = Field(default_factory=list)
    log_parser: str = ""
    base_image_name: str = ""
    docker_specs: dict[str, Any] | None = None

    @field_validator("install", "test_cmd", mode="before")
    @classmethod
    def _coerce_command_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [item for item in value if isinstance(item, str) and item.strip()]
        raise TypeError("commands must be a string or list of strings")


class TestEvidence(BaseModel):
    """Patch and expected test-status evidence for a candidate task."""

    patch: str = ""
    test_patch: str = ""
    fail_to_pass: list[str] = Field(default_factory=list)
    pass_to_pass: list[str] = Field(default_factory=list)
    install_config: InstallConfig = Field(default_factory=InstallConfig)

    @model_validator(mode="after")
    def _expectations_do_not_overlap(self) -> "TestEvidence":
        overlap = set(self.fail_to_pass).intersection(self.pass_to_pass)
        if overlap:
            names = ", ".join(sorted(overlap)[:5])
            raise ValueError(
                f"tests cannot be both fail_to_pass and pass_to_pass: {names}"
            )
        return self


class SourceEvidence(BaseModel):
    """Provenance that does not fit in EvalManifest.source yet."""

    kind: SourceKind
    upstream_id: str = ""
    url: str = ""
    pr_number: int = 0
    merge_commit: str = ""
    language: str = ""
    image_name: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CandidateTask(BaseModel):
    """A normalized task candidate before native taskforge rendering."""

    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str
    source: SourceEvidence
    tests: TestEvidence = Field(default_factory=TestEvidence)

    @field_validator("repo")
    @classmethod
    def _repo_has_owner(cls, value: str) -> str:
        if "/" not in value:
            raise ValueError("repo must be in owner/name form")
        owner, name = value.split("/", 1)
        if not owner or not name:
            raise ValueError("repo must be in owner/name form")
        return value

    @property
    def owner(self) -> str:
        return self.repo.split("/", 1)[0]

    @property
    def repo_name(self) -> str:
        return self.repo.split("/", 1)[1]

    @property
    def task_slug(self) -> str:
        slug = self.instance_id.lower()
        slug = re.sub(r"[^a-z0-9._-]+", "-", slug)
        slug = slug.strip(".-_")
        return slug or "imported-task"

    def to_manifest(self) -> EvalManifest:
        """Build a native EvalManifest with one check per expected test name."""

        checks: list[Check] = []
        for test_name in self.tests.fail_to_pass:
            checks.append(
                Check(
                    id=_check_id("ftp", test_name),
                    type=CheckType.FAIL_TO_PASS,
                    origin=CheckOrigin.PR_DIFF,
                    description=f"Imported failing test should pass: {test_name}",
                )
            )
        for test_name in self.tests.pass_to_pass:
            checks.append(
                Check(
                    id=_check_id("ptp", test_name),
                    type=CheckType.PASS_TO_PASS,
                    origin=CheckOrigin.REPO_TESTS,
                    description=f"Imported passing test should stay passing: {test_name}",
                )
            )

        return EvalManifest(
            source=SourcePR(
                repo=self.repo,
                pr=self.source.pr_number,
                base_commit=self.base_commit,
                merge_commit=self.source.merge_commit,
            ),
            checks=checks,
            rubric=[],
            distractors=[],
        )


def _check_id(prefix: str, test_name: str) -> str:
    slug = test_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    if len(slug) > 72:
        slug = slug[:72].rstrip("_")
    return f"{prefix}_{slug or 'unnamed'}"
