"""Tests for pulumi/pulumi#22360 - Fix flaky TestPropertyValueSchema/serialized"""

import json
import subprocess
import sys
import jsonschema

REPO = "/workspace/pulumi"
PKG_DIR = f"{REPO}/pkg"
SCHEMA_PATH = f"{REPO}/sdk/go/common/apitype/property-values.json"
TEST_FILE_PATH = f"{REPO}/pkg/resource/stack/deployment_test.go"


def test_json_schema_validates_float_object():
    """Fail-to-pass: JSON schema must accept serialized float objects (NaN/Inf)."""
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    # Build a lookup: find any oneOf entry that could be a float type
    # by checking for the float signature property key
    float_sig_key = '4dabf18193072939515e22adb298388d'
    float_schema = None
    for entry in schema.get('oneOf', []):
        props = entry.get('properties', {})
        if float_sig_key in props:
            float_schema = entry
            break

    assert float_schema is not None, (
        "No schema entry with float signature property found in oneOf"
    )

    # Validate structure: must have value property with string type and hex pattern
    value_prop = float_schema.get('properties', {}).get('value', {})
    assert value_prop.get('type') == 'string', "Float value property must be string type"
    assert 'pattern' in value_prop or value_prop.get('pattern') == '^[0-9a-f]{16}$', (
        "Float value property must have hex pattern"
    )

    # Verify required fields
    required = float_schema.get('required', [])
    assert float_sig_key in required, "Float signature must be required"
    assert 'value' in required, "value must be required"

    # Validate actual sample float objects against the schema
    sample_floats = [
        {
            float_sig_key: '8ad145fe-0d11-4827-bfd7-1abcbf086f5c',
            'value': '7ff8000000000001',  # NaN
        },
        {
            float_sig_key: '8ad145fe-0d11-4827-bfd7-1abcbf086f5c',
            'value': '7ff0000000000000',  # +Inf
        },
        {
            float_sig_key: '8ad145fe-0d11-4827-bfd7-1abcbf086f5c',
            'value': 'fff0000000000000',  # -Inf
        },
    ]

    # The schema entry itself (without $schema ref) can be used to validate
    for sample in sample_floats:
        try:
            jsonschema.validate(sample, float_schema)
        except jsonschema.ValidationError as e:
            assert False, f"Sample {sample} failed schema validation: {e.message}"


def test_test_property_value_schema_passes():
    """Fail-to-pass: TestPropertyValueSchema/serialized subtest must pass reliably."""
    # Run the specific test multiple times to verify it's not flaky
    for i in range(5):
        result = subprocess.run(
            ['go', 'test', '-run', 'TestPropertyValueSchema/serialized', './resource/stack/...',
             '-count=1', '-tags', 'all'],
            cwd=PKG_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, (
            f"TestPropertyValueSchema/serialized failed on run {i+1}:\n"
            f"stdout: {result.stdout[-1000:]}\n"
            f"stderr: {result.stderr[-1000:]}"
        )


def test_go_build_passes():
    """Pass-to-pass: Go code should compile."""
    result = subprocess.run(
        ['go', 'build', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_go_vet_passes():
    """Pass-to-pass: go vet should pass."""
    result = subprocess.run(
        ['go', 'vet', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_json_schema_is_valid():
    """Pass-to-pass: JSON schema file must be valid JSON."""
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    assert '$schema' in schema or 'oneOf' in schema or 'type' in schema, "Schema missing root structure"
    assert 'oneOf' in schema, "Schema missing oneOf array"


def test_pkg_unit_tests_pass():
    """Pass-to-pass: Unit tests in pkg/resource/stack pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-count=1', '-tags', 'all', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_gofmt_pkg_passes():
    """Pass-to-pass: Go formatting check passes for pkg/ (repo CI)."""
    result = subprocess.run(
        ['gofmt', '-l', './resource/stack/'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )
    # gofmt -l returns list of files with formatting issues; empty output means no issues
    assert result.returncode == 0, f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", f"Files need formatting:\n{result.stdout}"


def test_checkpoint_tests_pass():
    """Pass-to-pass: Checkpoint tests in resource/stack pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-run', 'TestCheckpoint', '-count=1', '-tags', 'all', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Checkpoint tests failed:\n{result.stderr[-1000:]}"


def test_serialize_property_value_tests_pass():
    """Pass-to-pass: SerializePropertyValue tests pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-run', 'TestSerializePropertyValue', '-count=1', '-tags', 'all', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"SerializePropertyValue tests failed:\n{result.stderr[-1000:]}"


def test_deserialize_property_value_tests_pass():
    """Pass-to-pass: DeserializePropertyValue tests pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-run', 'TestDeserializePropertyValue', '-count=1', '-tags', 'all', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"DeserializePropertyValue tests failed:\n{result.stderr[-1000:]}"


def test_round_trip_property_value_tests_pass():
    """Pass-to-pass: RoundTripPropertyValue tests pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-run', 'TestRoundTripPropertyValue', '-count=1', '-tags', 'all', './resource/stack/...'],
        cwd=PKG_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"RoundTripPropertyValue tests failed:\n{result.stderr[-1000:]}"


def test_sdk_apitype_tests_pass():
    """Pass-to-pass: SDK apitype tests pass (repo CI)."""
    result = subprocess.run(
        ['go', 'test', '-count=1', '-tags', 'all', './go/common/apitype/...'],
        cwd=f"{REPO}/sdk",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"SDK apitype tests failed:\n{result.stderr[-1000:]}"
