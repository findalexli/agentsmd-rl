"""
Task: beam-yaml-add-jinja-inheritance-example
Repo: apache/beam @ b9d48fa1750f6427cb86fa1de9d52e4d1849a433
PR:   37601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/beam"
JINJA_DIR = (
    Path(REPO)
    / "sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance"
)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — base pipeline with inheritance block
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_pipeline_has_inheritance_block():
    """Base pipeline YAML must define a {% block extra_steps %} injection point."""
    base = JINJA_DIR / "base" / "base_pipeline.yaml"
    assert base.exists(), "base/base_pipeline.yaml must exist"
    content = base.read_text()
    assert "{% block extra_steps %}" in content, \
        "Base pipeline must define {% block extra_steps %}"
    assert "{% endblock %}" in content, \
        "Base pipeline must close the block with {% endblock %}"
    # The base must define the pipeline chain structure
    assert "type: chain" in content, \
        "Base pipeline must use chain type"


# [pr_diff] fail_to_pass
def test_base_pipeline_has_core_transforms():
    """Base pipeline must have ReadFromText, MapToFields, Explode, WriteToText."""
    base = JINJA_DIR / "base" / "base_pipeline.yaml"
    content = base.read_text()
    for transform in ["ReadFromText", "MapToFields", "Explode", "WriteToText"]:
        assert transform in content, \
            f"Base pipeline must include {transform} transform"


# [pr_diff] fail_to_pass
def test_child_pipeline_extends_base():
    """Child pipeline must use {% extends %} to inherit from the base pipeline."""
    child = JINJA_DIR / "wordCountInheritance.yaml"
    assert child.exists(), "wordCountInheritance.yaml must exist"
    content = child.read_text()
    assert "{% extends" in content, \
        "Child pipeline must use {% extends %} directive"
    assert "base_pipeline.yaml" in content, \
        "Child pipeline must extend base_pipeline.yaml"


# [pr_diff] fail_to_pass
def test_child_injects_combine_into_block():
    """Child pipeline must override extra_steps block with a Combine transform."""
    child = JINJA_DIR / "wordCountInheritance.yaml"
    content = child.read_text()
    assert "{% block extra_steps %}" in content, \
        "Child must override the extra_steps block"
    assert "Combine" in content, \
        "Child must inject a Combine transform into the block"
    # Verify it configures group_by (not just an empty combine)
    assert "group_by" in content, \
        "Combine transform must specify group_by"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — test framework integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_preprocessor_registers_inheritance():
    """examples_test.py must register test_wordCountInheritance_yaml in the
    Jinja test preprocessor."""
    test_file = (
        Path(REPO)
        / "sdks/python/apache_beam/yaml/examples/testing/examples_test.py"
    )
    content = test_file.read_text()
    assert "test_wordCountInheritance_yaml" in content, \
        "examples_test.py must register the inheritance test"
    # It should appear near the other jinja tests (include, import)
    assert "test_wordCountInclude_yaml" in content, \
        "Include test must still be registered"
    assert "test_wordCountImport_yaml" in content, \
        "Import test must still be registered"


# [pr_diff] fail_to_pass
def test_input_data_returns_base_pipeline():
    """input_data.py must return the base pipeline path for the inheritance test."""
    input_data = (
        Path(REPO)
        / "sdks/python/apache_beam/yaml/examples/testing/input_data.py"
    )
    content = input_data.read_text()
    assert "test_wordCountInheritance_yaml" in content, \
        "input_data.py must handle the inheritance test name"
    assert "inheritance/base/base_pipeline.yaml" in content, \
        "input_data.py must reference the base pipeline template path"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — license compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
