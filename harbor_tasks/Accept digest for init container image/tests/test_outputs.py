"""
Test suite for init container digest support in Dagster Helm chart.

These tests verify that:
1. Legacy string image format for init containers still works
2. Structured image format with tag works
3. Structured image format with digest works
4. Digest takes precedence over tag when both specified
5. pullPolicy is properly passed through for structured images
"""

import subprocess
import tempfile
import os
import yaml
import json

REPO_ROOT = "/workspace/dagster"
HELM_CHART_PATH = f"{REPO_ROOT}/helm/dagster/charts/dagster-user-deployments"


def run_helm_template(values_content: str) -> str:
    """Run helm template and return the output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(values_content)
        values_file = f.name

    try:
        result = subprocess.run(
            ["helm", "template", "test-release", ".", "-f", values_file],
            cwd=HELM_CHART_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"Helm template failed: {result.stderr}")
        return result.stdout
    finally:
        os.unlink(values_file)


def extract_init_containers(output: str) -> list:
    """Extract init container specs from helm template output."""
    docs = list(yaml.safe_load_all(output))
    init_containers = []

    for doc in docs:
        if doc and doc.get("kind") == "Deployment":
            spec = doc.get("spec", {}).get("template", {}).get("spec", {})
            containers = spec.get("initContainers", [])
            init_containers.extend(containers)

    return init_containers


def test_init_container_string_image_format():
    """
    Test that init containers with legacy string image format still work.
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-test
        image: "busybox:latest"
        command: ["sh", "-c", "echo hello"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 1, f"Expected 1 init container, got {len(containers)}"
    assert containers[0]["name"] == "init-test"
    assert containers[0]["image"] == "busybox:latest"
    assert containers[0]["command"] == ["sh", "-c", "echo hello"]


def test_init_container_structured_image_with_tag():
    """
    Test init container with structured image format using tag.
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-test
        image:
          repository: "busybox"
          tag: "1.36"
        command: ["sh", "-c", "echo hello"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 1, f"Expected 1 init container, got {len(containers)}"
    assert containers[0]["name"] == "init-test"
    assert containers[0]["image"] == "busybox:1.36"


def test_init_container_structured_image_with_digest():
    """
    Test init container with structured image format using digest.
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-test
        image:
          repository: "busybox"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo hello"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 1, f"Expected 1 init container, got {len(containers)}"
    assert containers[0]["name"] == "init-test"
    assert containers[0]["image"] == "busybox@sha256:abc123def456"


def test_init_container_digest_takes_precedence():
    """
    Test that digest takes precedence over tag for init container images.
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-test
        image:
          repository: "busybox"
          tag: "1.36"
          digest: "sha256:abc123def456"
        command: ["sh", "-c", "echo hello"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 1, f"Expected 1 init container, got {len(containers)}"
    assert containers[0]["name"] == "init-test"
    # Digest should take precedence over tag
    assert containers[0]["image"] == "busybox@sha256:abc123def456"


def test_init_container_pull_policy():
    """
    Test that pullPolicy is properly set for init containers with structured images.
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-test
        image:
          repository: "busybox"
          tag: "1.36"
          pullPolicy: "IfNotPresent"
        command: ["sh", "-c", "echo hello"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 1, f"Expected 1 init container, got {len(containers)}"
    assert containers[0]["name"] == "init-test"
    assert containers[0]["image"] == "busybox:1.36"
    assert containers[0].get("imagePullPolicy") == "IfNotPresent"


def test_init_container_multiple_mixed_formats():
    """
    Test multiple init containers with mixed formats (string and structured).
    F2P: This test should FAIL before the fix and PASS after.
    """
    values = """
deployments:
  - name: "test-deployment"
    image:
      repository: "docker.io/test/app"
      tag: "v1.0.0"
      pullPolicy: "Always"
    dagsterApiGrpcArgs:
      - "-f"
      - "/test/repo.py"
    port: 3030
    securityContext: {}
    includeConfigInLaunchedRuns:
      enabled: true
    initContainers:
      - name: init-string
        image: "alpine:3.18"
        command: ["sh", "-c", "echo first"]
      - name: init-structured
        image:
          repository: "busybox"
          digest: "sha256:xyz789"
        command: ["sh", "-c", "echo second"]
"""
    output = run_helm_template(values)
    containers = extract_init_containers(output)

    assert len(containers) == 2, f"Expected 2 init containers, got {len(containers)}"

    # First container should use string format
    assert containers[0]["name"] == "init-string"
    assert containers[0]["image"] == "alpine:3.18"

    # Second container should use structured format with digest
    assert containers[1]["name"] == "init-structured"
    assert containers[1]["image"] == "busybox@sha256:xyz789"


def test_python_schema_classes_exist():
    """
    Test that the required Python schema classes exist and are importable.
    F2P: This test should FAIL before the fix and PASS after.
    """
    # Install pydantic if not available
    r = subprocess.run(
        ["pip", "install", "pydantic", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Failed to install pydantic: {r.stderr[-500:]}"

    # Add the schema path to import
    import sys
    schema_path = f"{REPO_ROOT}/helm/dagster/schema"
    sys.path.insert(0, schema_path)

    try:
        from schema.charts.utils.kubernetes import InitContainerImage, InitContainerWithStructuredImage

        # Test InitContainerImage creation
        image_with_tag = InitContainerImage(repository="busybox", tag="1.36")
        assert image_with_tag.name == "busybox:1.36"

        # Test InitContainerImage with digest
        image_with_digest = InitContainerImage(repository="busybox", digest="sha256:abc123")
        assert image_with_digest.name == "busybox@sha256:abc123"

        # Test that digest takes precedence
        image_both = InitContainerImage(repository="busybox", tag="1.36", digest="sha256:abc123")
        assert image_both.name == "busybox@sha256:abc123"

        # Test InitContainerWithStructuredImage
        container = InitContainerWithStructuredImage(
            name="init-test",
            image=image_with_digest
        )
        assert container.name == "init-test"
        assert container.image.name == "busybox@sha256:abc123"

    finally:
        sys.path.remove(schema_path)


def test_values_schema_updated():
    """
    Test that the values.schema.json files include the new InitContainerImage schema.
    P2P: This test verifies the schema is properly defined.
    """
    subchart_schema_path = f"{REPO_ROOT}/helm/dagster/charts/dagster-user-deployments/values.schema.json"
    main_schema_path = f"{REPO_ROOT}/helm/dagster/values.schema.json"

    for schema_path in [subchart_schema_path, main_schema_path]:
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Check that InitContainerImage is defined
        defs = schema.get("$defs", {})
        assert "InitContainerImage" in defs, f"InitContainerImage not found in {schema_path}"

        # Check that InitContainerWithStructuredImage is defined
        assert "InitContainerWithStructuredImage" in defs, f"InitContainerWithStructuredImage not found in {schema_path}"

        # Check that initContainers uses the union type
        user_deployment = defs.get("UserDeployment", {})
        init_containers_prop = user_deployment.get("properties", {}).get("initContainers", {})

        # The schema has nested anyOf: initContainers.anyOf[0].items.anyOf[] contains the refs
        init_any_of = init_containers_prop.get("anyOf", [])

        # Find the array type entry and check its items.anyOf
        found_ref = False
        for entry in init_any_of:
            if entry.get("type") == "array":
                items = entry.get("items", {})
                item_any_of = items.get("anyOf", [])
                for ref_item in item_any_of:
                    ref = ref_item.get("$ref", "")
                    if "InitContainerWithStructuredImage" in ref:
                        found_ref = True
                        break
                if found_ref:
                    break

        assert found_ref, \
            f"InitContainers should reference InitContainerWithStructuredImage in {schema_path}"


def test_helpers_tpl_has_init_container_definitions():
    """
    Test that the _helpers.tpl file contains the required helper definitions.
    P2P: This test verifies the template helpers exist.
    """
    helpers_path = f"{HELM_CHART_PATH}/templates/helpers/_helpers.tpl"

    with open(helpers_path, 'r') as f:
        content = f.read()

    # Check for dagster.initContainerImage.name definition
    assert 'define "dagster.initContainerImage.name"' in content, \
        "Missing dagster.initContainerImage.name helper definition"

    # Check for dagster.initContainer definition
    assert 'define "dagster.initContainer"' in content, \
        "Missing dagster.initContainer helper definition"

    # Check for kindIs "string" check for backwards compatibility
    assert 'kindIs "string"' in content, \
        "Missing kindIs string check for backwards compatibility"

    # Check for digest handling
    assert "$image.digest" in content, \
        "Missing digest handling in template"

    # Check for imagePullPolicy handling
    assert "imagePullPolicy" in content, \
        "Missing imagePullPolicy handling in template"


def test_deployment_template_uses_helper():
    """
    Test that deployment-user.yaml uses the new dagster.initContainer helper.
    P2P: This test verifies the deployment template is updated.
    """
    deployment_path = f"{HELM_CHART_PATH}/templates/deployment-user.yaml"

    with open(deployment_path, 'r') as f:
        content = f.read()

    # Should use the new helper instead of direct toYaml
    assert 'include "dagster.initContainer"' in content, \
        "deployment-user.yaml should use dagster.initContainer helper"

    # Should iterate over initContainers with range
    assert "range $container := $deployment.initContainers" in content, \
        "Should iterate over initContainers with range"




def test_repo_schema_tests():
    """
    Run the repo's own schema tests for user deployments.
    P2P: These tests verify the Dagster Helm chart schema and templates work correctly.
    Origin: helm/dagster/schema/schema_tests/test_user_deployments.py
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the files, copy from /dagster-src mount
    if not os.path.exists(f"{REPO_ROOT}/helm/dagster/schema/schema_tests"):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    # Install required dependencies
    r = subprocess.run(
        ["pip", "install", "-e", f"{REPO_ROOT}/python_modules/libraries/dagster-k8s", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT
    )
    assert r.returncode == 0, f"Failed to install dagster-k8s: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pip", "install", "kubernetes", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO_ROOT
    )
    assert r.returncode == 0, f"Failed to install kubernetes: {r.stderr[-500:]}"

    # Run the repo's schema tests
    schema_path = f"{REPO_ROOT}/helm/dagster/schema"
    r = subprocess.run(
        ["pytest", "schema_tests/test_user_deployments.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=600, cwd=schema_path
    )
    assert r.returncode == 0, f"Repo schema tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_helm_lint():
    """
    Run helm lint on the dagster-user-deployments chart.
    P2P: This verifies the Helm chart passes linting.
    Origin: CI workflow helm chart validation
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the chart, copy from /dagster-src mount
    if not os.path.exists(HELM_CHART_PATH):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    r = subprocess.run(
        ["helm", "lint", ".", "--strict"],
        capture_output=True, text=True, timeout=60, cwd=HELM_CHART_PATH
    )
    assert r.returncode == 0, f"Helm lint on user-deployments chart failed:\n{r.stdout}\n{r.stderr}"


def test_repo_helm_lint_main_chart():
    """
    Run helm lint on the main dagster chart with subcharts.
    P2P: This verifies the main Helm chart and all subcharts pass linting.
    Origin: CI workflow - helm lint helm/dagster --with-subcharts --strict
    """
    import shutil

    MAIN_CHART_PATH = f"{REPO_ROOT}/helm/dagster"

    # If REPO_ROOT doesn't exist or doesn't have the chart, copy from /dagster-src mount
    if not os.path.exists(MAIN_CHART_PATH):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    r = subprocess.run(
        ["helm", "lint", ".", "--with-subcharts", "--strict"],
        capture_output=True, text=True, timeout=60, cwd=MAIN_CHART_PATH
    )
    assert r.returncode == 0, f"Helm lint on main chart failed:\n{r.stdout}\n{r.stderr}"


def test_repo_schema_all_tests():
    """
    Run the repo's full schema test suite (dagit, daemon, celery queues).
    P2P: These tests verify the Dagster Helm chart schema and templates work correctly.
    Origin: helm/dagster/schema/schema_tests/*.py (161 tests total)
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the files, copy from /dagster-src mount
    if not os.path.exists(f"{REPO_ROOT}/helm/dagster/schema/schema_tests"):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    # Install required dependencies
    r = subprocess.run(
        ["pip", "install", "-e", f"{REPO_ROOT}/helm/dagster/schema", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT
    )
    assert r.returncode == 0, f"Failed to install schema package: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pip", "install", "-e", f"{REPO_ROOT}/python_modules/libraries/dagster-k8s", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT
    )
    assert r.returncode == 0, f"Failed to install dagster-k8s: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pip", "install", "kubernetes", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO_ROOT
    )
    assert r.returncode == 0, f"Failed to install kubernetes: {r.stderr[-500:]}"

    # Run the repo's schema tests (excluding tests that need extra deps)
    schema_path = f"{REPO_ROOT}/helm/dagster/schema"
    test_files = [
        "schema_tests/test_user_deployments.py",
        "schema_tests/test_dagit.py",
        "schema_tests/test_dagster_daemon.py",
        "schema_tests/test_celery_queues.py",
    ]
    r = subprocess.run(
        ["pytest"] + test_files + ["-v", "--tb=short"],
        capture_output=True, text=True, timeout=600, cwd=schema_path
    )
    assert r.returncode == 0, f"Repo schema tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_schema_dagit():
    """
    Run the repo's dagit schema tests.
    P2P: These tests verify the Dagster webserver Helm chart configuration.
    Origin: helm/dagster/schema/schema_tests/test_dagit.py (~40 tests)
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the files, copy from /dagster-src mount
    if not os.path.exists(f"{REPO_ROOT}/helm/dagster/schema/schema_tests"):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    # Install required dependencies
    for pkg in [f"{REPO_ROOT}/helm/dagster/schema", f"{REPO_ROOT}/python_modules/libraries/dagster-k8s", "kubernetes"]:
        r = subprocess.run(
            ["pip", "install", "-e", pkg, "-q"] if pkg.startswith("/") else ["pip", "install", pkg, "-q"],
            capture_output=True, text=True, timeout=120, cwd=REPO_ROOT
        )
        assert r.returncode == 0, f"Failed to install {pkg}: {r.stderr[-500:]}"

    # Run dagit tests
    schema_path = f"{REPO_ROOT}/helm/dagster/schema"
    r = subprocess.run(
        ["pytest", "schema_tests/test_dagit.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=schema_path
    )
    assert r.returncode == 0, f"Dagit schema tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_schema_daemon():
    """
    Run the repo's dagster-daemon schema tests.
    P2P: These tests verify the Dagster daemon Helm chart configuration.
    Origin: helm/dagster/schema/schema_tests/test_dagster_daemon.py (~30 tests)
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the files, copy from /dagster-src mount
    if not os.path.exists(f"{REPO_ROOT}/helm/dagster/schema/schema_tests"):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    # Install required dependencies
    for pkg in [f"{REPO_ROOT}/helm/dagster/schema", f"{REPO_ROOT}/python_modules/libraries/dagster-k8s", "kubernetes"]:
        r = subprocess.run(
            ["pip", "install", "-e", pkg, "-q"] if pkg.startswith("/") else ["pip", "install", pkg, "-q"],
            capture_output=True, text=True, timeout=120, cwd=REPO_ROOT
        )
        assert r.returncode == 0, f"Failed to install {pkg}: {r.stderr[-500:]}"

    # Run daemon tests
    schema_path = f"{REPO_ROOT}/helm/dagster/schema"
    r = subprocess.run(
        ["pytest", "schema_tests/test_dagster_daemon.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=schema_path
    )
    assert r.returncode == 0, f"Daemon schema tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_ruff():
    """
    Run ruff linter on the Helm schema code.
    P2P: This verifies the Python code passes linting checks.
    Origin: Makefile - make ruff / make check_ruff
    """
    import shutil

    # If REPO_ROOT doesn't exist or doesn't have the files, copy from /dagster-src mount
    if not os.path.exists(f"{REPO_ROOT}/helm/dagster/schema"):
        if os.path.exists("/dagster-src"):
            os.makedirs(os.path.dirname(REPO_ROOT), exist_ok=True)
            if os.path.exists(REPO_ROOT):
                shutil.rmtree(REPO_ROOT)
            shutil.copytree("/dagster-src", REPO_ROOT, symlinks=True)

    # Install ruff with the required version from pyproject.toml
    r = subprocess.run(
        ["pip", "install", "ruff==0.11.5", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    # Run ruff check on the Helm schema code
    r = subprocess.run(
        ["ruff", "check", f"{REPO_ROOT}/helm/dagster/schema/"],
        capture_output=True, text=True, timeout=120
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
