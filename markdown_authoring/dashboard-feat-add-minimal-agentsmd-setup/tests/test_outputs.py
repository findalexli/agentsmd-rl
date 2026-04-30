"""Behavioral checks for dashboard-feat-add-minimal-agentsmd-setup (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dashboard")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Gardener Dashboard - Management UI for Gardener Kubernetes clusters. Yarn-managed monorepo with Vue.js frontend, Node.js backend, and shared packages.' in text, "expected to find: " + 'Gardener Dashboard - Management UI for Gardener Kubernetes clusters. Yarn-managed monorepo with Vue.js frontend, Node.js backend, and shared packages.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '# Install dependencies' in text, "expected to find: " + '# Install dependencies'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## Essential Commands' in text, "expected to find: " + '## Essential Commands'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/AGENTS.md')
    assert 'Backend API service for the Gardener Dashboard. Express.js with ESM modules, part of yarn monorepo workspace.' in text, "expected to find: " + 'Backend API service for the Gardener Dashboard. Express.js with ESM modules, part of yarn monorepo workspace.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/AGENTS.md')
    assert 'yarn build-test-target  # Required: Transpile ESM to CommonJS for tests' in text, "expected to find: " + 'yarn build-test-target  # Required: Transpile ESM to CommonJS for tests'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/AGENTS.md')
    assert 'yarn test-coverage     # Run tests with coverage report' in text, "expected to find: " + 'yarn test-coverage     # Run tests with coverage report'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert 'Frontend client for the Gardener Dashboard. Vue 3 SPA with Vuetify, part of yarn monorepo workspace.' in text, "expected to find: " + 'Frontend client for the Gardener Dashboard. Vue 3 SPA with Vuetify, part of yarn monorepo workspace.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert 'yarn test <PATH TO SPEC FILE>  # Run specific test' in text, "expected to find: " + 'yarn test <PATH TO SPEC FILE>  # Run specific test'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert '# Start development server (HTTPS on port 8443)' in text, "expected to find: " + '# Start development server (HTTPS on port 8443)'[:80]

