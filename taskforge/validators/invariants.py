"""Validation invariants shared by imported and native taskforge tasks."""

from __future__ import annotations

from pydantic import BaseModel, Field

from taskforge.execution.log_parsers import TestStatus


class ExpectedTransitionReport(BaseModel):
    """A normalized report for expected test-status transitions."""

    ok: bool
    missing: list[str] = Field(default_factory=list)
    unexpected: dict[str, str] = Field(default_factory=dict)


def check_gold_expectations(
    parsed_statuses: dict[str, str],
    *,
    fail_to_pass: list[str],
    pass_to_pass: list[str],
) -> ExpectedTransitionReport:
    """Check that all expected tests pass after the gold patch is applied."""

    expected = list(fail_to_pass) + list(pass_to_pass)
    missing: list[str] = []
    unexpected: dict[str, str] = {}
    for name in expected:
        status = parsed_statuses.get(name)
        if status is None:
            missing.append(name)
        elif status != TestStatus.PASSED.value:
            unexpected[name] = status
    return ExpectedTransitionReport(
        ok=not missing and not unexpected, missing=missing, unexpected=unexpected
    )


def check_expected_transition(
    base_statuses: dict[str, str],
    gold_statuses: dict[str, str],
    *,
    fail_to_pass: list[str],
    pass_to_pass: list[str],
) -> ExpectedTransitionReport:
    """Check nop=0/gold=1-style transitions from parsed status maps."""

    missing: list[str] = []
    unexpected: dict[str, str] = {}
    observed_base_fail_to_pass_failure = False

    for name in fail_to_pass:
        base = base_statuses.get(name)
        gold = gold_statuses.get(name)
        if gold is None:
            missing.append(name)
            continue
        if base == TestStatus.PASSED.value:
            unexpected[f"base:{name}"] = base
        elif base is not None:
            observed_base_fail_to_pass_failure = True
        if gold != TestStatus.PASSED.value:
            unexpected[f"gold:{name}"] = gold

    if fail_to_pass and not observed_base_fail_to_pass_failure:
        unexpected["base:fail_to_pass"] = "no observed fail-to-pass failure"

    for name in pass_to_pass:
        base = base_statuses.get(name)
        gold = gold_statuses.get(name)
        if base is None or gold is None:
            missing.append(name)
            continue
        if base != TestStatus.PASSED.value:
            unexpected[f"base:{name}"] = base
        if gold != TestStatus.PASSED.value:
            unexpected[f"gold:{name}"] = gold

    return ExpectedTransitionReport(
        ok=not missing and not unexpected, missing=missing, unexpected=unexpected
    )
