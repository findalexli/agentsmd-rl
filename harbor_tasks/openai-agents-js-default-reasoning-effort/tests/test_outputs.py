"""Behavioral and regression tests for the GPT-5 default model resolver."""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/agents-js"
TSX = f"{REPO}/node_modules/.bin/tsx"
SRC_IMPORT = "./packages/agents-core/src/defaultModel"


def _node_eval(code: str, timeout: int = 60) -> str:
    """Run a tsx -e snippet in the repo root and return stdout's last line."""
    r = subprocess.run(
        [TSX, "-e", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert r.returncode == 0, (
        f"tsx invocation failed (rc={r.returncode}):\n"
        f"--- stderr ---\n{r.stderr[-1500:]}\n"
        f"--- stdout ---\n{r.stdout[-1500:]}"
    )
    out = r.stdout.strip().splitlines()
    assert out, f"tsx produced no output. stderr: {r.stderr[-500:]}"
    return out[-1]


def _settings_for(model: str) -> dict:
    code = (
        f"import {{ getDefaultModelSettings }} from '{SRC_IMPORT}';"
        f"console.log(JSON.stringify(getDefaultModelSettings({json.dumps(model)})));"
    )
    return json.loads(_node_eval(code))


def _required_for(model: str) -> bool:
    code = (
        f"import {{ gpt5ReasoningSettingsRequired }} from '{SRC_IMPORT}';"
        f"console.log(JSON.stringify(gpt5ReasoningSettingsRequired({json.dumps(model)})));"
    )
    return json.loads(_node_eval(code))


# ── fail-to-pass: behavioral changes introduced by the fix ──────────────

def test_gpt5_4_default_effort_is_none():
    """gpt-5.4 must default to reasoning.effort='none' with verbosity='low'."""
    assert _settings_for("gpt-5.4") == {
        "reasoning": {"effort": "none"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_4_mini_default_effort_is_none():
    """gpt-5.4-mini must default to reasoning.effort='none' with verbosity='low'."""
    assert _settings_for("gpt-5.4-mini") == {
        "reasoning": {"effort": "none"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_4_nano_default_effort_is_none():
    """gpt-5.4-nano must default to reasoning.effort='none' with verbosity='low'."""
    assert _settings_for("gpt-5.4-nano") == {
        "reasoning": {"effort": "none"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_4_pro_default_effort_is_medium():
    """gpt-5.4-pro must default to reasoning.effort='medium' with verbosity='low'."""
    assert _settings_for("gpt-5.4-pro") == {
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_3_codex_default_effort_is_none():
    """gpt-5.3-codex must default to reasoning.effort='none'."""
    assert _settings_for("gpt-5.3-codex") == {
        "reasoning": {"effort": "none"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_4_dated_snapshot_resolves_like_family():
    """A dated snapshot like gpt-5.4-2026-03-05 must resolve to the same defaults."""
    assert _settings_for("gpt-5.4-2026-03-05") == {
        "reasoning": {"effort": "none"},
        "text": {"verbosity": "low"},
    }
    assert _settings_for("gpt-5.4-pro-2026-03-05") == {
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "low"},
    }


def test_gpt5_mini_omits_reasoning_effort():
    """gpt-5-mini default settings must NOT include a reasoning.effort key.

    Variants without confirmed support for a particular effort value must
    keep the verbosity default but omit reasoning entirely.
    """
    settings = _settings_for("gpt-5-mini")
    assert "reasoning" not in settings, (
        f"gpt-5-mini must not assume a reasoning.effort default; got {settings}"
    )
    assert settings == {"text": {"verbosity": "low"}}


def test_gpt5_nano_omits_reasoning_effort():
    """gpt-5-nano must also omit reasoning.effort from its default settings."""
    settings = _settings_for("gpt-5-nano")
    assert "reasoning" not in settings, (
        f"gpt-5-nano must not assume a reasoning.effort default; got {settings}"
    )
    assert settings == {"text": {"verbosity": "low"}}


def test_chat_latest_aliases_have_empty_settings():
    """All chat-latest aliases must return empty settings (no reasoning, no verbosity)."""
    for alias in (
        "gpt-5-chat-latest",
        "gpt-5.1-chat-latest",
        "gpt-5.2-chat-latest",
        "gpt-5.3-chat-latest",
    ):
        assert _settings_for(alias) == {}, f"{alias} must return empty settings"


def test_chat_latest_aliases_do_not_require_reasoning():
    """gpt5ReasoningSettingsRequired must return false for every chat-latest alias."""
    for alias in (
        "gpt-5-chat-latest",
        "gpt-5.1-chat-latest",
        "gpt-5.2-chat-latest",
        "gpt-5.3-chat-latest",
    ):
        assert _required_for(alias) is False, (
            f"{alias} must not require reasoning settings"
        )


def test_pro_models_still_require_reasoning():
    """Pro-tier reasoning models must still report that reasoning settings are required."""
    results = {model: _required_for(model) for model in ("gpt-5.2-pro", "gpt-5.4-pro")}
    assert results == {"gpt-5.2-pro": True, "gpt-5.4-pro": True}, results


# ── pass-to-pass: behaviors that hold both before and after the fix ─────

def test_gpt5_base_low_effort_unchanged():
    """The base 'gpt-5' model continues to default to reasoning.effort='low'."""
    assert _settings_for("gpt-5") == {
        "reasoning": {"effort": "low"},
        "text": {"verbosity": "low"},
    }


def test_non_gpt5_returns_empty_settings():
    """Non GPT-5 models continue to return empty default settings."""
    assert _settings_for("gpt-4o") == {}


def test_repo_unit_tests_pass():
    """The agents-core vitest suite still passes."""
    env = {**os.environ, "CI": "1", "NODE_ENV": "test"}
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "exec", "vitest", "run"],
        cwd=REPO, capture_output=True, text=True, timeout=600, env=env,
    )
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}):\n"
        f"--- stdout tail ---\n{r.stdout[-2000:]}\n"
        f"--- stderr tail ---\n{r.stderr[-1000:]}"
    )


def test_repo_typecheck_passes():
    """tsc --noEmit on agents-core test config still passes."""
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"build-check failed (rc={r.returncode}):\n"
        f"--- stdout tail ---\n{r.stdout[-2000:]}\n"
        f"--- stderr tail ---\n{r.stderr[-1000:]}"
    )


def test_repo_lint_passes():
    """ESLint passes on the repository (Conventional Commits style)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"pnpm lint failed (rc={r.returncode}):\n"
        f"--- stdout tail ---\n{r.stdout[-2000:]}\n"
        f"--- stderr tail ---\n{r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_detects_GPT_5_models_while_ignoring_chat_latest_():
    """fail_to_pass | PR added test 'detects GPT-5 models while ignoring chat latest families' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest families" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest families" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest families" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "detects GPT-5 models while ignoring chat latest families" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'detects GPT-5 models while ignoring chat latest families' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_1_mode():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.1 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.1 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.1 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.1 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.1 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.1 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_2_mode():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.2 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.2 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.2 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.2 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.2 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.2 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_3_code():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.3 codex models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.3 codex models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.3 codex models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.3 codex models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.3 codex models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.3 codex models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_4_mode():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.4 models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.4 models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_4_snap():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.4 snapshot families' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 snapshot families" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 snapshot families" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 snapshot families" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 snapshot families" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.4 snapshot families' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_none_reasoning_defaults_for_GPT_5_4_mini():
    """fail_to_pass | PR added test 'returns none reasoning defaults for GPT-5.4 mini and nano models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 mini and nano models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 mini and nano models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 mini and nano models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns none reasoning defaults for GPT-5.4 mini and nano models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns none reasoning defaults for GPT-5.4 mini and nano models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_low_effort_defaults_for_the_base_GPT_5_m():
    """fail_to_pass | PR added test 'returns low-effort defaults for the base GPT-5 model' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for the base GPT-5 model" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for the base GPT-5 model" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for the base GPT-5 model" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for the base GPT-5 model" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns low-effort defaults for the base GPT-5 model' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_low_effort_defaults_for_GPT_5_2_codex_mo():
    """fail_to_pass | PR added test 'returns low-effort defaults for GPT-5.2 codex models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for GPT-5.2 codex models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for GPT-5.2 codex models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for GPT-5.2 codex models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns low-effort defaults for GPT-5.2 codex models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns low-effort defaults for GPT-5.2 codex models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_medium_defaults_for_GPT_5_pro_models():
    """fail_to_pass | PR added test 'returns medium defaults for GPT-5 pro models' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns medium defaults for GPT-5 pro models" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns medium defaults for GPT-5 pro models" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns medium defaults for GPT-5 pro models" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns medium defaults for GPT-5 pro models" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns medium defaults for GPT-5 pro models' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_omits_reasoning_defaults_for_GPT_5_variants_with():
    """fail_to_pass | PR added test 'omits reasoning defaults for GPT-5 variants without confirmed support' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "omits reasoning defaults for GPT-5 variants without confirmed support" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "omits reasoning defaults for GPT-5 variants without confirmed support" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "omits reasoning defaults for GPT-5 variants without confirmed support" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "omits reasoning defaults for GPT-5 variants without confirmed support" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'omits reasoning defaults for GPT-5 variants without confirmed support' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_empty_settings_for_GPT_5_chat_latest_ali():
    """fail_to_pass | PR added test 'returns empty settings for GPT-5 chat latest aliases' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns empty settings for GPT-5 chat latest aliases" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns empty settings for GPT-5 chat latest aliases" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns empty settings for GPT-5 chat latest aliases" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns empty settings for GPT-5 chat latest aliases" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns empty settings for GPT-5 chat latest aliases' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_returns_true_only_when_env_points_to_GPT_5():
    """fail_to_pass | PR added test 'returns true only when env points to GPT-5' in 'packages/agents-core/test/defaultModel.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns true only when env points to GPT-5" 2>&1 || npx vitest run "packages/agents-core/test/defaultModel.test.ts" -t "returns true only when env points to GPT-5" 2>&1 || pnpm jest "packages/agents-core/test/defaultModel.test.ts" -t "returns true only when env points to GPT-5" 2>&1 || npx jest "packages/agents-core/test/defaultModel.test.ts" -t "returns true only when env points to GPT-5" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns true only when env points to GPT-5' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
