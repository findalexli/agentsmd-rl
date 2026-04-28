"""Behavioral checks for binance-skills-hub-remove-deprecated-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/binance-skills-hub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/algo/CHANGELOG.md')
    assert 'skills/binance/algo/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/algo/CHANGELOG.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/algo/LICENSE.md')
    assert 'skills/binance/algo/LICENSE.md' in text, "expected to find: " + 'skills/binance/algo/LICENSE.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/algo/SKILL.md')
    assert 'skills/binance/algo/SKILL.md' in text, "expected to find: " + 'skills/binance/algo/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/algo/references/authentication.md')
    assert 'skills/binance/algo/references/authentication.md' in text, "expected to find: " + 'skills/binance/algo/references/authentication.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/alpha/CHANGELOG.md')
    assert 'skills/binance/alpha/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/alpha/CHANGELOG.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/alpha/LICENSE.md')
    assert 'skills/binance/alpha/LICENSE.md' in text, "expected to find: " + 'skills/binance/alpha/LICENSE.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/alpha/SKILL.md')
    assert 'skills/binance/alpha/SKILL.md' in text, "expected to find: " + 'skills/binance/alpha/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/alpha/references/authentication.md')
    assert 'skills/binance/alpha/references/authentication.md' in text, "expected to find: " + 'skills/binance/alpha/references/authentication.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/assets/CHANGELOG.md')
    assert 'skills/binance/assets/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/assets/CHANGELOG.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/assets/LICENSE.md')
    assert 'skills/binance/assets/LICENSE.md' in text, "expected to find: " + 'skills/binance/assets/LICENSE.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/assets/SKILL.md')
    assert 'skills/binance/assets/SKILL.md' in text, "expected to find: " + 'skills/binance/assets/SKILL.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/assets/references/authentication.md')
    assert 'skills/binance/assets/references/authentication.md' in text, "expected to find: " + 'skills/binance/assets/references/authentication.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/convert/CHANGELOG.md')
    assert 'skills/binance/convert/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/convert/CHANGELOG.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/convert/LICENSE.md')
    assert 'skills/binance/convert/LICENSE.md' in text, "expected to find: " + 'skills/binance/convert/LICENSE.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/convert/SKILL.md')
    assert 'skills/binance/convert/SKILL.md' in text, "expected to find: " + 'skills/binance/convert/SKILL.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/convert/references/authentication.md')
    assert 'skills/binance/convert/references/authentication.md' in text, "expected to find: " + 'skills/binance/convert/references/authentication.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-coin-futures/CHANGELOG.md')
    assert 'skills/binance/derivatives-trading-coin-futures/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-coin-futures/CHANGELOG.md'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-coin-futures/LICENSE.md')
    assert 'skills/binance/derivatives-trading-coin-futures/LICENSE.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-coin-futures/LICENSE.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-coin-futures/SKILL.md')
    assert 'skills/binance/derivatives-trading-coin-futures/SKILL.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-coin-futures/SKILL.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-coin-futures/references/authentication.md')
    assert 'skills/binance/derivatives-trading-coin-futures/references/authentication.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-coin-futures/references/authentication.md'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-options/CHANGELOG.md')
    assert 'skills/binance/derivatives-trading-options/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-options/CHANGELOG.md'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-options/LICENSE.md')
    assert 'skills/binance/derivatives-trading-options/LICENSE.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-options/LICENSE.md'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-options/SKILL.md')
    assert 'skills/binance/derivatives-trading-options/SKILL.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-options/SKILL.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-options/references/authentication.md')
    assert 'skills/binance/derivatives-trading-options/references/authentication.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-options/references/authentication.md'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin-pro/CHANGELOG.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin-pro/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin-pro/CHANGELOG.md'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin-pro/LICENSE.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin-pro/LICENSE.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin-pro/LICENSE.md'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin-pro/SKILL.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin-pro/SKILL.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin-pro/SKILL.md'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin-pro/references/authentication.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin-pro/references/authentication.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin-pro/references/authentication.md'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin/CHANGELOG.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin/CHANGELOG.md'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin/LICENSE.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin/LICENSE.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin/LICENSE.md'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin/SKILL.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin/SKILL.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin/SKILL.md'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-portfolio-margin/references/authentication.md')
    assert 'skills/binance/derivatives-trading-portfolio-margin/references/authentication.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-portfolio-margin/references/authentication.md'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-usds-futures/CHANGELOG.md')
    assert 'skills/binance/derivatives-trading-usds-futures/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-usds-futures/CHANGELOG.md'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-usds-futures/LICENSE.md')
    assert 'skills/binance/derivatives-trading-usds-futures/LICENSE.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-usds-futures/LICENSE.md'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-usds-futures/SKILL.md')
    assert 'skills/binance/derivatives-trading-usds-futures/SKILL.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-usds-futures/SKILL.md'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/derivatives-trading-usds-futures/references/authentication.md')
    assert 'skills/binance/derivatives-trading-usds-futures/references/authentication.md' in text, "expected to find: " + 'skills/binance/derivatives-trading-usds-futures/references/authentication.md'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/margin-trading/CHANGELOG.md')
    assert 'skills/binance/margin-trading/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/margin-trading/CHANGELOG.md'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/margin-trading/LICENSE.md')
    assert 'skills/binance/margin-trading/LICENSE.md' in text, "expected to find: " + 'skills/binance/margin-trading/LICENSE.md'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/margin-trading/SKILL.md')
    assert 'skills/binance/margin-trading/SKILL.md' in text, "expected to find: " + 'skills/binance/margin-trading/SKILL.md'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/margin-trading/references/authentication.md')
    assert 'skills/binance/margin-trading/references/authentication.md' in text, "expected to find: " + 'skills/binance/margin-trading/references/authentication.md'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/simple-earn/CHANGELOG.md')
    assert 'skills/binance/simple-earn/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/simple-earn/CHANGELOG.md'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/simple-earn/LICENSE.md')
    assert 'skills/binance/simple-earn/LICENSE.md' in text, "expected to find: " + 'skills/binance/simple-earn/LICENSE.md'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/simple-earn/SKILL.md')
    assert 'skills/binance/simple-earn/SKILL.md' in text, "expected to find: " + 'skills/binance/simple-earn/SKILL.md'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/simple-earn/references/authentication.md')
    assert 'skills/binance/simple-earn/references/authentication.md' in text, "expected to find: " + 'skills/binance/simple-earn/references/authentication.md'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/spot/CHANGELOG.md')
    assert 'skills/binance/spot/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/spot/CHANGELOG.md'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/spot/LICENSE.md')
    assert 'skills/binance/spot/LICENSE.md' in text, "expected to find: " + 'skills/binance/spot/LICENSE.md'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/spot/SKILL.md')
    assert 'skills/binance/spot/SKILL.md' in text, "expected to find: " + 'skills/binance/spot/SKILL.md'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/spot/references/authentication.md')
    assert 'skills/binance/spot/references/authentication.md' in text, "expected to find: " + 'skills/binance/spot/references/authentication.md'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/sub-account/CHANGELOG.md')
    assert 'skills/binance/sub-account/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/sub-account/CHANGELOG.md'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/sub-account/LICENSE.md')
    assert 'skills/binance/sub-account/LICENSE.md' in text, "expected to find: " + 'skills/binance/sub-account/LICENSE.md'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/sub-account/SKILL.md')
    assert 'skills/binance/sub-account/SKILL.md' in text, "expected to find: " + 'skills/binance/sub-account/SKILL.md'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/sub-account/references/authentication.md')
    assert 'skills/binance/sub-account/references/authentication.md' in text, "expected to find: " + 'skills/binance/sub-account/references/authentication.md'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/vip-loan/CHANGELOG.md')
    assert 'skills/binance/vip-loan/CHANGELOG.md' in text, "expected to find: " + 'skills/binance/vip-loan/CHANGELOG.md'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/vip-loan/LICENSE.md')
    assert 'skills/binance/vip-loan/LICENSE.md' in text, "expected to find: " + 'skills/binance/vip-loan/LICENSE.md'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/vip-loan/SKILL.md')
    assert 'skills/binance/vip-loan/SKILL.md' in text, "expected to find: " + 'skills/binance/vip-loan/SKILL.md'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/binance/vip-loan/references/authentication.md')
    assert 'skills/binance/vip-loan/references/authentication.md' in text, "expected to find: " + 'skills/binance/vip-loan/references/authentication.md'[:80]

