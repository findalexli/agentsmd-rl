"""Behavioral checks for fledge-cursor-rules-for-c-plugins (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fledge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/core.mdc')
    assert '- All log entries should be written to be human readable and standalone from the code that raises them. The reader of the log message should not need to have access to the source code in order to unde' in text, "expected to find: " + '- All log entries should be written to be human readable and standalone from the code that raises them. The reader of the log message should not need to have access to the source code in order to unde'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/core.mdc')
    assert '- Log messages should not contain source file names, line numbers or function names as these have little to no meaning to the intended audience for the majority of log messages These also take up valu' in text, "expected to find: " + '- Log messages should not contain source file names, line numbers or function names as these have little to no meaning to the intended audience for the majority of log messages These also take up valu'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/core.mdc')
    assert 'Fledge support 5 levels of logging, which can be considered in descending order of severity; fatal, error, warning, info and debug. Each of these has a defined use and a targeted audience. By default ' in text, "expected to find: " + 'Fledge support 5 levels of logging, which can be considered in descending order of severity; fatal, error, warning, info and debug. Each of these has a defined use and a targeted audience. By default '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/filter.mdc')
    assert '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist' in text, "expected to find: " + '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/filter.mdc')
    assert '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of' in text, "expected to find: " + '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/filter.mdc')
    assert '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio' in text, "expected to find: " + '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/north.mdc')
    assert '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist' in text, "expected to find: " + '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/north.mdc')
    assert '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of' in text, "expected to find: " + '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/north.mdc')
    assert '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio' in text, "expected to find: " + '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/south.mdc')
    assert '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist' in text, "expected to find: " + '|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/south.mdc')
    assert '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of' in text, "expected to find: " + '|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/C/plugins/south.mdc')
    assert '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio' in text, "expected to find: " + '|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuratio'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert '│\xa0\xa0 ├── core.mdc          # Core C++ Standards + + platform requirements' in text, "expected to find: " + '│\xa0\xa0 ├── core.mdc          # Core C++ Standards + + platform requirements'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert '| `@C/plugins/filter` | C++ Filter Plugin| `*.h`, `*.cpp` |' in text, "expected to find: " + '| `@C/plugins/filter` | C++ Filter Plugin| `*.h`, `*.cpp` |'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert '| `@C/plugins/south` | C++ South Plugin| `*.h`, `*.cpp` |' in text, "expected to find: " + '| `@C/plugins/south` | C++ South Plugin| `*.h`, `*.cpp` |'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification.mdc')
    assert '# Fledge Notification Service - Feature Development Rules (MDC Format)' in text, "expected to find: " + '# Fledge Notification Service - Feature Development Rules (MDC Format)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification.mdc')
    assert '- "throw NotificationException(\\"Invalid recipient: \\" + recipient)"' in text, "expected to find: " + '- "throw NotificationException(\\"Invalid recipient: \\" + recipient)"'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification.mdc')
    assert 'patterns: ["try_catch", "custom_exceptions", "error_logging"]' in text, "expected to find: " + 'patterns: ["try_catch", "custom_exceptions", "error_logging"]'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification_code_review.mdc')
    assert 'This MDC file serves as a comprehensive guide for AI-assisted development and code review in the Fledge Notification Service project. It provides structured evaluation criteria, git diff analysis tech' in text, "expected to find: " + 'This MDC file serves as a comprehensive guide for AI-assisted development and code review in the Fledge Notification Service project. It provides structured evaluation criteria, git diff analysis tech'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification_code_review.mdc')
    assert 'This MDC file contains comprehensive rules, guidelines, and documentation for AI-assisted development and code review in the Fledge Notification Service project. It combines code review evaluation cri' in text, "expected to find: " + 'This MDC file contains comprehensive rules, guidelines, and documentation for AI-assisted development and code review in the Fledge Notification Service project. It combines code review evaluation cri'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/services/notification_code_review.mdc')
    assert 'For each truly changed file and each diffed hunk, evaluate against the 12 evaluation criteria listed above.' in text, "expected to find: " + 'For each truly changed file and each diffed hunk, evaluate against the 12 evaluation criteria listed above.'[:80]

