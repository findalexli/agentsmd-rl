"""Behavioral checks for pay-chore-agentsmd-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pay")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/container-dev/SKILL.md')
    assert 'description: "Use when local PHP environment is unavailable. Fallback container-based development environment for yansongda/pay project."' in text, "expected to find: " + 'description: "Use when local PHP environment is unavailable. Fallback container-based development environment for yansongda/pay project."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/container-dev/SKILL.md')
    assert 'sh -c "echo \'nameserver 8.8.8.8\' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 php-cs-fixer fix ./src"' in text, "expected to find: " + 'sh -c "echo \'nameserver 8.8.8.8\' > /etc/resolv.conf && COMPOSER_ALLOW_SUPERUSER=1 php-cs-fixer fix ./src"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/container-dev/SKILL.md')
    assert 'sh -c "echo \'nameserver 8.8.8.8\' > /etc/resolv.conf && composer update --with-all-dependencies"' in text, "expected to find: " + 'sh -c "echo \'nameserver 8.8.8.8\' > /etc/resolv.conf && composer update --with-all-dependencies"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-review-provider/SKILL.md')
    assert '| 支付宝 | 无 | `FormatPayloadBizContentPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |' in text, "expected to find: " + '| 支付宝 | 无 | `FormatPayloadBizContentPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-review-provider/SKILL.md')
    assert '| 微信 | 无 | `AddPayloadBodyPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |' in text, "expected to find: " + '| 微信 | 无 | `AddPayloadBodyPlugin` → `AddPayloadSignaturePlugin` → `AddRadarPlugin` → `VerifySignaturePlugin` → `ResponsePlugin` |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-review-provider/SKILL.md')
    assert '| 5 | Trait 方法 | `src/Traits/{Provider}Trait.php` | `get{Provider}Url`、`verify{Provider}WebhookSign` 等 |' in text, "expected to find: " + '| 5 | Trait 方法 | `src/Traits/{Provider}Trait.php` | `get{Provider}Url`、`verify{Provider}WebhookSign` 等 |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| URL 构建 | `AlipayTrait::getAlipayUrl()`、`WechatTrait::getWechatUrl()`、`UnipayTrait::getUnipayUrl()`、`StripeTrait::getStripeUrl()` |' in text, "expected to find: " + '| URL 构建 | `AlipayTrait::getAlipayUrl()`、`WechatTrait::getWechatUrl()`、`UnipayTrait::getUnipayUrl()`、`StripeTrait::getStripeUrl()` |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| 签名验证 | `AlipayTrait::verifyAlipaySign()`、`WechatTrait::verifyWechatSign()`、`StripeTrait::verifyStripeWebhookSign()` |' in text, "expected to find: " + '| 签名验证 | `AlipayTrait::verifyAlipaySign()`、`WechatTrait::verifyWechatSign()`、`StripeTrait::verifyStripeWebhookSign()` |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- 插件管道：`StartPlugin → [前置插件] → 业务插件 → [后置插件] → ParserPlugin`（各 Provider 差异较大，详见各 Provider 的 `mergeCommonPlugins`）' in text, "expected to find: " + '- 插件管道：`StartPlugin → [前置插件] → 业务插件 → [后置插件] → ParserPlugin`（各 Provider 差异较大，详见各 Provider 的 `mergeCommonPlugins`）'[:80]

