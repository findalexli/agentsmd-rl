"""
Task: efcore-autostart-cosmos-emulator-via-testcontainers
Repo: dotnet/efcore @ dd9da572feeb9851a0c4a6579b05163c48574c29
PR:   37999

Replace explicit Docker scripts for the Cosmos emulator with automatic
Testcontainers.CosmosDb lifecycle management. Also update the agent skill
file to reflect the new approach.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/efcore"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python validation code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified C# files are present and non-empty."""
    files = [
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs",
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs",
        "test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must have substantial content"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_testenvironment_initialize_async_logic():
    """TestEnvironment.cs has InitializeAsync with 3-path logic (configured->probe->testcontainer)."""
    r = _run_py("""
import re

src = open('test/EFCore.Cosmos.FunctionalTests/TestUtilities/TestEnvironment.cs').read()

# Method exists with correct signature
assert 'public static async Task InitializeAsync()' in src, \\
    'Must define public static async Task InitializeAsync()'

# Path 1: use configured connection if set
assert re.search(r'IsNullOrEmpty\\(configured\\)', src), \\
    'Path 1: must check IsNullOrEmpty for configured connection'

# Path 2: probe for already-running emulator
assert 'TryProbeEmulatorAsync' in src, \\
    'Path 2: must define TryProbeEmulatorAsync'
assert re.search(r'await.*TryProbeEmulatorAsync.*ConfigureAwait', src), \\
    'Path 2: must await TryProbeEmulatorAsync with ConfigureAwait'

# Path 3: start testcontainer as fallback
assert 'CosmosDbBuilder' in src, 'Path 3: must use CosmosDbBuilder'
assert 'StartAsync' in src, 'Path 3: must call StartAsync on container'

# Thread-safe init guard
assert '_initSemaphore' in src, 'Must use semaphore for thread-safe initialization'

# ConfigureAwait(false) throughout async calls
assert '.ConfigureAwait(false)' in src, 'Async calls must use ConfigureAwait(false)'

# DefaultConnection is now mutable (private set) so init can update it
assert 'private set' in src, 'DefaultConnection must be mutable (private set)'

print('PASS')
""")
    assert r.returncode == 0, f"InitializeAsync validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cosmos_config_default_connection_null():
    """cosmosConfig.json DefaultConnection must be null (not hardcoded URL)."""
    r = _run_py("""
import json

data = json.load(open('test/EFCore.Cosmos.FunctionalTests/cosmosConfig.json'))
conn = data['Test']['Cosmos']['DefaultConnection']
assert conn is None, f'DefaultConnection should be null, got {conn!r}'

# AuthToken must still be present (not accidentally removed)
assert data['Test']['Cosmos'].get('AuthToken') is not None, \\
    'AuthToken must still be present'

print('PASS')
""")
    assert r.returncode == 0, f"Config validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docker_scripts_removed():
    """The old Docker startup scripts must be removed."""
    r = _run_py("""
from pathlib import Path

ps1 = Path('eng/testing/run-cosmos-container.ps1')
sh = Path('eng/testing/run-cosmos-container.sh')

assert not ps1.exists(), f'{ps1} should be deleted'
assert not sh.exists(), f'{sh} should be deleted'

print('PASS')
""")
    assert r.returncode == 0, f"Script removal check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_testcontainers_package_referenced():
    """Testcontainers.CosmosDb must be added as a package dependency."""
    r = _run_py("""
import xml.etree.ElementTree as ET

# Directory.Packages.props must declare the version
props_tree = ET.parse('test/Directory.Packages.props')
props_root = props_tree.getroot()
found = False
for elem in props_root.iter():
    if elem.text and 'Testcontainers.CosmosDb' in elem.text:
        found = True
        break
assert found, 'Directory.Packages.props must declare Testcontainers.CosmosDb version'

# csproj must have a PackageReference
csproj = open('test/EFCore.Cosmos.FunctionalTests/EFCore.Cosmos.FunctionalTests.csproj').read()
assert 'Testcontainers.CosmosDb' in csproj, \\
    'csproj must reference Testcontainers.CosmosDb'
assert '<PackageReference Include="Testcontainers.CosmosDb"' in csproj, \\
    'csproj must have correct PackageReference syntax'

print('PASS')
""")
    assert r.returncode == 0, f"Package reference check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cosmosteststore_mutable_and_calls_initialize():
    """CosmosTestStore has mutable connection properties and calls TestEnvironment.InitializeAsync."""
    r = _run_py("""
import re

src = open('test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosTestStore.cs').read()

# ConnectionUri and ConnectionString must be mutable (private set)
assert 'public string ConnectionUri { get; private set; }' in src, \\
    'ConnectionUri must have private setter'
assert 'public string ConnectionString { get; private set; }' in src, \\
    'ConnectionString must have private setter'

# Must call TestEnvironment.InitializeAsync
assert 'TestEnvironment.InitializeAsync()' in src, \\
    'Must call TestEnvironment.InitializeAsync()'

# Must update connection details after init
assert 'ConnectionUri = TestEnvironment.DefaultConnection' in src, \\
    'Must update ConnectionUri from TestEnvironment'
assert 'ConnectionString = TestEnvironment.ConnectionString' in src, \\
    'Must update ConnectionString from TestEnvironment'

# Must use ConfigureAwait(false)
assert re.search(r'InitializeAsync.*ConfigureAwait\\(false\\)', src), \\
    'Must use ConfigureAwait(false) on InitializeAsync call'

print('PASS')
""")
    assert r.returncode == 0, f"CosmosTestStore validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_options_builder_uses_http_handler():
    """CosmosDbContextOptionsBuilderExtensions uses TestEnvironment.HttpMessageHandler."""
    r = _run_py("""
src = open('test/EFCore.Cosmos.FunctionalTests/TestUtilities/CosmosDbContextOptionsBuilderExtensions.cs').read()

# Must reference TestEnvironment.HttpMessageHandler
assert 'TestEnvironment.HttpMessageHandler' in src, \\
    'Must use TestEnvironment.HttpMessageHandler'

# Must have HttpClientFactory pattern
assert 'HttpClientFactory' in src, 'Must set HttpClientFactory'

# Must still have fallback cert validation
assert 'DangerousAcceptAnyServerCertificateValidator' in src, \\
    'Must accept self-signed certs as fallback'

print('PASS')
""")
    assert r.returncode == 0, f"Options builder validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_helix_simplified():
    """helix.proj no longer references old Docker scripts in PreCommands."""
    r = _run_py("""
src = open('eng/helix.proj').read()

# Old script references must be gone
assert 'run-cosmos-container.sh' not in src, \\
    'helix.proj must not reference run-cosmos-container.sh'
assert 'run-cosmos-container.ps1' not in src, \\
    'helix.proj must not reference run-cosmos-container.ps1'

# Old Docker cleanup commands removed
assert 'docker stop cosmos-emulator' not in src, \\
    'Old docker stop command must be removed'
assert 'docker rm -f cosmos-emulator' not in src, \\
    'Old docker rm command must be removed'

# CosmosTests must still be referenced
assert 'CosmosTests' in src, 'Must still reference CosmosTests'

print('PASS')
""")
    assert r.returncode == 0, f"helix.proj validation failed: {r.stderr}"
    assert "PASS" in r.stdout
