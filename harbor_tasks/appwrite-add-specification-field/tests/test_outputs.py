#!/usr/bin/env python3
"""Tests for the appwrite PR #11536 fix."""

import subprocess
import json
import base64
from pathlib import Path
import tempfile
import os

REPO = Path("/workspace/appwrite")
PROJECTS_PHP = REPO / "app" / "config" / "collections" / "projects.php"


def _run_php_script(php_code):
    """Run PHP code from a temporary file to avoid escaping issues."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(php_code)
        temp_path = f.name
    
    try:
        result = subprocess.run(
            ["php", temp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result
    finally:
        os.unlink(temp_path)


def _extract_collection_attributes(content, collection_name):
    """Extract the attributes array for a given collection using PHP execution."""
    php_code = '''<?php
$content = ''' + repr(content) + ''';
$collection_name = ''' + repr(collection_name) + ''';
$pattern = "/ID::custom('" . preg_quote($collection_name, '/') . "').*?'attributes' => \\[(.*?)\\],\\s*'indexes'/s";
if (!preg_match($pattern, $content, $matches)) {
    echo json_encode(["error" => "Collection not found"]);
    exit;
}
$attrs_text = $matches[1];
$blocks = [];
$depth = 0;
$start = -1;
$len = strlen($attrs_text);
for ($i = 0; $i < $len; $i++) {
    if ($attrs_text[$i] == "[") {
        if ($depth == 0) {
            $start = $i;
        }
        $depth++;
    } else if ($attrs_text[$i] == "]") {
        $depth--;
        if ($depth == 0 && $start >= 0) {
            $blocks[] = substr($attrs_text, $start, $i - $start + 1);
        }
    }
}
echo json_encode(["blocks" => $blocks, "count" => count($blocks)]);
?>
'''
    result = _run_php_script(php_code)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse", "stdout": result.stdout, "stderr": result.stderr}


def _find_attribute_by_id(attr_blocks, attr_id):
    """Find an attribute by its ID within the extracted blocks."""
    for block in attr_blocks:
        if "ID::custom('" + attr_id + "')" in block:
            return block
    return None


def _extract_attribute_properties(attr_block):
    """Extract all key-value pairs from an attribute block."""
    php_code = '''<?php
$block = ''' + repr(attr_block) + ''';
$props = [];
if (preg_match("/'\\$id' => ID::custom\\('([^']+)'\\)/", $block, $m)) {
    $props["id"] = $m[1];
}
if (preg_match("/'type' => (Database::[A-Z_]+)/", $block, $m)) {
    $props["type"] = $m[1];
}
if (preg_match("/'size' => (\\d+)/", $block, $m)) {
    $props["size"] = (int)$m[1];
}
if (preg_match("/'signed' => (true|false)/", $block, $m)) {
    $props["signed"] = $m[1] === "true";
}
if (preg_match("/'required' => (true|false)/", $block, $m)) {
    $props["required"] = $m[1] === "true";
}
if (preg_match("/'array' => (true|false)/", $block, $m)) {
    $props["array"] = $m[1] === "true";
}
if (preg_match("/'format' => '([^']*)'/", $block, $m)) {
    $props["format"] = $m[1];
}
$props["has_specification_default"] = strpos($block, "APP_COMPUTE_SPECIFICATION_DEFAULT") !== false;
echo json_encode($props);
?>
'''
    result = _run_php_script(php_code)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {}


# ==================== Pass-to-Pass Tests ====================


def test_php_syntax_collections():
    """All collection PHP files have valid syntax."""
    collection_files = [
        REPO / "app" / "config" / "collections" / "common.php",
        REPO / "app" / "config" / "collections" / "databases.php",
        REPO / "app" / "config" / "collections" / "logs.php",
        REPO / "app" / "config" / "collections" / "platform.php",
        REPO / "app" / "config" / "collections" / "projects.php",
    ]
    for f in collection_files:
        result = subprocess.run(
            ["php", "-l", str(f)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PHP syntax error in {f}: {result.stderr}"


def test_php_syntax_projects_php():
    """Projects.php file has valid PHP syntax."""
    result = subprocess.run(
        ["php", "-l", str(PROJECTS_PHP)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


# ==================== Fail-to-Pass Tests ====================


def test_functions_has_specification_field():
    """Verify functions collection has specification attribute."""
    content = PROJECTS_PHP.read_text()

    result = _extract_collection_attributes(content, "functions")
    assert "error" not in result, f"Could not find functions collection: {result.get('error')}"

    blocks = result.get("blocks", [])
    assert len(blocks) > 0, "No attribute blocks found in functions collection"

    spec_block = _find_attribute_by_id(blocks, "specification")
    assert spec_block is not None, "Missing specification field in functions collection"

    props = _extract_attribute_properties(spec_block)
    assert props.get("type") == "Database::VAR_STRING", \
        f"specification should have VAR_STRING type, got {props.get('type')}"
    assert props.get("has_specification_default") is True, \
        "specification should use APP_COMPUTE_SPECIFICATION_DEFAULT"


def test_sites_has_specification_field():
    """Verify sites collection has specification attribute."""
    content = PROJECTS_PHP.read_text()

    result = _extract_collection_attributes(content, "sites")
    assert "error" not in result, f"Could not find sites collection: {result.get('error')}"

    blocks = result.get("blocks", [])
    assert len(blocks) > 0, "No attribute blocks found in sites collection"

    spec_block = _find_attribute_by_id(blocks, "specification")
    assert spec_block is not None, "Missing specification field in sites collection"

    props = _extract_attribute_properties(spec_block)
    assert props.get("type") == "Database::VAR_STRING", \
        f"specification should have VAR_STRING type, got {props.get('type')}"
    assert props.get("has_specification_default") is True, \
        "specification should use APP_COMPUTE_SPECIFICATION_DEFAULT"


def test_specification_field_properties():
    """Verify the specification field has correct properties in both collections."""
    content = PROJECTS_PHP.read_text()

    for coll_name in ["functions", "sites"]:
        result = _extract_collection_attributes(content, coll_name)
        assert "error" not in result, f"Could not find {coll_name} collection: {result.get('error')}"

        blocks = result.get("blocks", [])
        spec_block = _find_attribute_by_id(blocks, "specification")
        assert spec_block is not None, f"Missing specification field in {coll_name} collection"

        props = _extract_attribute_properties(spec_block)

        assert props.get("size") == 128, \
            f"specification field in {coll_name} should have size=128, got {props.get('size')}"
        assert props.get("signed") is False, \
            f"specification field in {coll_name} should have signed=false, got {props.get('signed')}"
        assert props.get("required") is False, \
            f"specification field in {coll_name} should have required=false, got {props.get('required')}"
        assert props.get("array") is False, \
            f"specification field in {coll_name} should have array=false, got {props.get('array')}"
        assert props.get("format") == "", \
            f"specification field in {coll_name} should have empty format, got '{props.get('format')}'"


def test_functions_specification_before_buildspecification():
    """Verify that in functions collection, specification comes before buildSpecification."""
    content = PROJECTS_PHP.read_text()

    result = _extract_collection_attributes(content, "functions")
    assert "error" not in result, f"Could not find functions collection: {result.get('error')}"

    blocks = result.get("blocks", [])

    spec_index = None
    build_index = None

    for i, block in enumerate(blocks):
        if "ID::custom('specification')" in block:
            spec_index = i
        if "ID::custom('buildSpecification')" in block:
            build_index = i

    assert spec_index is not None, "specification field not found in functions"
    assert build_index is not None, "buildSpecification field not found in functions"
    assert spec_index < build_index, \
        f"specification should come before buildSpecification in functions (found at {spec_index} vs {build_index})"


def test_sites_specification_before_buildspecification():
    """Verify that in sites collection, specification comes before buildSpecification."""
    content = PROJECTS_PHP.read_text()

    result = _extract_collection_attributes(content, "sites")
    assert "error" not in result, f"Could not find sites collection: {result.get('error')}"

    blocks = result.get("blocks", [])

    spec_index = None
    build_index = None

    for i, block in enumerate(blocks):
        if "ID::custom('specification')" in block:
            spec_index = i
        if "ID::custom('buildSpecification')" in block:
            build_index = i

    assert spec_index is not None, "specification field not found in sites"
    assert build_index is not None, "buildSpecification field not found in sites"
    assert spec_index < build_index, \
        f"specification should come before buildSpecification in sites (found at {spec_index} vs {build_index})"
