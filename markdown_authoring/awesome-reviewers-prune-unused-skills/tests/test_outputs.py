"""Behavioral checks for awesome-reviewers-prune-unused-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-reviewers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/async-error-callbacks/SKILL.md')
    assert '_skills/async-error-callbacks/SKILL.md' in text, "expected to find: " + '_skills/async-error-callbacks/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/avoid-code-duplication/SKILL.md')
    assert '_skills/avoid-code-duplication/SKILL.md' in text, "expected to find: " + '_skills/avoid-code-duplication/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/balance-organization-with-constraints/SKILL.md')
    assert '_skills/balance-organization-with-constraints/SKILL.md' in text, "expected to find: " + '_skills/balance-organization-with-constraints/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/compatible-null-annotations/SKILL.md')
    assert '_skills/compatible-null-annotations/SKILL.md' in text, "expected to find: " + '_skills/compatible-null-annotations/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/component-reuse-first/SKILL.md')
    assert '_skills/component-reuse-first/SKILL.md' in text, "expected to find: " + '_skills/component-reuse-first/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/consistent-ai-interfaces/SKILL.md')
    assert '_skills/consistent-ai-interfaces/SKILL.md' in text, "expected to find: " + '_skills/consistent-ai-interfaces/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/consistent-camelcase-naming/SKILL.md')
    assert '_skills/consistent-camelcase-naming/SKILL.md' in text, "expected to find: " + '_skills/consistent-camelcase-naming/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/consistent-provider-options/SKILL.md')
    assert '_skills/consistent-provider-options/SKILL.md' in text, "expected to find: " + '_skills/consistent-provider-options/SKILL.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/consistent-semantic-naming/SKILL.md')
    assert '_skills/consistent-semantic-naming/SKILL.md' in text, "expected to find: " + '_skills/consistent-semantic-naming/SKILL.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/consistent-technical-term-translation/SKILL.md')
    assert '_skills/consistent-technical-term-translation/SKILL.md' in text, "expected to find: " + '_skills/consistent-technical-term-translation/SKILL.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/context-rich-log-messages/SKILL.md')
    assert '_skills/context-rich-log-messages/SKILL.md' in text, "expected to find: " + '_skills/context-rich-log-messages/SKILL.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/document-api-schemas/SKILL.md')
    assert '_skills/document-api-schemas/SKILL.md' in text, "expected to find: " + '_skills/document-api-schemas/SKILL.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/document-configuration-decisions/SKILL.md')
    assert '_skills/document-configuration-decisions/SKILL.md' in text, "expected to find: " + '_skills/document-configuration-decisions/SKILL.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/document-intentional-choices/SKILL.md')
    assert '_skills/document-intentional-choices/SKILL.md' in text, "expected to find: " + '_skills/document-intentional-choices/SKILL.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/document-public-api-boundaries/SKILL.md')
    assert '_skills/document-public-api-boundaries/SKILL.md' in text, "expected to find: " + '_skills/document-public-api-boundaries/SKILL.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/document-security-exceptions/SKILL.md')
    assert '_skills/document-security-exceptions/SKILL.md' in text, "expected to find: " + '_skills/document-security-exceptions/SKILL.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/documentation-best-practices/SKILL.md')
    assert '_skills/documentation-best-practices/SKILL.md' in text, "expected to find: " + '_skills/documentation-best-practices/SKILL.md'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/enforce-authentication-boundaries/SKILL.md')
    assert '_skills/enforce-authentication-boundaries/SKILL.md' in text, "expected to find: " + '_skills/enforce-authentication-boundaries/SKILL.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/ensure-deterministic-queries/SKILL.md')
    assert '_skills/ensure-deterministic-queries/SKILL.md' in text, "expected to find: " + '_skills/ensure-deterministic-queries/SKILL.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/explicit-api-parameters/SKILL.md')
    assert '_skills/explicit-api-parameters/SKILL.md' in text, "expected to find: " + '_skills/explicit-api-parameters/SKILL.md'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/explicit-code-organization-patterns/SKILL.md')
    assert '_skills/explicit-code-organization-patterns/SKILL.md' in text, "expected to find: " + '_skills/explicit-code-organization-patterns/SKILL.md'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/explicit-over-implicit-configuration/SKILL.md')
    assert '_skills/explicit-over-implicit-configuration/SKILL.md' in text, "expected to find: " + '_skills/explicit-over-implicit-configuration/SKILL.md'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/explicit-version-constraints/SKILL.md')
    assert '_skills/explicit-version-constraints/SKILL.md' in text, "expected to find: " + '_skills/explicit-version-constraints/SKILL.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/externalize-configuration-values/SKILL.md')
    assert '_skills/externalize-configuration-values/SKILL.md' in text, "expected to find: " + '_skills/externalize-configuration-values/SKILL.md'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/flexible-api-inputs/SKILL.md')
    assert '_skills/flexible-api-inputs/SKILL.md' in text, "expected to find: " + '_skills/flexible-api-inputs/SKILL.md'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/follow-naming-conventions/SKILL.md')
    assert '_skills/follow-naming-conventions/SKILL.md' in text, "expected to find: " + '_skills/follow-naming-conventions/SKILL.md'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/format-for-rendering-compatibility/SKILL.md')
    assert '_skills/format-for-rendering-compatibility/SKILL.md' in text, "expected to find: " + '_skills/format-for-rendering-compatibility/SKILL.md'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/handle-errors-gracefully/SKILL.md')
    assert '_skills/handle-errors-gracefully/SKILL.md' in text, "expected to find: " + '_skills/handle-errors-gracefully/SKILL.md'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/handle-exceptions-with-specificity/SKILL.md')
    assert '_skills/handle-exceptions-with-specificity/SKILL.md' in text, "expected to find: " + '_skills/handle-exceptions-with-specificity/SKILL.md'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/internationalize-ui-text/SKILL.md')
    assert '_skills/internationalize-ui-text/SKILL.md' in text, "expected to find: " + '_skills/internationalize-ui-text/SKILL.md'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/isolate-test-environments/SKILL.md')
    assert '_skills/isolate-test-environments/SKILL.md' in text, "expected to find: " + '_skills/isolate-test-environments/SKILL.md'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/keep-tests-simple/SKILL.md')
    assert '_skills/keep-tests-simple/SKILL.md' in text, "expected to find: " + '_skills/keep-tests-simple/SKILL.md'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/maintain-api-naming-consistency/SKILL.md')
    assert '_skills/maintain-api-naming-consistency/SKILL.md' in text, "expected to find: " + '_skills/maintain-api-naming-consistency/SKILL.md'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/optimize-ci-type-checking/SKILL.md')
    assert '_skills/optimize-ci-type-checking/SKILL.md' in text, "expected to find: " + '_skills/optimize-ci-type-checking/SKILL.md'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/place-configurations-appropriately/SKILL.md')
    assert '_skills/place-configurations-appropriately/SKILL.md' in text, "expected to find: " + '_skills/place-configurations-appropriately/SKILL.md'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/provide-actionable-examples/SKILL.md')
    assert '_skills/provide-actionable-examples/SKILL.md' in text, "expected to find: " + '_skills/provide-actionable-examples/SKILL.md'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/standardize-model-access/SKILL.md')
    assert '_skills/standardize-model-access/SKILL.md' in text, "expected to find: " + '_skills/standardize-model-access/SKILL.md'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/test-actual-functionality/SKILL.md')
    assert '_skills/test-actual-functionality/SKILL.md' in text, "expected to find: " + '_skills/test-actual-functionality/SKILL.md'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/test-before-documenting/SKILL.md')
    assert '_skills/test-before-documenting/SKILL.md' in text, "expected to find: " + '_skills/test-before-documenting/SKILL.md'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/test-security-boundaries/SKILL.md')
    assert '_skills/test-security-boundaries/SKILL.md' in text, "expected to find: " + '_skills/test-security-boundaries/SKILL.md'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/thread-safe-message-dispatching/SKILL.md')
    assert '_skills/thread-safe-message-dispatching/SKILL.md' in text, "expected to find: " + '_skills/thread-safe-message-dispatching/SKILL.md'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/type-safe-null-handling/SKILL.md')
    assert '_skills/type-safe-null-handling/SKILL.md' in text, "expected to find: " + '_skills/type-safe-null-handling/SKILL.md'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/use-definite-assignment-assertions/SKILL.md')
    assert '_skills/use-definite-assignment-assertions/SKILL.md' in text, "expected to find: " + '_skills/use-definite-assignment-assertions/SKILL.md'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/use-descriptive-names/SKILL.md')
    assert '_skills/use-descriptive-names/SKILL.md' in text, "expected to find: " + '_skills/use-descriptive-names/SKILL.md'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/validate-connection-protocols/SKILL.md')
    assert '_skills/validate-connection-protocols/SKILL.md' in text, "expected to find: " + '_skills/validate-connection-protocols/SKILL.md'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/validate-environment-bindings/SKILL.md')
    assert '_skills/validate-environment-bindings/SKILL.md' in text, "expected to find: " + '_skills/validate-environment-bindings/SKILL.md'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/validate-pattern-matching/SKILL.md')
    assert '_skills/validate-pattern-matching/SKILL.md' in text, "expected to find: " + '_skills/validate-pattern-matching/SKILL.md'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/verify-ai-model-capabilities/SKILL.md')
    assert '_skills/verify-ai-model-capabilities/SKILL.md' in text, "expected to find: " + '_skills/verify-ai-model-capabilities/SKILL.md'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/verify-properties-before-logging/SKILL.md')
    assert '_skills/verify-properties-before-logging/SKILL.md' in text, "expected to find: " + '_skills/verify-properties-before-logging/SKILL.md'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('_skills/versioning-for-migrations/SKILL.md')
    assert '_skills/versioning-for-migrations/SKILL.md' in text, "expected to find: " + '_skills/versioning-for-migrations/SKILL.md'[:80]

