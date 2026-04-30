"""Behavioral checks for opik-na-be-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opik")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_quality.mdc')
    assert '**Rule**: When you have repeated string prefixes or patterns, define them as constants with string formatting templates.' in text, "expected to find: " + '**Rule**: When you have repeated string prefixes or patterns, define them as constants with string formatting templates.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_quality.mdc')
    assert '// private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // REMOVED' in text, "expected to find: " + '// private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // REMOVED'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_quality.mdc')
    assert 'private static final Map<AutomationRuleEvaluatorField, String> FIELD_MAP = new EnumMap<>(' in text, "expected to find: " + 'private static final Map<AutomationRuleEvaluatorField, String> FIELD_MAP = new EnumMap<>('[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '**Rule**: Remove commented-out constants and unused field declarations instead of leaving them in the codebase.' in text, "expected to find: " + '**Rule**: Remove commented-out constants and unused field declarations instead of leaving them in the codebase.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '// private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // Don\'t expose' in text, "expected to find: " + '// private static final String WEBHOOK_SECRET_TOKEN_DB = "webhook_secret_token"; // Don\'t expose'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/code_style.mdc')
    assert '- [Code Quality Guidelines](mdc:apps/opik-backend/.cursor/rules/code_quality.mdc)' in text, "expected to find: " + '- [Code Quality Guidelines](mdc:apps/opik-backend/.cursor/rules/code_quality.mdc)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/general.mdc')
    assert 'Use PODAM for generating test data. See the comprehensive [Test Data Generation guidelines](mdc:apps/opik-backend/.cursor/rules/testing.mdc#test-data-generation) in the testing documentation.' in text, "expected to find: " + 'Use PODAM for generating test data. See the comprehensive [Test Data Generation guidelines](mdc:apps/opik-backend/.cursor/rules/testing.mdc#test-data-generation) in the testing documentation.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_assertions.mdc')
    assert '**Why This Is Wrong**: This test extracts actual values from the API response, sorts those same values, and then compares them. This will always pass regardless of whether the API actually sorted corr' in text, "expected to find: " + '**Why This Is Wrong**: This test extracts actual values from the API response, sorts those same values, and then compares them. This will always pass regardless of whether the API actually sorted corr'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_assertions.mdc')
    assert '**Critical Issue**: Tests must verify that the API actually sorts data correctly, not just verify that sorting the same list twice produces the same result.' in text, "expected to find: " + '**Critical Issue**: Tests must verify that the API actually sorts data correctly, not just verify that sorting the same list twice produces the same result.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_assertions.mdc')
    assert '3. **Pre-Sorted Comparison**: Sort original data independently, compare with API results' in text, "expected to find: " + '3. **Pre-Sorted Comparison**: Sort original data independently, compare with API results'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_async_patterns.mdc')
    assert '**Background**: Awaitility should only be used when dealing with truly asynchronous operations. MySQL operations in Opik backend tests are synchronous and transactional.' in text, "expected to find: " + '**Background**: Awaitility should only be used when dealing with truly asynchronous operations. MySQL operations in Opik backend tests are synchronous and transactional.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_async_patterns.mdc')
    assert '**Rule**: Instead of using `Thread.sleep()` to create time gaps, use timestamp manipulation or Instant-based approaches.' in text, "expected to find: " + '**Rule**: Instead of using `Thread.sleep()` to create time gaps, use timestamp manipulation or Instant-based approaches.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/test_async_patterns.mdc')
    assert '**Symptoms**: Tests pass on local machine but fail in GitHub Actions or CI environment.' in text, "expected to find: " + '**Symptoms**: Tests pass on local machine but fail in GitHub Actions or CI environment.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/testing.mdc')
    assert '**Note**: For test data generation in parameterized tests, follow the [PODAM guidelines](#podam-configuration) above. Let the factory generate random values and only override when necessary for the sp' in text, "expected to find: " + '**Note**: For test data generation in parameterized tests, follow the [PODAM guidelines](#podam-configuration) above. Let the factory generate random values and only override when necessary for the sp'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/testing.mdc')
    assert '**Critical**: When testing sorting/filtering functionality, ensure ALL fields from the corresponding factory class are included in parameterized tests at least once.' in text, "expected to find: " + '**Critical**: When testing sorting/filtering functionality, ensure ALL fields from the corresponding factory class are included in parameterized tests at least once.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-backend/.cursor/rules/testing.mdc')
    assert '**Rule**: Use `factory.manufacturePojo()` to generate random test data instead of manually setting values, unless specific values are required for the test case.' in text, "expected to find: " + '**Rule**: Use `factory.manufacturePojo()` to generate random test data instead of manually setting values, unless specific values are required for the test case.'[:80]

