"""Behavioral checks for kuma-choredevx-add-claudemd-and-clauderules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kuma")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/debug.md')
    assert 'k3d init containers sometimes get throttled on local machines. Set `K3D_HELM_DEPLOY_NO_CNI=true` to reduce resource pressure. If still slow, comment out CPU limits in `pkg/plugins/runtime/k8s/webhooks' in text, "expected to find: " + 'k3d init containers sometimes get throttled on local machines. Set `K3D_HELM_DEPLOY_NO_CNI=true` to reduce resource pressure. If still slow, comment out CPU limits in `pkg/plugins/runtime/k8s/webhooks'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/debug.md')
    assert 'Renamed targets that will error: `k3d/restart` (use `k3d/restart/kumactl`), `k3d/deploy/kuma` (use `k3d/deploy/kumactl`).' in text, "expected to find: " + 'Renamed targets that will error: `k3d/restart` (use `k3d/restart/kumactl`), `k3d/deploy/kuma` (use `k3d/deploy/kumactl`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/debug.md')
    assert '2. Create a test namespace with sidecar injection: `kubectl label namespace <ns> kuma.io/sidecar-injection=enabled`' in text, "expected to find: " + '2. Create a test namespace with sidecar injection: `kubectl label namespace <ns> kuma.io/sidecar-injection=enabled`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/linting.md')
    assert '`make check` runs `check/rbac`: if any RBAC manifests in `deployments/` change (Role, RoleBinding, ClusterRole, ClusterRoleBinding), `UPGRADE.md` must also be updated.' in text, "expected to find: " + '`make check` runs `check/rbac`: if any RBAC manifests in `deployments/` change (Role, RoleBinding, ClusterRole, ClusterRoleBinding), `UPGRADE.md` must also be updated.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/linting.md')
    assert 'Use `tracing.SafeSpanEnd(span)` instead of `span.End()`. The `forbidigo` linter blocks direct `span.End()` calls to prevent panics during OTel init/shutdown.' in text, "expected to find: " + 'Use `tracing.SafeSpanEnd(span)` instead of `span.End()`. The `forbidigo` linter blocks direct `span.End()` calls to prevent panics during OTel init/shutdown.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/linting.md')
    assert '- `sigs.k8s.io/controller-runtime/pkg/log` → use `sigs.k8s.io/controller-runtime` (data race in init containers, see #13299)' in text, "expected to find: " + '- `sigs.k8s.io/controller-runtime/pkg/log` → use `sigs.k8s.io/controller-runtime` (data race in init containers, see #13299)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/policies.md')
    assert '`make generate` runs per policy: `policy-gen core-resource` → `k8s-resource` → `plugin-file` → `helpers` → `openapi`' in text, "expected to find: " + '`make generate` runs per policy: `policy-gen core-resource` → `k8s-resource` → `plugin-file` → `helpers` → `openapi`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/policies.md')
    assert '**Gotcha**: `tools/resource-gen` depends on `tools/policy-gen`, so modifying policy-gen forces resource-gen rebuild.' in text, "expected to find: " + '**Gotcha**: `tools/resource-gen` depends on `tools/policy-gen`, so modifying policy-gen forces resource-gen rebuild.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/policies.md')
    assert 'Policies live in `pkg/plugins/policies/` (MeshTrafficPermission, MeshHTTPRoute, MeshTimeout, etc.).' in text, "expected to find: " + 'Policies live in `pkg/plugins/policies/` (MeshTrafficPermission, MeshHTTPRoute, MeshTimeout, etc.).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert '- Update deps: `gh workflow run update-insecure-dependencies.yaml --repo kumahq/kuma` (runs daily 03:00 UTC)' in text, "expected to find: " + '- Update deps: `gh workflow run update-insecure-dependencies.yaml --repo kumahq/kuma` (runs daily 03:00 UTC)'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert '5. `gh workflow run release.yaml --repo kumahq/kuma --ref master -f version=X.Y.Z -f check=true`' in text, "expected to find: " + '5. `gh workflow run release.yaml --repo kumahq/kuma --ref master -f version=X.Y.Z -f check=true`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/release.md')
    assert '2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"` then `git push --no-verify upstream vX.Y.Z`' in text, "expected to find: " + '2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"` then `git push --no-verify upstream vX.Y.Z`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'Hand-written stubs only, no mockgen or counterfeiter. Implement the minimal interface in the test file itself.' in text, "expected to find: " + 'Hand-written stubs only, no mockgen or counterfeiter. Implement the minimal interface in the test file itself.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'Auto-load from testdata: `test.EntriesForFolder("testdata/folder")` scans for `.input.yaml` files.' in text, "expected to find: " + 'Auto-load from testdata: `test.EntriesForFolder("testdata/folder")` scans for `.input.yaml` files.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'builders.Dataplane().WithName("dp-1").WithMesh("default").WithAddress("127.0.0.1").Build()' in text, "expected to find: " + 'builders.Dataplane().WithName("dp-1").WithMesh("default").WithAddress("127.0.0.1").Build()'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Run `make generate` after changes to `.proto` files, `pkg/plugins/policies/*/api/` dirs, or resource definitions. Generated files: `zz_generated.*`, `*.pb.go`, `*.pb.validate.go`, `rest.yaml`' in text, "expected to find: " + 'Run `make generate` after changes to `.proto` files, `pkg/plugins/policies/*/api/` dirs, or resource definitions. Generated files: `zz_generated.*`, `*.pb.go`, `*.pb.validate.go`, `rest.yaml`'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Import aliases required**: `.golangci.yml` enforces `core_mesh`, `mesh_proto`, `core_model`, `common_api`, etc. See `.claude/rules/linting.md`' in text, "expected to find: " + '- **Import aliases required**: `.golangci.yml` enforces `core_mesh`, `mesh_proto`, `core_model`, `common_api`, etc. See `.claude/rules/linting.md`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Uses `mise` (config: `mise.toml`). Install via `make install`. Includes: buf, ginkgo, helm, kind, kubectl, protoc, golangci-lint, skaffold.' in text, "expected to find: " + 'Uses `mise` (config: `mise.toml`). Install via `make install`. Includes: buf, ginkgo, helm, kind, kubectl, protoc, golangci-lint, skaffold.'[:80]

