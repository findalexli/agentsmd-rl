"""Behavioral checks for finance-skills-add-dynamic-content-injection-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/finance-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Skills can embed shell commands that Claude Code executes at skill invocation time, injecting the output inline. Use this for runtime environment checks (tool installation status, auth state, live dat' in text, "expected to find: " + 'Skills can embed shell commands that Claude Code executes at skill invocation time, injecting the output inline. Use this for runtime environment checks (tool installation status, auth state, live dat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '!`(command -v mytool && mytool status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`' in text, "expected to find: " + '!`(command -v mytool && mytool status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Always include fallback output (e.g., `|| echo "UNAVAILABLE"`) so the skill degrades gracefully' in text, "expected to find: " + '- Always include fallback output (e.g., `|| echo "UNAVAILABLE"`) so the skill degrades gracefully'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/discord/SKILL.md')
    assert '!`(command -v discord && discord status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`' in text, "expected to find: " + '!`(command -v discord && discord status 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/discord/SKILL.md')
    assert 'If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:' in text, "expected to find: " + 'If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/discord/SKILL.md')
    assert 'If `AUTH_NEEDED`, guide the user:' in text, "expected to find: " + 'If `AUTH_NEEDED`, guide the user:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/options-payoff/SKILL.md')
    assert '!`python3 -c "import yfinance as yf; print(f\'SPX ≈ {yf.Ticker(\\"^GSPC\\").fast_info[\\"lastPrice\\"]:.0f}\')" 2>/dev/null || echo "SPX price unavailable — check market data"`' in text, "expected to find: " + '!`python3 -c "import yfinance as yf; print(f\'SPX ≈ {yf.Ticker(\\"^GSPC\\").fast_info[\\"lastPrice\\"]:.0f}\')" 2>/dev/null || echo "SPX price unavailable — check market data"`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/options-payoff/SKILL.md')
    assert '**Critical for screenshots**: The spot price is the CURRENT price of the underlying index/stock, NOT the strikes. Never default spot to a strike price value.' in text, "expected to find: " + '**Critical for screenshots**: The spot price is the CURRENT price of the underlying index/stock, NOT the strikes. Never default spot to a strike price value.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/options-payoff/SKILL.md')
    assert '**Current SPX reference price:**' in text, "expected to find: " + '**Current SPX reference price:**'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert '!`python3 -c "import yfinance, pandas, numpy; print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')" 2>/dev/null || echo "DEPS_MISSING"`' in text, "expected to find: " + '!`python3 -c "import yfinance, pandas, numpy; print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')" 2>/dev/null || echo "DEPS_MISSING"`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert 'If all dependencies are already installed, skip the install step and proceed directly.' in text, "expected to find: " + 'If all dependencies are already installed, skip the install step and proceed directly.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stock-correlation/SKILL.md')
    assert 'If `DEPS_MISSING`, install required packages before running any code:' in text, "expected to find: " + 'If `DEPS_MISSING`, install required packages before running any code:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/telegram/SKILL.md')
    assert '!`(tdl chat ls --limit 1 2>&1 >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null`' in text, "expected to find: " + '!`(tdl chat ls --limit 1 2>&1 >/dev/null && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/telegram/SKILL.md')
    assert '!`(command -v tdl && tdl version 2>&1 | head -3 || echo "TDL_NOT_INSTALLED") 2>/dev/null`' in text, "expected to find: " + '!`(command -v tdl && tdl version 2>&1 | head -3 || echo "TDL_NOT_INSTALLED") 2>/dev/null`'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/telegram/SKILL.md')
    assert 'If the status above shows a version number, tdl is installed — skip to Step 2.' in text, "expected to find: " + 'If the status above shows a version number, tdl is installed — skip to Step 2.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/twitter/SKILL.md')
    assert '!`(command -v twitter && twitter status --yaml 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`' in text, "expected to find: " + '!`(command -v twitter && twitter status --yaml 2>&1 | head -5 && echo "AUTH_OK" || echo "AUTH_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/twitter/SKILL.md')
    assert 'If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:' in text, "expected to find: " + 'If the status above shows `AUTH_OK`, skip to Step 2. If `NOT_INSTALLED`, install first:'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/twitter/SKILL.md')
    assert 'If `AUTH_NEEDED`, guide the user:' in text, "expected to find: " + 'If `AUTH_NEEDED`, guide the user:'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/yfinance-data/SKILL.md')
    assert '!`python3 -c "import yfinance; print(\'yfinance \' + yfinance.__version__ + \' installed\')" 2>/dev/null || echo "YFINANCE_NOT_INSTALLED"`' in text, "expected to find: " + '!`python3 -c "import yfinance; print(\'yfinance \' + yfinance.__version__ + \' installed\')" 2>/dev/null || echo "YFINANCE_NOT_INSTALLED"`'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/yfinance-data/SKILL.md')
    assert 'If yfinance is already installed, skip the install step and proceed directly.' in text, "expected to find: " + 'If yfinance is already installed, skip the install step and proceed directly.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/yfinance-data/SKILL.md')
    assert 'If `YFINANCE_NOT_INSTALLED`, install it before running any code:' in text, "expected to find: " + 'If `YFINANCE_NOT_INSTALLED`, install it before running any code:'[:80]

