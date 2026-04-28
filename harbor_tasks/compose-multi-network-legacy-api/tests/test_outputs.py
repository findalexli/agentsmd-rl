"""Benchmark tests for docker/compose#13629.

f2p tests: verify the multi-network < API-1.44 fallback is implemented.
p2p tests: pre-existing pkg/compose suite + repo-wide build/vet/gofmt still pass.
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/compose"
INJECTED_TEST = Path(REPO) / "pkg" / "compose" / "legacy_api_test.go"
GO_TEST_TIMEOUT = 300

# Go test fixture — package-private symbols force the test to live inside
# pkg/compose. Held as a string here so /workspace/task/tests/ contains only
# the harness files. Written into the repo by an autouse pytest fixture.
LEGACY_API_TEST_GO = r'''/*
   Benchmark task test file (injected at test time).
*/

package compose

import (
	"context"
	"fmt"
	"testing"

	"github.com/compose-spec/compose-go/v2/types"
	"github.com/docker/cli/cli/config/configfile"
	"github.com/moby/moby/api/types/container"
	"github.com/moby/moby/api/types/network"
	"github.com/moby/moby/client"
	"go.uber.org/mock/gomock"
	"gotest.tools/v3/assert"
	"gotest.tools/v3/assert/cmp"

	"github.com/docker/compose/v5/pkg/mocks"
)

// TestDefaultNetworkSettings_BelowAPI144 ensures that for daemons running an
// API older than 1.44, defaultNetworkSettings returns only the primary network
// in EndpointsConfig (extra networks must be connected post-create).
func TestDefaultNetworkSettings_BelowAPI144(t *testing.T) {
	service := types.ServiceConfig{
		Name: "myService",
		Networks: map[string]*types.ServiceNetworkConfig{
			"myNetwork1": {Priority: 10},
			"myNetwork2": {Priority: 1000},
		},
	}
	project := types.Project{
		Name:     "myProject",
		Services: types.Services{"myService": service},
		Networks: types.Networks(map[string]types.NetworkConfig{
			"myNetwork1": {Name: "myProject_myNetwork1"},
			"myNetwork2": {Name: "myProject_myNetwork2"},
		}),
	}

	networkMode, networkConfig, err := defaultNetworkSettings(&project, service, 1, nil, true, "1.43")
	assert.NilError(t, err)
	assert.Equal(t, string(networkMode), "myProject_myNetwork2")
	assert.Check(t, cmp.Len(networkConfig.EndpointsConfig, 1))
	assert.Check(t, cmp.Contains(networkConfig.EndpointsConfig, "myProject_myNetwork2"))
}

// TestDefaultNetworkSettings_AtAPI144 ensures the API >= 1.44 path still
// includes every network in EndpointsConfig (regression guard for the gating).
func TestDefaultNetworkSettings_AtAPI144(t *testing.T) {
	service := types.ServiceConfig{
		Name: "myService",
		Networks: map[string]*types.ServiceNetworkConfig{
			"myNetwork1": {Priority: 10},
			"myNetwork2": {Priority: 1000},
		},
	}
	project := types.Project{
		Name:     "myProject",
		Services: types.Services{"myService": service},
		Networks: types.Networks(map[string]types.NetworkConfig{
			"myNetwork1": {Name: "myProject_myNetwork1"},
			"myNetwork2": {Name: "myProject_myNetwork2"},
		}),
	}

	_, networkConfig, err := defaultNetworkSettings(&project, service, 1, nil, true, "1.44")
	assert.NilError(t, err)
	assert.Check(t, cmp.Len(networkConfig.EndpointsConfig, 2))
	assert.Check(t, cmp.Contains(networkConfig.EndpointsConfig, "myProject_myNetwork1"))
	assert.Check(t, cmp.Contains(networkConfig.EndpointsConfig, "myProject_myNetwork2"))
}

// TestCreateMobyContainerLegacyAPI verifies that on API < 1.44, createMobyContainer:
//   - sends only the primary network in ContainerCreate's EndpointsConfig
//   - calls NetworkConnect for each extra network
//   - issues ContainerInspect AFTER NetworkConnect (so the result reflects all attached networks)
func TestCreateMobyContainerLegacyAPI(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()
	apiClient := mocks.NewMockAPIClient(mockCtrl)
	cli := mocks.NewMockCli(mockCtrl)
	tested, err := NewComposeService(cli)
	assert.NilError(t, err)
	cli.EXPECT().Client().Return(apiClient).AnyTimes()
	cli.EXPECT().ConfigFile().Return(&configfile.ConfigFile{}).AnyTimes()
	apiClient.EXPECT().DaemonHost().Return("").AnyTimes()
	apiClient.EXPECT().ImageInspect(anyCancellableContext(), gomock.Any()).
		Return(client.ImageInspectResult{}, nil).AnyTimes()

	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.43"}, nil).AnyTimes()
	apiClient.EXPECT().ClientVersion().Return("1.43").AnyTimes()

	service := types.ServiceConfig{
		Name: "test",
		Networks: map[string]*types.ServiceNetworkConfig{
			"a": {Priority: 10},
			"b": {Priority: 100},
		},
	}
	project := types.Project{
		Name: "bork",
		Services: types.Services{
			"test": service,
		},
		Networks: types.Networks{
			"a": types.NetworkConfig{Name: "a-moby-name"},
			"b": types.NetworkConfig{Name: "b-moby-name"},
		},
	}

	var gotCreate client.ContainerCreateOptions
	apiClient.EXPECT().ContainerCreate(gomock.Any(), gomock.Any()).
		DoAndReturn(func(_ context.Context, opts client.ContainerCreateOptions) (client.ContainerCreateResult, error) {
			gotCreate = opts
			return client.ContainerCreateResult{ID: "an-id"}, nil
		})

	var gotConnect client.NetworkConnectOptions
	connectCall := apiClient.EXPECT().
		NetworkConnect(gomock.Any(), gomock.Eq("a-moby-name"), gomock.Any()).
		DoAndReturn(func(_ context.Context, _ string, opts client.NetworkConnectOptions) (client.NetworkConnectResult, error) {
			gotConnect = opts
			return client.NetworkConnectResult{}, nil
		})

	apiClient.EXPECT().ContainerInspect(gomock.Any(), gomock.Eq("an-id"), gomock.Any()).
		Times(1).After(connectCall).Return(client.ContainerInspectResult{
		Container: container.InspectResponse{
			ID:     "an-id",
			Name:   "a-name",
			Config: &container.Config{},
			NetworkSettings: &container.NetworkSettings{
				Networks: map[string]*network.EndpointSettings{
					"b-moby-name": {
						IPAMConfig: &network.EndpointIPAMConfig{},
						Aliases:    []string{"bork-test-0"},
					},
					"a-moby-name": {
						IPAMConfig: &network.EndpointIPAMConfig{},
						Aliases:    []string{"bork-test-0"},
					},
				},
			},
		},
	}, nil)

	_, err = tested.(*composeService).createMobyContainer(t.Context(), &project, service, "test", 0, nil, createOptions{
		Labels:            make(types.Labels),
		UseNetworkAliases: true,
	})
	assert.NilError(t, err)

	assert.Check(t, gotCreate.NetworkingConfig != nil)
	assert.Equal(t, len(gotCreate.NetworkingConfig.EndpointsConfig), 1)
	_, hasPrimary := gotCreate.NetworkingConfig.EndpointsConfig["b-moby-name"]
	assert.Check(t, hasPrimary, "primary network b-moby-name should be in ContainerCreate EndpointsConfig")

	assert.Equal(t, gotConnect.Container, "an-id")
	assert.Check(t, gotConnect.EndpointConfig != nil)
}

// TestCreateMobyContainerLegacyAPI_NetworkConnectFailure verifies that when
// the post-create NetworkConnect fails, the orphan container is removed via
// ContainerRemove(Force=true) and the error is propagated.
func TestCreateMobyContainerLegacyAPI_NetworkConnectFailure(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()
	apiClient := mocks.NewMockAPIClient(mockCtrl)
	cli := mocks.NewMockCli(mockCtrl)
	tested, err := NewComposeService(cli)
	assert.NilError(t, err)
	cli.EXPECT().Client().Return(apiClient).AnyTimes()
	cli.EXPECT().ConfigFile().Return(&configfile.ConfigFile{}).AnyTimes()
	apiClient.EXPECT().DaemonHost().Return("").AnyTimes()
	apiClient.EXPECT().ImageInspect(anyCancellableContext(), gomock.Any()).
		Return(client.ImageInspectResult{}, nil).AnyTimes()

	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.43"}, nil).AnyTimes()
	apiClient.EXPECT().ClientVersion().Return("1.43").AnyTimes()

	service := types.ServiceConfig{
		Name: "test",
		Networks: map[string]*types.ServiceNetworkConfig{
			"a": {Priority: 10},
			"b": {Priority: 100},
		},
	}
	project := types.Project{
		Name: "bork",
		Services: types.Services{
			"test": service,
		},
		Networks: types.Networks{
			"a": types.NetworkConfig{Name: "a-moby-name"},
			"b": types.NetworkConfig{Name: "b-moby-name"},
		},
	}

	apiClient.EXPECT().ContainerCreate(gomock.Any(), gomock.Any()).
		Return(client.ContainerCreateResult{ID: "an-id"}, nil)

	connectErr := fmt.Errorf("network connect failed")
	apiClient.EXPECT().NetworkConnect(gomock.Any(), gomock.Eq("a-moby-name"), gomock.Any()).
		Return(client.NetworkConnectResult{}, connectErr)

	apiClient.EXPECT().ContainerRemove(gomock.Any(), gomock.Eq("an-id"), gomock.Any()).
		DoAndReturn(func(_ context.Context, _ string, opts client.ContainerRemoveOptions) (client.ContainerRemoveResult, error) {
			assert.Check(t, opts.Force, "ContainerRemove should use Force")
			return client.ContainerRemoveResult{}, nil
		})

	_, err = tested.(*composeService).createMobyContainer(t.Context(), &project, service, "test", 0, nil, createOptions{
		Labels:            make(types.Labels),
		UseNetworkAliases: true,
	})
	assert.ErrorContains(t, err, "network connect failed")
}
'''


@pytest.fixture(scope="session", autouse=True)
def install_legacy_api_test():
    """Inject the legacy-API Go test file into pkg/compose before tests run."""
    INJECTED_TEST.write_text(LEGACY_API_TEST_GO)
    yield
    try:
        INJECTED_TEST.unlink()
    except FileNotFoundError:
        pass


def _go_test(run_pattern: str, timeout: int = GO_TEST_TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["go", "test", "-count=1", "-timeout", "120s", "-run", run_pattern, "-v",
         "./pkg/compose/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "GOFLAGS": "-mod=mod", "CGO_ENABLED": "0"},
    )


# ---------- fail-to-pass (the bug fix) ----------

def test_below_api_144_default_settings():
    """defaultNetworkSettings on API < 1.44 returns only the primary network."""
    r = _go_test("^TestDefaultNetworkSettings_BelowAPI144$")
    assert r.returncode == 0, (
        f"TestDefaultNetworkSettings_BelowAPI144 failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )
    assert "--- PASS: TestDefaultNetworkSettings_BelowAPI144" in r.stdout, r.stdout[-1500:]


def test_legacy_api_create_uses_network_connect():
    """createMobyContainer on API < 1.44 calls NetworkConnect for extra networks."""
    r = _go_test("^TestCreateMobyContainerLegacyAPI$")
    assert r.returncode == 0, (
        f"TestCreateMobyContainerLegacyAPI failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )
    assert "--- PASS: TestCreateMobyContainerLegacyAPI" in r.stdout, r.stdout[-1500:]


def test_legacy_api_network_connect_failure_cleans_up():
    """If NetworkConnect fails post-create, the orphan container is removed."""
    r = _go_test("^TestCreateMobyContainerLegacyAPI_NetworkConnectFailure$")
    assert r.returncode == 0, (
        f"TestCreateMobyContainerLegacyAPI_NetworkConnectFailure failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )
    assert "--- PASS: TestCreateMobyContainerLegacyAPI_NetworkConnectFailure" in r.stdout, r.stdout[-1500:]


# ---------- pass-to-pass (regression guards) ----------

def test_at_api_144_default_settings_unchanged():
    """defaultNetworkSettings on API >= 1.44 still includes every network."""
    r = _go_test("^TestDefaultNetworkSettings_AtAPI144$")
    assert r.returncode == 0, (
        f"TestDefaultNetworkSettings_AtAPI144 failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_existing_default_network_settings_subtests():
    """The four pre-existing TestDefaultNetworkSettings sub-tests still pass."""
    r = _go_test("^TestDefaultNetworkSettings$")
    assert r.returncode == 0, (
        f"TestDefaultNetworkSettings failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_existing_create_moby_container():
    """The pre-existing TestCreateMobyContainer (API >= 1.44 path) still passes."""
    r = _go_test("^TestCreateMobyContainer$")
    assert r.returncode == 0, (
        f"TestCreateMobyContainer failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_pkg_compose_full_suite_excluding_injected():
    """All other pkg/compose tests (excluding the injected legacy-API tests) still pass."""
    skip_pattern = (
        "^TestDefaultNetworkSettings_BelowAPI144$|"
        "^TestDefaultNetworkSettings_AtAPI144$|"
        "^TestCreateMobyContainerLegacyAPI$|"
        "^TestCreateMobyContainerLegacyAPI_NetworkConnectFailure$"
    )
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "300s",
         "-skip", skip_pattern, "./pkg/compose/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=GO_TEST_TIMEOUT,
        env={**os.environ, "GOFLAGS": "-mod=mod", "CGO_ENABLED": "0"},
    )
    assert r.returncode == 0, (
        f"pkg/compose suite (excluding injected) failed:\n"
        f"STDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1500:]}"
    )


def test_repo_builds():
    """The whole module builds (go build ./...)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=GO_TEST_TIMEOUT,
        env={**os.environ, "GOFLAGS": "-mod=mod", "CGO_ENABLED": "0"},
    )
    assert r.returncode == 0, (
        f"go build ./... failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_repo_govet():
    """go vet ./pkg/... reports no issues."""
    r = subprocess.run(
        ["go", "vet", "./pkg/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=GO_TEST_TIMEOUT,
        env={**os.environ, "GOFLAGS": "-mod=mod", "CGO_ENABLED": "0"},
    )
    assert r.returncode == 0, (
        f"go vet ./pkg/... failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_gofmt_clean():
    """gofmt -l reports no unformatted files in pkg/compose (style enforced by repo)."""
    r = subprocess.run(
        ["gofmt", "-l", "pkg/compose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0 and r.stdout.strip() == "", (
        f"gofmt found unformatted files:\n{r.stdout}\n{r.stderr}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_check_docker_version():
    """fail_to_pass | CI job 'e2e' → step 'Check Docker Version'"""
    r = subprocess.run(
        ["bash", "-lc", 'docker --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Docker Version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_build_example_provider():
    """fail_to_pass | CI job 'e2e' → step 'Build example provider'"""
    r = subprocess.run(
        ["bash", "-lc", 'make example-provider'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build example provider' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_test_plugin_mode():
    """fail_to_pass | CI job 'e2e' → step 'Test plugin mode'"""
    r = subprocess.run(
        ["bash", "-lc", 'make e2e-compose GOCOVERDIR=bin/coverage/e2e TEST_FLAGS="-v"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test plugin mode' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_test_standalone_mode():
    """fail_to_pass | CI job 'e2e' → step 'Test standalone mode'"""
    r = subprocess.run(
        ["bash", "-lc", 'make e2e-compose-standalone'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test standalone mode' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")