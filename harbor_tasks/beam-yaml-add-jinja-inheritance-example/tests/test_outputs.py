"""
Task: beam-yaml-add-jinja-inheritance-example
Repo: apache/beam @ b9d48fa1750f6427cb86fa1de9d52e4d1849a433
PR:   37601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/beam"
JINJA_DIR = (
    Path(REPO)
    / "sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance"
)

# Ensure jinja2 is available (Dockerfile only installs pyyaml)
_r = subprocess.run(
    ["python3", "-c", "import jinja2"],
    capture_output=True,
)
if _r.returncode != 0:
    subprocess.run(
        ["python3", "-m", "pip", "install", "-q", "jinja2"],
        check=True, timeout=60,
    )


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo context."""
    script = Path("/tmp") / "_beam_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks that should pass on base commit
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_input_data_functions():
    """input_data.py functions return valid JSON and data structures (pass_to_pass)."""
    test_code = """
import sys
import types
import json

# Create a complete mock structure
class MockModule(types.ModuleType):
    def __getattr__(self, name):
        return MockModule(name)

# Mock out the entire apache_beam package tree
for mod_path in ['apache_beam', 'apache_beam.io', 'apache_beam.io.gcp', 'apache_beam.io.gcp.pubsub',
                 'apache_beam.yaml', 'apache_beam.yaml.examples', 'apache_beam.yaml.examples.testing']:
    sys.modules[mod_path] = MockModule(mod_path)

# Add PubsubMessage mock
class MockPubsubMessage:
    def __init__(self, data, attributes):
        self.data = data
        self.attributes = attributes
sys.modules['apache_beam.io.gcp.pubsub'].PubsubMessage = MockPubsubMessage

# Read and exec the input_data.py file directly
with open('/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/input_data.py') as f:
    source = f.read()

# Execute in a controlled namespace
namespace = {}
exec(source, namespace)

# Test word_count_jinja_parameter_data returns valid JSON
result = namespace['word_count_jinja_parameter_data']()
params = json.loads(result)
assert 'readFromTextTransform' in params, 'Missing readFromTextTransform'
assert 'combineTransform' in params, 'Missing combineTransform'
assert 'mapToFieldsSplitConfig' in params, 'Missing mapToFieldsSplitConfig'
print('word_count_jinja_parameter_data: OK')

# Test word_count_jinja_template_data returns valid paths
result = namespace['word_count_jinja_template_data']('test_wordCountInclude_yaml')
assert len(result) > 0, 'Empty template list for include'
assert all('.yaml' in p for p in result), 'All paths should be .yaml files'
print('word_count_jinja_template_data(include): OK')

result = namespace['word_count_jinja_template_data']('test_wordCountImport_yaml')
assert len(result) > 0, 'Empty template list for import'
assert 'wordCountMacros.yaml' in result[0], 'Should reference wordCountMacros.yaml'
print('word_count_jinja_template_data(import): OK')

# Test text_data returns expected content
result = namespace['text_data']()
assert 'KING LEAR' in result, 'Missing KING LEAR'
assert len(result.split('\\n')) >= 3, 'Should have multiple lines'
print('text_data: OK')

print('All input_data.py function tests passed!')
"""
    r = _run_python(test_code, timeout=60)
    assert r.returncode == 0, f"input_data.py function check failed:\n{r.stderr}"
    assert "All input_data.py function tests passed!" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_yamllint_jinja_include():
    """Jinja include YAML submodule files are processable by yamllint (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "yamllint"],
        capture_output=True, timeout=60,
    )
    yaml_files = [
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/readFromTextTransform.yaml",
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/mapToFieldsSplitConfig.yaml",
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/explodeTransform.yaml",
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/combineTransform.yaml",
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/writeToTextTransform.yaml",
        "sdks/python/apache_beam/yaml/examples/transforms/jinja/include/submodules/mapToFieldsCountConfig.yaml",
    ]
    for yaml_file in yaml_files:
        r = subprocess.run(
            ["yamllint", "-c", ".yamllint.yml", yaml_file],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        # These are Jinja template fragments which will have syntax issues due to
        # template syntax ({{ }}, {%- %}) - this is expected. We just verify
        # yamllint runs without crashing (stderr should be empty unless yamllint itself fails)
        assert r.stderr == "", f"yamllint crashed on {yaml_file}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yamllint_non_jinja():
    """Non-Jinja YAML files pass yamllint (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "yamllint"],
        capture_output=True, timeout=60,
    )
    # Check aggregation examples which are pure YAML (no Jinja syntax)
    r = subprocess.run(
        ["yamllint", "-c", ".yamllint.yml", "sdks/python/apache_beam/yaml/examples/transforms/aggregation/combine_sum_minimal.yaml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"yamllint failed:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_input_data():
    """Python syntax check passes for input_data.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "sdks/python/apache_beam/yaml/examples/testing/input_data.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed for input_data.py:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_examples_test():
    """Python syntax check passes for examples_test.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "sdks/python/apache_beam/yaml/examples/testing/examples_test.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed for examples_test.py:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yamllint_wordcount_minimal():
    """wordcount_minimal.yaml passes yamllint (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "yamllint"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["yamllint", "-c", ".yamllint.yml", "sdks/python/apache_beam/yaml/examples/wordcount_minimal.yaml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"yamllint failed for wordcount_minimal.yaml:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_init_examples():
    """Python syntax check passes for examples/__init__.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "sdks/python/apache_beam/yaml/examples/__init__.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed for examples/__init__.py:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_init_testing():
    """Python syntax check passes for testing/__init__.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "sdks/python/apache_beam/yaml/examples/testing/__init__.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed for testing/__init__.py:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yaml_syntax_aggregation():
    """Aggregation YAML files pass yamllint (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "yamllint"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["yamllint", "-c", ".yamllint.yml", "sdks/python/apache_beam/yaml/examples/transforms/aggregation/combine_count_minimal.yaml"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"yamllint failed for combine_count_minimal.yaml:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_jinja_template_syntax_include():
    """Jinja2 template syntax is valid for wordCountInclude.yaml (pass_to_pass)."""
    r = _run_python("""
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import sys

jinja_dir = '/workspace/beam/sdks/python/apache_beam/yaml/examples/transforms/jinja'
try:
    env = Environment(loader=FileSystemLoader(jinja_dir))
    template = env.get_template('include/wordCountInclude.yaml')
    # Successfully loading template validates syntax
    print("PASS")
except TemplateSyntaxError as e:
    print(f"Jinja syntax error: {e}")
    sys.exit(1)
""")
    assert r.returncode == 0, f"Jinja template syntax check failed for wordCountInclude.yaml:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_jinja_template_syntax_import():
    """Jinja2 template syntax is valid for wordCountImport.yaml (pass_to_pass)."""
    r = _run_python("""
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import sys

jinja_dir = '/workspace/beam/sdks/python/apache_beam/yaml/examples/transforms/jinja'
try:
    env = Environment(loader=FileSystemLoader(jinja_dir))
    template = env.get_template('import/wordCountImport.yaml')
    # Successfully loading template validates syntax
    print("PASS")
except TemplateSyntaxError as e:
    print(f"Jinja syntax error: {e}")
    sys.exit(1)
""")
    assert r.returncode == 0, f"Jinja template syntax check failed for wordCountImport.yaml:\n{r.stderr}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - Jinja2 template rendering
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_pipeline_renders_valid_yaml():
    """Base pipeline YAML renders via Jinja2 to valid YAML with core transforms."""
    r = _run_python("""
import yaml
from jinja2 import Environment, FileSystemLoader

base_dir = '/workspace/beam/sdks/python/apache_beam/yaml/examples/transforms/jinja/inheritance/base'
env = Environment(loader=FileSystemLoader(base_dir))
template = env.get_template('base_pipeline.yaml')

variables = {
    "readFromTextTransform": {"path": "/tmp/test_input.txt"},
    "mapToFieldsSplitConfig": {"language": "python", "fields": {"value": "1"}},
    "explodeTransform": {"fields": "word"},
    "mapToFieldsCountConfig": {"language": "python", "fields": {"output": "str(word)"}},
    "writeToTextTransform": {"path": "/tmp/test_output.txt"}
}
rendered = template.render(**variables)
data = yaml.safe_load(rendered)

assert data is not None, "Rendered YAML must not be None"
assert data['pipeline']['type'] == 'chain', "Pipeline must be chain type"
types = [t.get('type') for t in data['pipeline']['transforms']]
for expected in ['ReadFromText', 'MapToFields', 'Explode', 'WriteToText']:
    assert expected in types, f"Missing {expected} transform, got: {types}"
print("PASS")
""")
    assert r.returncode == 0, f"Base pipeline render failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_child_pipeline_renders_with_inheritance():
    """Child pipeline extends base and injects Combine via Jinja2 block override."""
    r = _run_python("""
import yaml
from jinja2 import Environment, FileSystemLoader

# Child uses {% extends \"apache_beam/.../base_pipeline.yaml\" %}
# so the loader must be rooted at sdks/python to resolve the path
sdk_python = '/workspace/beam/sdks/python'
env = Environment(loader=FileSystemLoader(sdk_python))
child_path = 'apache_beam/yaml/examples/transforms/jinja/inheritance/wordCountInheritance.yaml'
template = env.get_template(child_path)

variables = {
    "readFromTextTransform": {"path": "/tmp/test_input.txt"},
    "mapToFieldsSplitConfig": {"language": "python", "fields": {"value": "1"}},
    "explodeTransform": {"fields": "word"},
    "combineTransform": {"group_by": "word", "combine": {"value": "sum"}},
    "mapToFieldsCountConfig": {"language": "python", "fields": {"output": "str(word)"}},
    "writeToTextTransform": {"path": "/tmp/test_output.txt"}
}
rendered = template.render(**variables)
data = yaml.safe_load(rendered)

assert data is not None, "Rendered YAML must not be None"
types = [t.get('type') for t in data['pipeline']['transforms']]

# All base transforms must be present
for expected in ['ReadFromText', 'MapToFields', 'Explode', 'WriteToText']:
    assert expected in types, f"Missing base transform {expected}, got: {types}"

# Combine must be injected by the child's block override
assert 'Combine' in types, f"Combine must be injected by inheritance, got: {types}"

# Verify Combine has group_by configuration
combine = [t for t in data['pipeline']['transforms'] if t.get('type') == 'Combine'][0]
assert 'group_by' in combine.get('config', {}), "Combine must specify group_by"
print("PASS")
""")
    assert r.returncode == 0, f"Child pipeline render failed: {r.stderr}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - test framework integration
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_preprocessor_registers_inheritance():
    """examples_test.py registers test_wordCountInheritance_yaml in preprocessors."""
    r = _run_python("""
test_file = '/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/examples_test.py'
with open(test_file) as f:
    content = f.read()

count = content.count('test_wordCountInheritance_yaml')
assert count >= 3, (
    f"test_wordCountInheritance_yaml must appear >= 3 times "
    f"(wordcount preprocessor + io_write preprocessor + jinja preprocessor), found {count}"
)

# Existing jinja tests must still be registered
assert 'test_wordCountInclude_yaml' in content, "Include test must still exist"
assert 'test_wordCountImport_yaml' in content, "Import test must still exist"
print("PASS")
""")
    assert r.returncode == 0, f"Preprocessor check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_input_data_returns_base_pipeline():
    """input_data.py returns the base pipeline template path for inheritance test."""
    r = _run_python("""
import sys, types, importlib.util

# Mock apache_beam package tree so input_data.py can load in sparse checkout
for pkg in ['apache_beam', 'apache_beam.yaml', 'apache_beam.yaml.examples',
            'apache_beam.yaml.examples.testing']:
    sys.modules.setdefault(pkg, types.ModuleType(pkg))

spec = importlib.util.spec_from_file_location(
    "input_data",
    "/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/input_data.py"
)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception:
    # Sparse checkout may miss transitive imports; fall back to structural check
    with open("/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/input_data.py") as f:
        content = f.read()
    assert "test_wordCountInheritance_yaml" in content, "Must handle inheritance test name"
    assert "inheritance/base/base_pipeline.yaml" in content, "Must reference base pipeline"
    print("PASS")
    sys.exit(0)

result = mod.word_count_jinja_template_data('test_wordCountInheritance_yaml')
assert result, f"Expected non-empty list, got: {result}"
assert any('inheritance/base/base_pipeline.yaml' in p for p in result), (
    f"Must contain base_pipeline.yaml path, got: {result}"
)
print("PASS")
""")
    assert r.returncode == 0, f"Input data check failed: {r.stderr}"
    assert "PASS" in r.stdout
