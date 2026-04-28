"""
Task: beam-recommendations-ai-tagged-outputs
Repo: beam @ 8044fcb3e6e394db4be60a7883eb9572ebd41eac
PR:   38103

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import os
from unittest.mock import MagicMock, patch

REPO = "/workspace/beam"


def _get_mock_catalog_client(succeed=True):
    """Build a mock Recommendations AI catalog client."""
    from google.cloud import recommendationengine

    client = MagicMock()
    if succeed:
        client.create_catalog_item.return_value = recommendationengine.CatalogItem(
            {
                "id": "mock_created",
                "title": "Mock Created Item",
                "category_hierarchies": [{"categories": ["electronics"]}],
            }
        )
    else:
        client.create_catalog_item.side_effect = RuntimeError("Simulated API failure")
    return client


def _make_catalog_items(n, prefix="item"):
    """Generate diverse catalog item dicts to avoid single-value hardcoding."""
    categories = ["electronics", "books", "clothing", "furniture", "food"]
    return [
        {
            "id": f"{prefix}_{i}",
            "title": f"Test {prefix.title()} {i}",
            "language_code": "en",
            "category_hierarchies": [
                {"categories": [categories[i % len(categories)]]}
            ],
        }
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    target = os.path.join(
        REPO, "sdks", "python", "apache_beam", "ml", "gcp", "recommendations_ai.py"
    )
    py_compile.compile(target, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_expand_returns_tagged_output_type():
    """CreateCatalogItem must return tagged outputs with created_catalog_items and failed_catalog_items."""
    import apache_beam as beam
    from apache_beam.ml.gcp import recommendations_ai

    mock_client = _get_mock_catalog_client(succeed=True)
    with patch.object(
        recommendations_ai,
        "get_recommendation_catalog_client",
        return_value=mock_client,
    ):
        p = beam.Pipeline()
        items = _make_catalog_items(n=2, prefix="tag_check")
        result = (
            p
            | beam.Create(items)
            | recommendations_ai.CreateCatalogItem(project="test-project")
        )

        assert hasattr(result, "created_catalog_items"), (
            f"Expected tagged output 'created_catalog_items' on "
            f"{type(result).__name__}"
        )
        assert hasattr(result, "failed_catalog_items"), (
            f"Expected tagged output 'failed_catalog_items' on "
            f"{type(result).__name__}"
        )


# [pr_diff] fail_to_pass
def test_success_items_routed_to_created_output():
    """Successfully created items must appear in the created_catalog_items PCollection."""
    import apache_beam as beam
    from apache_beam.testing.util import assert_that, is_not_empty
    from apache_beam.ml.gcp import recommendations_ai

    mock_client = _get_mock_catalog_client(succeed=True)
    with patch.object(
        recommendations_ai,
        "get_recommendation_catalog_client",
        return_value=mock_client,
    ):
        with beam.Pipeline() as p:
            items = _make_catalog_items(n=4, prefix="success")
            result = (
                p
                | beam.Create(items)
                | recommendations_ai.CreateCatalogItem(project="test-project")
            )
            assert_that(result.created_catalog_items, is_not_empty())


# [pr_diff] fail_to_pass
def test_failure_items_routed_to_failed_output():
    """Items that fail creation must appear in the failed_catalog_items PCollection."""
    import apache_beam as beam
    from apache_beam.testing.util import assert_that, is_not_empty
    from apache_beam.ml.gcp import recommendations_ai

    mock_client = _get_mock_catalog_client(succeed=False)
    with patch.object(
        recommendations_ai,
        "get_recommendation_catalog_client",
        return_value=mock_client,
    ):
        with beam.Pipeline() as p:
            items = _make_catalog_items(n=3, prefix="fail")
            result = (
                p
                | beam.Create(items)
                | recommendations_ai.CreateCatalogItem(project="test-project")
            )
            assert_that(result.failed_catalog_items, is_not_empty())


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_unit_tests_relevant():
    """Repo's unit tests for recommendations_ai module pass (pass_to_pass)."""
    # Need cachetools for the module to import properly
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "cachetools"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "apache_beam/ml/gcp/recommendations_ai_test.py",
            "-v", "--tb=short",
        ],
        capture_output=True, text=True, timeout=120,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"Unit tests failed:{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pylint():
    """Repo's pylint check on modified file passes (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pylint"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [
            sys.executable, "-m", "pylint",
            "apache_beam/ml/gcp/recommendations_ai.py",
            "--rcfile=.pylintrc",
        ],
        capture_output=True, text=True, timeout=120,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"Pylint failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_yapf():
    """Repo's yapf formatting check on modified file passes (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "yapf"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [
            sys.executable, "-m", "yapf",
            "--diff",
            "apache_beam/ml/gcp/recommendations_ai.py",
        ],
        capture_output=True, text=True, timeout=120,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"Yapf formatting check failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flake8():
    """Repo's flake8 syntax check on modified file passes (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "flake8"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [
            sys.executable, "-m", "flake8",
            "apache_beam/ml/gcp/recommendations_ai.py",
            "--count",
            "--select=E9,F821,F822,F823",
            "--show-source",
            "--statistics",
        ],
        capture_output=True, text=True, timeout=120,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"Flake8 check failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort import ordering check on modified file passes (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "isort==7.0.0"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [
            sys.executable, "-m", "isort",
            "apache_beam/ml/gcp/recommendations_ai.py",
            "-p", "apache_beam",
            "--line-width", "120",
            "--check-only",
            "--order-by-type",
            "--combine-star",
            "--force-single-line-imports",
            "--diff",
            "--magic-placement",
        ],
        capture_output=True, text=True, timeout=120,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"Isort check failed:{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ml_gcp_unit_tests():
    """All ml/gcp unit tests pass (pass_to_pass) - covers entire modified module."""
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "apache_beam/ml/gcp/",
            "-v", "--tb=short",
            "--ignore-glob=*_it*",
            "-x",
        ],
        capture_output=True, text=True, timeout=300,
        cwd=os.path.join(REPO, "sdks/python"),
    )
    assert r.returncode == 0, f"ML/GCP unit tests failed:{r.stdout[-1000:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_pipeline_runs_successfully():
    """CreateCatalogItem must complete pipeline execution without error."""
    import apache_beam as beam
    from apache_beam.ml.gcp import recommendations_ai

    mock_client = _get_mock_catalog_client(succeed=True)
    with patch.object(
        recommendations_ai,
        "get_recommendation_catalog_client",
        return_value=mock_client,
    ):
        p = beam.Pipeline()
        items = _make_catalog_items(n=5, prefix="run_check")
        _ = (
            p
            | beam.Create(items)
            | recommendations_ai.CreateCatalogItem(project="test-project")
        )
        result = p.run()
        result.wait_until_finish()

def test_ci_build_python_source_distributi_build_source():
    """pass_to_pass | CI job 'Build python source distribution' → step 'Build source'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -U build && python -m build --sdist'], cwd=os.path.join(REPO, './sdks/python'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build source' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typescript_unit_tests_npm():
    """pass_to_pass | CI job 'TypeScript Unit Tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=os.path.join(REPO, './sdks/typescript'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typescript_unit_tests_npm_2():
    """pass_to_pass | CI job 'TypeScript Unit Tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=os.path.join(REPO, './sdks/typescript'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typescript_unit_tests_npm_3():
    """pass_to_pass | CI job 'TypeScript Unit Tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run prettier-check'], cwd=os.path.join(REPO, './sdks/typescript'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typescript_unit_tests_npm_4():
    """pass_to_pass | CI job 'TypeScript Unit Tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm test'], cwd=os.path.join(REPO, './sdks/typescript'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_environment_variables_check_are_gcp_variables_set():
    """pass_to_pass | CI job 'Check environment variables' → step 'Check are GCP variables set'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/ci/ci_check_are_gcp_variables_set.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check are GCP variables set' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
