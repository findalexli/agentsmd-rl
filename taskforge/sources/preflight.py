"""Cheap candidate preflight checks before expensive Docker validation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from taskforge.execution.log_parsers import NAME_TO_PARSER
from taskforge.sources.models import CandidateTask


class PreflightResult(BaseModel):
    accepted: bool
    reasons: list[str] = Field(default_factory=list)


def preflight_candidate(candidate: CandidateTask) -> PreflightResult:
    """Reject candidates with obvious missing evidence.

    This is deliberately deterministic. LLM-based preflight can be added later,
    but should remain advisory and separate from final reward.
    """

    reasons: list[str] = []
    if not candidate.base_commit:
        reasons.append("missing base_commit")
    if not candidate.problem_statement.strip():
        reasons.append("missing problem_statement")
    if not candidate.tests.patch.strip():
        reasons.append("missing gold patch")
    if not candidate.tests.test_patch.strip():
        reasons.append("missing test patch")
    if not candidate.tests.fail_to_pass:
        reasons.append("missing FAIL_TO_PASS expectations")
    if not candidate.tests.pass_to_pass:
        reasons.append("missing PASS_TO_PASS expectations")

    parser = candidate.tests.install_config.log_parser.strip()
    if (candidate.tests.fail_to_pass or candidate.tests.pass_to_pass) and not parser:
        reasons.append("missing log parser")
    elif parser and parser not in NAME_TO_PARSER:
        reasons.append(f"unknown log parser: {parser}")

    return PreflightResult(accepted=not reasons, reasons=reasons)
