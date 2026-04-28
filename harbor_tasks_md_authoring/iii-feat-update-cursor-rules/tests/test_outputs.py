"""Behavioral checks for iii-feat-update-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/iii")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc')
    assert '* for each HTTP Status Code, you need to define a schema that defines the response body' in text, "expected to find: " + '* for each HTTP Status Code, you need to define a schema that defines the response body'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc')
    assert 'export type ZodInput = ZodObject<any> | ZodArray<any>' in text, "expected to find: " + 'export type ZodInput = ZodObject<any> | ZodArray<any>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc')
    assert 'export type StepSchemaInput = ZodInput | JsonSchema' in text, "expected to find: " + 'export type StepSchemaInput = ZodInput | JsonSchema'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc')
    assert '* Optional: Virtually subscribed topics for documentation/lineage purposes.' in text, "expected to find: " + '* Optional: Virtually subscribed topics for documentation/lineage purposes.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc')
    assert 'Defining an Event Step is done by two elements. Configuration and Handler.' in text, "expected to find: " + 'Defining an Event Step is done by two elements. Configuration and Handler.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc')
    assert '* Optional: Infrastructure configuration for handler and queue settings.' in text, "expected to find: " + '* Optional: Infrastructure configuration for handler and queue settings.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc')
    assert 'Adapters allow you to customize the underlying infrastructure for state management, event handling, cron jobs, and streams. This is useful for horizontal scaling or using custom storage backends.' in text, "expected to find: " + 'Adapters allow you to customize the underlying infrastructure for state management, event handling, cron jobs, and streams. This is useful for horizontal scaling or using custom storage backends.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc')
    assert 'The `motia.config.ts` file is the central configuration file for your Motia application. It allows you to customize plugins, adapters, stream authentication, and Express app settings.' in text, "expected to find: " + 'The `motia.config.ts` file is the central configuration file for your Motia application. It allows you to customize plugins, adapters, stream authentication, and Express app settings.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc')
    assert 'authenticate: (request: StreamAuthRequest) => Promise<z.infer<TSchema> | null> | (z.infer<TSchema> | null)' in text, "expected to find: " + 'authenticate: (request: StreamAuthRequest) => Promise<z.infer<TSchema> | null> | (z.infer<TSchema> | null)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc')
    assert "baseConfig: { storageType: 'default' } | { storageType: 'custom'; factory: () => MotiaStream<any> }" in text, "expected to find: " + "baseConfig: { storageType: 'default' } | { storageType: 'custom'; factory: () => MotiaStream<any> }"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc')
    assert 'canAccess?: (subscription: StreamSubscription, authContext: any) => boolean | Promise<boolean>' in text, "expected to find: " + 'canAccess?: (subscription: StreamSubscription, authContext: any) => boolean | Promise<boolean>'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc')
    assert "* Use 'default' for built-in storage or 'custom' with a factory function." in text, "expected to find: " + "* Use 'default' for built-in storage or 'custom' with a factory function."[:80]

