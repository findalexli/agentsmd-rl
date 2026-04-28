"""Behavioral checks for sentry-ref-reorganize-agentsmd-into-focused (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Comments should not repeat what the code is saying. Instead, reserve comments for explaining **why** something is being done, or to provide context that is not obvious from the code itself.' in text, "expected to find: " + 'Comments should not repeat what the code is saying. Instead, reserve comments for explaining **why** something is being done, or to provide context that is not obvious from the code itself.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Exception**: Tests ensuring Snuba compatibility MUST be placed in `tests/snuba/`. The tests in this folder will also run in Snuba's CI." in text, "expected to find: " + "**Exception**: Tests ensuring Snuba compatibility MUST be placed in `tests/snuba/`. The tests in this folder will also run in Snuba's CI."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'NEVER directly call `Model.objects.create` - this violates our testing standards and bypasses shared test setup logic.' in text, "expected to find: " + 'NEVER directly call `Model.objects.create` - this violates our testing standards and bypasses shared test setup logic.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert '**Important**: Never suggest adding a default value to `options.get()` calls. All options are registered via `register()` in `defaults.py` which requires a default value. The options system will alway' in text, "expected to find: " + '**Important**: Never suggest adding a default value to `options.get()` calls. All options are registered via `register()` in `defaults.py` which requires a default value. The options system will alway'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert 'Sentry is a developer-first error tracking and performance monitoring platform. This repository contains the main Sentry application, which is a large-scale Django application with a React frontend.' in text, "expected to find: " + 'Sentry is a developer-first error tracking and performance monitoring platform. This repository contains the main Sentry application, which is a large-scale Django application with a React frontend.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert 'Always import a type from the module `collections.abc` rather than the `typing` module if it is available (e.g. `from collections.abc import Sequence` rather than `from typing import Sequence`).' in text, "expected to find: " + 'Always import a type from the module `collections.abc` rather than the `typing` module if it is available (e.g. `from collections.abc import Sequence` rather than `from typing import Sequence`).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/CLAUDE.md')
    assert 'src/CLAUDE.md' in text, "expected to find: " + 'src/CLAUDE.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars' in text, "expected to find: " + 'Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use <Text> from `@sentry/scraps/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.' in text, "expected to find: " + 'Use <Text> from `@sentry/scraps/text` for text styling instead of styled components that handle typography features like color, overflow, font-size, font-weight.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Place all icons in the static/app/icons folder. Never inline SVGs or add them to any other folder. Optimize SVGs using svgo or svgomg' in text, "expected to find: " + 'Place all icons in the static/app/icons folder. Never inline SVGs or add them to any other folder. Optimize SVGs using svgo or svgomg'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('static/CLAUDE.md')
    assert 'static/CLAUDE.md' in text, "expected to find: " + 'static/CLAUDE.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert 'When fixing errors or adding functionality, you MUST add test cases to existing test files rather than creating new test files. Follow this pattern to locate the correct test file:' in text, "expected to find: " + 'When fixing errors or adding functionality, you MUST add test cases to existing test files rather than creating new test files. Follow this pattern to locate the correct test file:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert 'In Sentry Python tests, always use `pytest` instead of `unittest`. This promotes consistency, reduces boilerplate, and leverages shared test setup logic defined in the factories.' in text, "expected to find: " + 'In Sentry Python tests, always use `pytest` instead of `unittest`. This promotes consistency, reduces boilerplate, and leverages shared test setup logic defined in the factories.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert "**Exception**: Tests ensuring Snuba compatibility MUST be placed in `tests/snuba/`. The tests in this folder will also run in Snuba's CI." in text, "expected to find: " + "**Exception**: Tests ensuring Snuba compatibility MUST be placed in `tests/snuba/`. The tests in this folder will also run in Snuba's CI."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/CLAUDE.md')
    assert 'tests/CLAUDE.md' in text, "expected to find: " + 'tests/CLAUDE.md'[:80]

