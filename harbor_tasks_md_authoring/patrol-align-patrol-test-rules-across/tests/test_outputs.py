"""Behavioral checks for patrol-align-patrol-test-rules-across (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/patrol")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests-architecture/SKILL.md')
    assert "1. Read the key files directly (modules aggregator, test wrapper, main keys.dart, and the specific app feature files for the scenario). These are known paths — don't search for them, open them directl" in text, "expected to find: " + "1. Read the key files directly (modules aggregator, test wrapper, main keys.dart, and the specific app feature files for the scenario). These are known paths — don't search for them, open them directl"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests-architecture/SKILL.md')
    assert '8. After full test passes, reorganize new code into existing/new modules. This is mandatory — the test file must only call module methods, not use Patrol APIs directly' in text, "expected to find: " + '8. After full test passes, reorganize new code into existing/new modules. This is mandatory — the test file must only call module methods, not use Patrol APIs directly'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests-architecture/SKILL.md')
    assert "7. Run the test frequently during development — don't wait until the full test is written. Run after completing each logical group of steps to catch failures early" in text, "expected to find: " + "7. Run the test frequently during development — don't wait until the full test is written. Run after completing each logical group of steps to catch failures early"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests/SKILL.md')
    assert "6. Run the test frequently during development — don't wait until the full test is written. Run after completing each logical group of steps to catch failures early" in text, "expected to find: " + "6. Run the test frequently during development — don't wait until the full test is written. Run after completing each logical group of steps to catch failures early"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests/SKILL.md')
    assert '2. Also think if one of existing functions can be adjusted to match its existing usage and new test' in text, "expected to find: " + '2. Also think if one of existing functions can be adjusted to match its existing usage and new test'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/patrol-tests/SKILL.md')
    assert '4. Start writing test: reuse existing functions + put new test steps in new test file' in text, "expected to find: " + '4. Start writing test: reuse existing functions + put new test steps in new test file'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-test-keys.mdc')
    assert '- For widgets located in separate package (e.g. widgetbook) follow this pattern: in `widgetbook` directory create `keys.dart` file with `WidgetKeys` class. Those keys are assigned with `widgetKeys.til' in text, "expected to find: " + '- For widgets located in separate package (e.g. widgetbook) follow this pattern: in `widgetbook` directory create `keys.dart` file with `WidgetKeys` class. Those keys are assigned with `widgetKeys.til'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-test-keys.mdc')
    assert '- Group related keys in a class named after the screen (e.g. `HomeKeys`). Use a private subclass of `ValueKey<String>` to prefix all key values with the page or widget name' in text, "expected to find: " + '- Group related keys in a class named after the screen (e.g. `HomeKeys`). Use a private subclass of `ValueKey<String>` to prefix all key values with the page or widget name'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-test-keys.mdc')
    assert '- For common widgets store them in WidgetKeys class. File containing this class should be placed in the directory that the common widget is defined' in text, "expected to find: " + '- For common widgets store them in WidgetKeys class. File containing this class should be placed in the directory that the common widget is defined'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-tests.mdc')
    assert '- System is a class for native interactions, specifically for actions that we need to perform by using $.platform that are not part of our app, eg. enabling airplane mode to test offline mode. Do not ' in text, "expected to find: " + '- System is a class for native interactions, specifically for actions that we need to perform by using $.platform that are not part of our app, eg. enabling airplane mode to test offline mode. Do not '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-tests.mdc')
    assert '- ApiClients - a class aggregating api clients for api communication. There will be separate clients for different apis we need to communicate with - eg. email server for testing, our test backend, or' in text, "expected to find: " + '- ApiClients - a class aggregating api clients for api communication. There will be separate clients for different apis we need to communicate with - eg. email server for testing, our test backend, or'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test-with-architecture/patrol-tests.mdc')
    assert "1. Read the key files directly (modules aggregator, test wrapper, main keys.dart, and the specific app feature files for the scenario). These are known paths — don't search for them, open them directl" in text, "expected to find: " + "1. Read the key files directly (modules aggregator, test wrapper, main keys.dart, and the specific app feature files for the scenario). These are known paths — don't search for them, open them directl"[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test/patrol-tests.mdc')
    assert "- Don't use `$.pump`, `waitUntilVisible` or `waitUntilExists` and other wait methods after or before tap, scrollTo and enterText. Patrol handles it automatically. Do this only at the end of the test" in text, "expected to find: " + "- Don't use `$.pump`, `waitUntilVisible` or `waitUntilExists` and other wait methods after or before tap, scrollTo and enterText. Patrol handles it automatically. Do this only at the end of the test"[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test/patrol-tests.mdc')
    assert '- Use `patrol-native-tree({})` to fetch the current native UI tree hierarchy for writing native interactions and interactions with apps other than the app under test.' in text, "expected to find: " + '- Use `patrol-native-tree({})` to fetch the current native UI tree hierarchy for writing native interactions and interactions with apps other than the app under test.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/patrol-test/patrol-tests.mdc')
    assert "- Any file that directly uses Patrol APIs (`$()`, `.scrollTo()`, `.tap()`, `.enterText()`, `.waitUntilVisible()`, etc.) should `import 'package:patrol/patrol.dart';`" in text, "expected to find: " + "- Any file that directly uses Patrol APIs (`$()`, `.scrollTo()`, `.tap()`, `.enterText()`, `.waitUntilVisible()`, etc.) should `import 'package:patrol/patrol.dart';`"[:80]

