"""
Task: lotti-feat-improve-collapsible-entries
Repo: matthiasn/lotti @ be8bbfc8f59d502773f05d99b835f122c22b18c1
PR:   2653

Verify: (1) scroll jumpiness fixed with conditional viewport-aware scroll,
        (2) header layout shows date when expanded,
        (3) collapse animation uses SizeTransition via _CollapsibleBody,
        (4) AnimatedSize in CollapsibleSection uses top alignment,
        (5) no duplicate date in expanded body.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/lotti"

DETAILS_WIDGET = "lib/features/journal/ui/widgets/entry_details_widget.dart"
HEADER = "lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart"
COLLAPSIBLE_SECTION = "lib/widgets/misc/collapsible_section.dart"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_repo_flutter_analyze():
    """Repo's Flutter analyze passes (pass_to_pass)."""
    r = subprocess.run(
        ["flutter", "analyze", "--no-pub"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flutter analyze failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_dart_format():
    """Repo's Dart code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["dart", "format", "--output=none", "--set-exit-if-changed", "lib", "test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Dart format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_syntax_check():
    """Modified Dart files parse without errors (balanced braces/parens)."""
    for path in [DETAILS_WIDGET, HEADER, COLLAPSIBLE_SECTION]:
        src = (Path(REPO) / path).read_text()
        assert src.count("{") == src.count("}"), \
            f"{path}: unbalanced braces"
        assert src.count("(") == src.count(")"), \
            f"{path}: unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------


def test_scroll_uses_viewport_check():
    """Scroll after expand checks viewport position via RenderAbstractViewport."""
    r = _run_py("""
import sys

src = open('lib/features/journal/ui/widgets/entry_details_widget.dart').read()

# 1. Must import rendering.dart for RenderAbstractViewport
assert 'package:flutter/rendering.dart' in src, \
    'Missing rendering.dart import for viewport-aware scroll'

# 2. Must define isExpanding variable to gate the scroll
assert 'final isExpanding' in src, \
    'Must define isExpanding to distinguish expand vs collapse'

# 3. Must use RenderAbstractViewport.maybeOf (nullable, not throwing)
assert 'RenderAbstractViewport.maybeOf' in src, \
    'Must use RenderAbstractViewport.maybeOf for safe viewport lookup'

# 4. Must use Scrollable.maybeOf (nullable)
assert 'Scrollable.maybeOf' in src, \
    'Must use Scrollable.maybeOf for safe scrollable lookup'

# 5. Verify the scroll logic is inside an if (isExpanding) block,
#    not unconditional like the old code
lines = src.split('\\n')
found_expanding_guard = False
found_conditional_ensure = False
brace_depth = 0
inside_expanding = False

for line in lines:
    if 'if (isExpanding)' in line:
        inside_expanding = True
        brace_depth = 0
        found_expanding_guard = True
        continue
    if inside_expanding:
        brace_depth += line.count('{') - line.count('}')
        if 'Scrollable.ensureVisible' in line:
            found_conditional_ensure = True
        if brace_depth <= 0 and '}' in line:
            inside_expanding = False

assert found_expanding_guard, \
    'Scroll must be guarded by if (isExpanding) block'
assert found_conditional_ensure, \
    'Scrollable.ensureVisible must be inside the isExpanding conditional'

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_header_shows_date_when_expanded():
    """Expanded collapsible header shows EntryDatetimeWidget."""
    r = _run_py("""
import sys

src = open('lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart').read()

# EntryDatetimeWidget must appear at least twice:
# once in collapsed block, once in expanded block
count = src.count('EntryDatetimeWidget')
assert count >= 2, \
    f'EntryDatetimeWidget should appear in both collapsed and expanded states (found {count})'

# Verify the expanded (!widget.isCollapsed) block contains EntryDatetimeWidget
# BEFORE the Spacer, so date is left-aligned and actions are right-aligned
lines = src.split('\\n')
expanded_sections = []
in_expanded = False
brace_depth = 0

for i, line in enumerate(lines):
    if 'if (!widget.isCollapsed)' in line and 'EntryDatetimeWidget' not in line:
        in_expanded = True
        brace_depth = 0
        section_lines = []
        continue
    if in_expanded:
        brace_depth += line.count('{') - line.count('}')
        section_lines.append(line)
        if brace_depth <= 0 and '}' in line and len(section_lines) > 1:
            expanded_sections.append(section_lines)
            in_expanded = False

# The first expanded section (with date) should have EntryDatetimeWidget
# The second expanded section (with actions) should have Spacer at start
assert len(expanded_sections) >= 1, \
    'Expected at least one expanded (!isCollapsed) block in _buildCollapsibleHeader'

# Find the section containing EntryDatetimeWidget
date_found = False
for section in expanded_sections:
    section_text = '\\n'.join(section)
    if 'EntryDatetimeWidget' in section_text:
        date_found = True
        break

assert date_found, \
    'Expanded header must include EntryDatetimeWidget for date display'

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_duplicate_date_in_body():
    """Date removed from expanded body content (no datePadding)."""
    r = _run_py("""
import sys

src = open('lib/features/journal/ui/widgets/entry_details_widget.dart').read()

# 1. The datePadding variable must be gone entirely
assert 'datePadding' not in src, \
    'datePadding variable must be removed (date now in header)'

# 2. The old import for EntryDatetimeWidget must be removed from this file
# (date widget is used in header file, not here anymore)
assert 'entry_datetime_widget.dart' not in src, \
    'entry_datetime_widget import removed from details widget (used in header now)'

# 3. The expanded content should NOT reference EntryDatetimeWidget
# (it's only in the header now)
lines = src.split('\\n')
in_expanded_content = False
for line in lines:
    if 'expandedContent' in line and 'Column' in line:
        in_expanded_content = True
    if in_expanded_content and 'EntryDatetimeWidget' in line:
        assert False, 'EntryDatetimeWidget should not appear in expandedContent'
    if in_expanded_content and line.strip().startswith('];'):
        in_expanded_content = False

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_collapsible_section_top_alignment():
    """AnimatedSize in CollapsibleSection uses top alignment."""
    r = _run_py("""
import sys

src = open('lib/widgets/misc/collapsible_section.dart').read()

# The AnimatedSize widget must have top alignment so content expands
# downward from the header, not squishing from center
assert 'AnimatedSize' in src, 'CollapsibleSection must still use AnimatedSize'
assert 'Alignment.topCenter' in src or 'Alignment.top' in src, \
    'AnimatedSize must use top alignment for downward expansion'

# Verify alignment is inside the AnimatedSize widget (not just floating)
lines = src.split('\\n')
in_animated_size = False
found_alignment_in_as = False
brace_depth = 0

for line in lines:
    if 'AnimatedSize(' in line:
        in_animated_size = True
        brace_depth = 0
        continue
    if in_animated_size:
        brace_depth += line.count('(') - line.count(')')
        if 'alignment' in line and ('Alignment.top' in line or 'Alignment.topCenter' in line):
            found_alignment_in_as = True
        if brace_depth < 0:
            in_animated_size = False

assert found_alignment_in_as, \
    'Alignment.topCenter must be a named parameter of AnimatedSize'

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_size_transition_for_collapse():
    """Collapse animation uses SizeTransition instead of AnimatedSize."""
    r = _run_py("""
import sys

src = open('lib/features/journal/ui/widgets/entry_details_widget.dart').read()

# 1. Must define _CollapsibleBody stateful widget that wraps the animation
assert 'class _CollapsibleBody extends StatefulWidget' in src, \
    'Must define _CollapsibleBody as StatefulWidget'
assert 'class _CollapsibleBodyState extends State<_CollapsibleBody>' in src, \
    'Must define _CollapsibleBodyState'

# 2. Must use SizeTransition (clips from edge) not bare AnimatedSize
assert 'SizeTransition(' in src, \
    'Must use SizeTransition for collapse/expand animation'
assert 'sizeFactor' in src, \
    'SizeTransition must use sizeFactor from AnimationController'
assert 'axisAlignment' in src, \
    'SizeTransition must set axisAlignment for top-aligned expansion'

# 3. Must use FadeTransition for opacity animation
assert 'FadeTransition(' in src, \
    'Must use FadeTransition for smooth opacity during collapse'
assert 'opacity' in src, \
    'FadeTransition must bind to opacity animation'

# 4. AnimationController must respond to isCollapsed changes
assert 'didUpdateWidget' in src, \
    '_CollapsibleBodyState must implement didUpdateWidget'
assert '_controller.forward()' in src, \
    'Must call forward() when expanding'
assert '_controller.reverse()' in src, \
    'Must call reverse() when collapsing'

# 5. The build method must use _CollapsibleBody, not bare AnimatedSize
# Find where the collapsible body is instantiated in the main build
assert '_CollapsibleBody(' in src, \
    'Must instantiate _CollapsibleBody widget in build tree'

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
