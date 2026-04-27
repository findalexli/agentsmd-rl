"""Behavioral tests for prime-rl PR #2206."""
import importlib
import logging
import subprocess
import sys
import types
import warnings
from pathlib import Path

import pytest

REPO = Path("/workspace/prime-rl")


def _stub_eval_utils_deps():
    """Install lightweight stubs so eval_utils can be imported without verifiers/etc."""
    if "verifiers" not in sys.modules:
        verifiers = types.ModuleType("verifiers")
        verifiers.Environment = type("Environment", (), {})
        verifiers.ClientConfig = type("ClientConfig", (), {})
        sys.modules["verifiers"] = verifiers
    if "prime_rl.orchestrator.vf_utils" not in sys.modules:
        vfu = types.ModuleType("prime_rl.orchestrator.vf_utils")
        vfu.evaluate = lambda *a, **k: None
        vfu.get_completion_len = lambda *a, **k: 0
        sys.modules["prime_rl.orchestrator.vf_utils"] = vfu
    if "prime_rl.utils.monitor" not in sys.modules:
        mon = types.ModuleType("prime_rl.utils.monitor")
        mon.get_monitor = lambda: None
        sys.modules["prime_rl.utils.monitor"] = mon
    if "prime_rl.utils.utils" not in sys.modules:
        u = types.ModuleType("prime_rl.utils.utils")
        u.capitalize = lambda x: x
        sys.modules["prime_rl.utils.utils"] = u


def _fresh_orchestrator_module():
    """Force a clean re-import of the orchestrator config module."""
    for name in list(sys.modules):
        if name.startswith("prime_rl.configs.orchestrator"):
            del sys.modules[name]
    return importlib.import_module("prime_rl.configs.orchestrator")


# ---------------------------------------------------------------------------
# fail_to_pass behavioral tests
# ---------------------------------------------------------------------------


def test_envconfig_has_max_total_completion_tokens_field():
    """EnvConfig must expose a `max_total_completion_tokens` field with default -1."""
    mod = _fresh_orchestrator_module()
    fields = mod.EnvConfig.model_fields
    assert "max_total_completion_tokens" in fields, (
        f"EnvConfig is missing 'max_total_completion_tokens'. Fields: {list(fields)}"
    )
    cfg = mod.EnvConfig(id="reverse-text")
    assert cfg.max_total_completion_tokens == -1, (
        f"Default should be -1 (disabled), got {cfg.max_total_completion_tokens}"
    )


def test_envconfig_auto_populates_extra_env_kwargs():
    """After validation, EnvConfig must auto-populate extra_env_kwargs['max_total_completion_tokens']."""
    mod = _fresh_orchestrator_module()
    # Default value
    cfg = mod.EnvConfig(id="reverse-text")
    assert cfg.extra_env_kwargs.get("max_total_completion_tokens") == -1, (
        f"extra_env_kwargs should auto-populate with -1, got {cfg.extra_env_kwargs}"
    )
    # Custom value
    cfg2 = mod.EnvConfig(id="math-env", max_total_completion_tokens=4096)
    assert cfg2.extra_env_kwargs.get("max_total_completion_tokens") == 4096, (
        f"extra_env_kwargs should reflect custom value 4096, got {cfg2.extra_env_kwargs}"
    )
    # Vary another value
    cfg3 = mod.EnvConfig(id="reverse-text", max_total_completion_tokens=128)
    assert cfg3.extra_env_kwargs.get("max_total_completion_tokens") == 128


def test_envconfig_propagates_through_evalenvconfig():
    """EvalEnvConfig (subclass) must inherit the auto-population behavior."""
    mod = _fresh_orchestrator_module()
    cfg = mod.EvalEnvConfig(id="aime2024", max_total_completion_tokens=2048)
    assert cfg.max_total_completion_tokens == 2048
    assert cfg.extra_env_kwargs.get("max_total_completion_tokens") == 2048


def test_sampling_config_has_max_completion_tokens():
    """SamplingConfig must expose `max_completion_tokens` field (renamed from max_tokens)."""
    mod = _fresh_orchestrator_module()
    assert "max_completion_tokens" in mod.SamplingConfig.model_fields, (
        f"SamplingConfig must define 'max_completion_tokens'. Fields: {list(mod.SamplingConfig.model_fields)}"
    )
    # The old direct field is gone (it lives on as an alias only)
    assert "max_tokens" not in mod.SamplingConfig.model_fields


def test_sampling_config_max_tokens_alias_for_backwards_compat():
    """SamplingConfig must still accept the legacy `max_tokens` keyword as an alias."""
    mod = _fresh_orchestrator_module()
    s_new = mod.SamplingConfig(max_completion_tokens=512)
    assert s_new.max_completion_tokens == 512
    s_old = mod.SamplingConfig(max_tokens=1024)
    assert s_old.max_completion_tokens == 1024, (
        f"Legacy 'max_tokens' input must populate max_completion_tokens, got {s_old.max_completion_tokens}"
    )
    # Vary values to reject hardcoded constants
    s_other = mod.SamplingConfig(max_tokens=64)
    assert s_other.max_completion_tokens == 64


def test_eval_sampling_config_has_max_completion_tokens():
    """EvalSamplingConfig must also be renamed."""
    mod = _fresh_orchestrator_module()
    assert "max_completion_tokens" in mod.EvalSamplingConfig.model_fields
    assert "max_tokens" not in mod.EvalSamplingConfig.model_fields


def test_eval_sampling_config_max_tokens_alias():
    """EvalSamplingConfig accepts max_tokens as alias for max_completion_tokens."""
    mod = _fresh_orchestrator_module()
    es = mod.EvalSamplingConfig(max_tokens=200)
    assert es.max_completion_tokens == 200
    es2 = mod.EvalSamplingConfig(max_completion_tokens=300)
    assert es2.max_completion_tokens == 300


def test_max_tokens_emits_deprecation_warning():
    """Using legacy `max_tokens` must emit a deprecation warning naming the new field."""
    mod = _fresh_orchestrator_module()
    # The codebase uses loguru. Capture via subprocess so we can read its stderr.
    code = (
        "import sys; sys.path.insert(0, '/workspace/prime-rl/src');"
        "from prime_rl.configs.orchestrator import SamplingConfig;"
        "SamplingConfig(max_tokens=128)"
    )
    r = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    combined = (r.stdout + r.stderr).lower()
    assert "max_tokens" in (r.stdout + r.stderr), (
        f"Deprecation message should mention 'max_tokens'. stderr was: {r.stderr!r}"
    )
    assert "deprecat" in combined, (
        f"Expected a deprecation warning. Output was: stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert "max_completion_tokens" in (r.stdout + r.stderr), (
        f"Deprecation message should suggest 'max_completion_tokens'. Output: {r.stdout!r} {r.stderr!r}"
    )


def test_eval_sampling_args_uses_new_key():
    """get_eval_sampling_args must emit the OpenAI-style 'max_completion_tokens' key, not 'max_tokens'."""
    _stub_eval_utils_deps()
    # Force fresh imports so the function picks up patched configs
    for name in list(sys.modules):
        if name.startswith("prime_rl.orchestrator.eval_utils") or name.startswith("prime_rl.configs.orchestrator"):
            del sys.modules[name]
    from prime_rl.configs.orchestrator import EvalSamplingConfig
    from prime_rl.orchestrator.eval_utils import get_eval_sampling_args

    cfg = EvalSamplingConfig(max_completion_tokens=512)
    out = get_eval_sampling_args(cfg)
    assert "max_completion_tokens" in out, f"Expected 'max_completion_tokens' in {out}"
    assert out["max_completion_tokens"] == 512
    assert "max_tokens" not in out, (
        f"Output must not contain legacy 'max_tokens' key, got {out}"
    )

    # Also via the legacy alias input — output key must still be the new name
    cfg2 = EvalSamplingConfig(max_tokens=64)
    out2 = get_eval_sampling_args(cfg2)
    assert out2.get("max_completion_tokens") == 64
    assert "max_tokens" not in out2


def test_envconfig_user_can_override_extra_env_kwargs_max_total():
    """Auto-population must run AFTER user-supplied extra_env_kwargs (the validator overrides any user value
    with the field value, ensuring the field is the single source of truth)."""
    mod = _fresh_orchestrator_module()
    # User passes a stale extra_env_kwargs and the field; field wins
    cfg = mod.EnvConfig(
        id="reverse-text",
        max_total_completion_tokens=999,
        extra_env_kwargs={"max_total_completion_tokens": 1, "other": "x"},
    )
    assert cfg.extra_env_kwargs["max_total_completion_tokens"] == 999
    assert cfg.extra_env_kwargs.get("other") == "x"


# ---------------------------------------------------------------------------
# pass_to_pass — tests that already pass at base and must stay passing
# ---------------------------------------------------------------------------


def test_envconfig_validate_env_name_still_works():
    """The pre-existing `validate_env_name` validator must still reject reserved name 'all'."""
    mod = _fresh_orchestrator_module()
    with pytest.raises(Exception):
        mod.EnvConfig(id="some-id", name="all")


def test_envconfig_default_id_still_works():
    """Constructing EnvConfig with defaults must still succeed."""
    mod = _fresh_orchestrator_module()
    cfg = mod.EnvConfig()
    assert cfg.id == "reverse-text"
    assert cfg.num_workers == "auto"
    assert cfg.max_retries == 0


def test_pyproject_verifiers_rev_is_short_hash():
    """Per AGENTS.md: git dependency pins must use 7-char commit hashes for the `rev` field."""
    pyproject = (REPO / "pyproject.toml").read_text()
    # Find the verifiers source line
    import re
    m = re.search(r'verifiers\s*=\s*\{\s*git\s*=\s*"[^"]+"\s*,\s*rev\s*=\s*"([^"]+)"\s*\}', pyproject)
    assert m, "Could not locate verifiers git source pin in pyproject.toml"
    rev = m.group(1)
    assert len(rev) == 7, (
        f"verifiers rev must be a 7-char short hash per AGENTS.md, got {rev!r} (len={len(rev)})"
    )
    assert re.fullmatch(r"[0-9a-f]{7}", rev), f"rev must be hex, got {rev!r}"
