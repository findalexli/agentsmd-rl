"""
Behavior tests for Infisical PR #5653.

Each f2p test checks one assertion captured by a corresponding vitest case
in `telemetry_groupidentify.test.ts`. Vitest is invoked once per test session
and the JSON results are cached in a module-scoped fixture.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/infisical")
BACKEND = REPO / "backend"
TEST_TS_SRC = Path("/tests/telemetry_groupidentify.test.ts")
TEST_TS_DST = BACKEND / "src" / "services" / "telemetry" / "telemetry_groupidentify.test.ts"
VITEST_JSON = Path("/tmp/vitest_results.json")


def _vitest_test_status(results: dict, name_substr: str) -> str:
    """Return 'passed' / 'failed' / 'missing' for the first vitest test
    whose fully-qualified name contains the substring."""
    for f in results.get("testResults", []):
        for a in f.get("assertionResults", []):
            full = a.get("fullName", "") or " > ".join(a.get("ancestorTitles", []) + [a.get("title", "")])
            if name_substr in full:
                return a.get("status", "missing")
    return "missing"


@pytest.fixture(scope="session")
def vitest_results():
    """Run vitest once and return parsed JSON results."""
    if not TEST_TS_SRC.exists():
        pytest.fail(f"Test file not found at {TEST_TS_SRC}")
    TEST_TS_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEST_TS_SRC, TEST_TS_DST)

    if VITEST_JSON.exists():
        VITEST_JSON.unlink()

    cmd = [
        "npx",
        "vitest",
        "run",
        "-c",
        "vitest.unit.config.mts",
        "src/services/telemetry/telemetry_groupidentify.test.ts",
        "--reporter=json",
        "--outputFile",
        str(VITEST_JSON),
    ]
    proc = subprocess.run(
        cmd,
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "NODE_ENV": "test"},
    )
    if not VITEST_JSON.exists():
        # Make failure visible — show stderr/stdout
        msg = "vitest produced no output file\n"
        msg += f"stdout (tail):\n{proc.stdout[-2000:]}\n"
        msg += f"stderr (tail):\n{proc.stderr[-2000:]}\n"
        pytest.fail(msg)
    with VITEST_JSON.open() as f:
        return json.load(f)


def test_groupidentify_includes_full_properties_in_aggregated_path(vitest_results):
    """processBucketEvents must call groupIdentify with is_cloud, plan, seat_count, created_at, name."""
    status = _vitest_test_status(
        vitest_results, "processBucketEvents groupIdentify includes is_cloud, plan, seat_count, created_at, name"
    )
    assert status == "passed", f"vitest reported '{status}' for the aggregated-path enrichment test"


def test_self_hosted_emits_is_cloud_false_and_plan_free(vitest_results):
    """Self-hosted instance: is_cloud=false, plan defaults to 'free' when slug is null."""
    status = _vitest_test_status(
        vitest_results, "self-hosted instance has is_cloud=false and plan defaults to 'free' when slug is null"
    )
    assert status == "passed", f"vitest reported '{status}' for the self-hosted defaults test"


def test_per_org_caching_within_bucket(vitest_results):
    """processBucketEvents must cache per-orgId so findOrgById/getPlan called once per org."""
    status = _vitest_test_status(
        vitest_results, "caches per-orgId so findOrgById/getPlan called once per org"
    )
    assert status == "passed", f"vitest reported '{status}' for the per-bucket cache test"


def test_send_posthog_events_fire_and_forget_enriches_groupidentify(vitest_results):
    """sendPostHogEvents fire-and-forget enriches groupIdentify with full properties."""
    status = _vitest_test_status(
        vitest_results, "sendPostHogEvents enriches groupIdentify (fire-and-forget) with full org properties"
    )
    assert status == "passed", f"vitest reported '{status}' for the fire-and-forget enrichment test"


def test_groupidentify_resilient_to_org_dal_failure(vitest_results):
    """When findOrgById throws, groupIdentify is still emitted with is_cloud/plan."""
    status = _vitest_test_status(
        vitest_results, "handles findOrgById failure gracefully"
    )
    assert status == "passed", f"vitest reported '{status}' for the orgDAL-failure resilience test"


def test_repo_typecheck():
    """pass_to_pass: backend TypeScript type-check must succeed."""
    proc = subprocess.run(
        ["npm", "run", "type:check"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"npm run type:check failed (rc={proc.returncode})\n"
        f"stdout (tail):\n{proc.stdout[-2000:]}\n"
        f"stderr (tail):\n{proc.stderr[-1000:]}"
    )
