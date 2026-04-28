"""Behavioral checks for sentry-javascript-choreagents-migrate-repowide-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-javascript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-ai-integration/SKILL.md')
    assert 'description: Add a new AI provider integration to the Sentry JavaScript SDK. Use when contributing a new AI instrumentation (OpenAI, Anthropic, Vercel AI, LangChain, etc.) or modifying an existing one' in text, "expected to find: " + 'description: Add a new AI provider integration to the Sentry JavaScript SDK. Use when contributing a new AI instrumentation (OpenAI, Anthropic, Vercel AI, LangChain, etc.) or modifying an existing one'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-ai-integration/SKILL.md')
    assert '- **Streaming:** `startSpanManual()`, accumulate state via async generator or event listeners, set `GEN_AI_RESPONSE_STREAMING_ATTRIBUTE: true`, call `span.end()` in finally block' in text, "expected to find: " + '- **Streaming:** `startSpanManual()`, accumulate state via async generator or event listeners, set `GEN_AI_RESPONSE_STREAMING_ATTRIBUTE: true`, call `span.end()` in finally block'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-ai-integration/SKILL.md')
    assert '2. **Node.js:** Add `callWhenPatched()` optimization in `packages/node/src/integrations/tracing/{provider}/index.ts` — defers registration until package is imported' in text, "expected to find: " + '2. **Node.js:** Add `callWhenPatched()` optimization in `packages/node/src/integrations/tracing/{provider}/index.ts` — defers registration until package is imported'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/release/SKILL.md')
    assert '5. Update `CHANGELOG.md` — add the new version entry with the changelog output. See the "Updating the Changelog" section in `docs/publishing-a-release.md` for formatting details. Do not remove existin' in text, "expected to find: " + '5. Update `CHANGELOG.md` — add the new version entry with the changelog output. See the "Updating the Changelog" section in `docs/publishing-a-release.md` for formatting details. Do not remove existin'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/release/SKILL.md')
    assert 'description: Publish a new Sentry JavaScript SDK release. Use when preparing a release, updating the changelog, or creating a release branch.' in text, "expected to find: " + 'description: Publish a new Sentry JavaScript SDK release. Use when preparing a release, updating the changelog, or creating a release branch.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/release/SKILL.md')
    assert '3. Decide on a version per [semver](https://semver.org). Check the top of `CHANGELOG.md` for the current version.' in text, "expected to find: " + '3. Decide on a version per [semver](https://semver.org). Check the top of `CHANGELOG.md` for the current version.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-dep/SKILL.md')
    assert 'Do **not** upgrade the major version of a dependency in `dev-packages/e2e-tests/test-applications/*` if the test directory name pins a version (e.g., `nestjs-8` must stay on NestJS 8).' in text, "expected to find: " + 'Do **not** upgrade the major version of a dependency in `dev-packages/e2e-tests/test-applications/*` if the test directory name pins a version (e.g., `nestjs-8` must stay on NestJS 8).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-dep/SKILL.md')
    assert 'description: Upgrade a dependency in the Sentry JavaScript SDK. Use when upgrading packages, bumping versions, or fixing security vulnerabilities via dependency updates.' in text, "expected to find: " + 'description: Upgrade a dependency in the Sentry JavaScript SDK. Use when upgrading packages, bumping versions, or fixing security vulnerabilities via dependency updates.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-dep/SKILL.md')
    assert 'If the dependency is not defined in any `package.json`, run the upgrade from the root workspace (the `yarn.lock` lives there).' in text, "expected to find: " + 'If the dependency is not defined in any `package.json`, run the upgrade from the root workspace (the `yarn.lock` lives there).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-otel/SKILL.md')
    assert '2. **All `@opentelemetry/instrumentation-*` packages.** Check each changelog: `https://github.com/open-telemetry/opentelemetry-js-contrib/blob/main/packages/instrumentation-{name}/CHANGELOG.md`' in text, "expected to find: " + '2. **All `@opentelemetry/instrumentation-*` packages.** Check each changelog: `https://github.com/open-telemetry/opentelemetry-js-contrib/blob/main/packages/instrumentation-{name}/CHANGELOG.md`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-otel/SKILL.md')
    assert 'description: Upgrade OpenTelemetry instrumentations across the Sentry JavaScript SDK. Use when bumping OTel instrumentation packages to their latest versions.' in text, "expected to find: " + 'description: Upgrade OpenTelemetry instrumentations across the Sentry JavaScript SDK. Use when bumping OTel instrumentation packages to their latest versions.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/upgrade-otel/SKILL.md')
    assert '1. **`@opentelemetry/instrumentation`** to latest. Check changelog: `https://github.com/open-telemetry/opentelemetry-js/blob/main/experimental/CHANGELOG.md`' in text, "expected to find: " + '1. **`@opentelemetry/instrumentation`** to latest. Check changelog: `https://github.com/open-telemetry/opentelemetry-js/blob/main/experimental/CHANGELOG.md`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/adding-a-new-ai-integration.mdc')
    assert '.cursor/rules/adding-a-new-ai-integration.mdc' in text, "expected to find: " + '.cursor/rules/adding-a-new-ai-integration.mdc'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/fetch-docs/attributes.mdc')
    assert '.cursor/rules/fetch-docs/attributes.mdc' in text, "expected to find: " + '.cursor/rules/fetch-docs/attributes.mdc'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/fetch-docs/scopes.mdc')
    assert '.cursor/rules/fetch-docs/scopes.mdc' in text, "expected to find: " + '.cursor/rules/fetch-docs/scopes.mdc'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/publishing_release.mdc')
    assert '.cursor/rules/publishing_release.mdc' in text, "expected to find: " + '.cursor/rules/publishing_release.mdc'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sdk_dependency_upgrades.mdc')
    assert '.cursor/rules/sdk_dependency_upgrades.mdc' in text, "expected to find: " + '.cursor/rules/sdk_dependency_upgrades.mdc'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/upgrade_opentelemetry_instrumentations.mdc')
    assert '.cursor/rules/upgrade_opentelemetry_instrumentations.mdc' in text, "expected to find: " + '.cursor/rules/upgrade_opentelemetry_instrumentations.mdc'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Scopes (global, isolation, current)](https://develop.sentry.dev/sdk/telemetry/scopes.md)' in text, "expected to find: " + '- [Scopes (global, isolation, current)](https://develop.sentry.dev/sdk/telemetry/scopes.md)'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use `/add-ai-integration` skill. See `.claude/skills/add-ai-integration/SKILL.md`' in text, "expected to find: " + 'Use `/add-ai-integration` skill. See `.claude/skills/add-ai-integration/SKILL.md`'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Span Attributes](https://develop.sentry.dev/sdk/telemetry/attributes.md)' in text, "expected to find: " + '- [Span Attributes](https://develop.sentry.dev/sdk/telemetry/attributes.md)'[:80]

