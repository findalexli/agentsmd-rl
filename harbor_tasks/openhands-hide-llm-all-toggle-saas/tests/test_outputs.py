"""Verifier for OpenHands PR #14013: hide All toggle in SaaS LLM settings."""
import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/OpenHands")
FRONTEND = REPO / "frontend"
SDK_SECTION = FRONTEND / "src/components/features/settings/sdk-settings/sdk-section-page.tsx"
LLM_ROUTE = FRONTEND / "src/routes/llm-settings.tsx"


def _run(cmd, cwd=FRONTEND, timeout=900, env_extra=None):
    env = os.environ.copy()
    env.setdefault("CI", "1")
    env.setdefault("NODE_OPTIONS", "--max-old-space-size=4096")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout, env=env,
    )


# ---------- f2p (fail-to-pass): the PR's new behaviour tests ----------

def test_f2p_force_advanced_toggle_for_critical_only_schema():
    """Vitest: 'shows the advanced toggle when it is forced for a critical-only schema'.

    Fails on base because SdkSectionPage does not accept the forcing prop.
    """
    r = _run([
        "npx", "vitest", "run",
        "__tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx",
        "-t", "shows the advanced toggle when it is forced for a critical-only schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


def test_f2p_oss_shows_advanced_and_all_toggles():
    """Vitest: 'shows Advanced and All toggles in OSS mode for the default LLM route schema'."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
        "-t", "shows Advanced and All toggles in OSS mode for the default LLM route schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


def test_f2p_saas_keeps_advanced_hides_all():
    """Vitest: 'keeps Advanced visible but hides All in SaaS mode for the default LLM route schema'."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
        "-t", "keeps Advanced visible but hides All in SaaS mode for the default LLM route schema",
    ], timeout=900)
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1000:]}"
    )


# ---------- p2p (pass-to-pass): repo CI keeps working ----------

def test_p2p_full_llm_settings_test_file():
    """Whole llm-settings.test.tsx passes (repo's existing route tests must not regress)."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
    ], timeout=900)
    assert r.returncode == 0, (
        f"llm-settings test file failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_p2p_full_sdk_section_page_test_file():
    """Whole sdk-section-page.test.tsx passes (repo's existing component tests must not regress)."""
    r = _run([
        "npx", "vitest", "run",
        "__tests__/components/features/settings/sdk-settings/sdk-section-page.test.tsx",
    ], timeout=900)
    assert r.returncode == 0, (
        f"sdk-section-page test file failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_p2p_build():
    """The repo's frontend build (`npm run build`) succeeds — required by AGENTS.md."""
    r = _run(["npm", "run", "build"], timeout=900)
    assert r.returncode == 0, (
        f"build failed (rc={r.returncode}).\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )
