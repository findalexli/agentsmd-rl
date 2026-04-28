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
        assert r.stderr == "", f"yamllint crashed on {yaml_file}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yamllint_non_jinja():
    """Non-Jinja YAML files pass yamllint (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "yamllint"],
        capture_output=True, timeout=60,
    )
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

for expected in ['ReadFromText', 'MapToFields', 'Explode', 'WriteToText']:
    assert expected in types, f"Missing base transform {expected}, got: {types}"

assert 'Combine' in types, f"Combine must be injected by inheritance, got: {types}"

combine = [t for t in data['pipeline']['transforms'] if t.get('type') == 'Combine'][0]
assert 'group_by' in combine.get('config', {}), "Combine must specify group_by"
print("PASS")
""")
    assert r.returncode == 0, f"Child pipeline render failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_preprocessor_registers_inheritance():
    """examples_test.py registers the inheritance test in preprocessors (at least 3 times)."""
    r = _run_python("""
import sys, types, re

for pkg in ['apache_beam', 'apache_beam.yaml', 'apache_beam.yaml.examples', 'apache_beam.yaml.examples.testing']:
    sys.modules.setdefault(pkg, types.ModuleType(pkg))

try:
    from importlib import util
    spec = util.spec_from_file_location(
        "examples_test",
        "/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/examples_test.py"
    )
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    preprocessors = [
        name for name in dir(mod)
        if 'preprocessor' in name.lower() or 'jinja' in name.lower()
    ]

    found = False
    for prep_name in preprocessors:
        prep = getattr(mod, prep_name)
        if callable(prep):
            try:
                result = prep()
                if result and any('Inheritance' in str(r) or 'inheritance' in str(r) for r in result):
                    found = True
                    break
            except:
                pass

    if not found:
        with open("/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/examples_test.py") as f:
            content = f.read()
        matches = re.findall(r'test_\\w*[Ii]nheritance_yaml', content)
        assert len(matches) >= 3, (
            f"Inheritance test identifier must appear >= 3 times in preprocessors, found {len(matches)}"
        )
    print("PASS")
except Exception as e:
    with open("/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/examples_test.py") as f:
        content = f.read()
    matches = re.findall(r'test_\\w*[Ii]nheritance_yaml', content)
    assert len(matches) >= 3, (
        f"Inheritance test identifier must appear >= 3 times in preprocessors, found {len(matches)}"
    )
    print("PASS")
""")
    assert r.returncode == 0, f"Preprocessor check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_input_data_returns_base_pipeline():
    """input_data.py template data functions work for the inheritance test."""
    r = _run_python("""
import sys, types, json
from importlib import util

for pkg in ['apache_beam', 'apache_beam.yaml', 'apache_beam.yaml.examples',
            'apache_beam.yaml.examples.testing']:
    sys.modules.setdefault(pkg, types.ModuleType(pkg))

spec = util.spec_from_file_location(
    "input_data",
    "/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/input_data.py"
)
mod = util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception:
    with open("/workspace/beam/sdks/python/apache_beam/yaml/examples/testing/input_data.py") as f:
        content = f.read()
    assert "test_wordCountInheritance_yaml" in content, "Must handle inheritance test name"
    assert "inheritance/base/base_pipeline.yaml" in content, "Must reference base pipeline"
    print("PASS")
    sys.exit(0)

result = mod.word_count_jinja_template_data('test_wordCountInheritance_yaml')
assert result, f"Expected non-empty list for inheritance test, got: {result}"
assert any('inheritance/base/base_pipeline.yaml' in p for p in result), (
    f"Must contain base_pipeline.yaml path, got: {result}"
)

param_result = mod.word_count_jinja_parameter_data()
params = json.loads(param_result)
required_keys = ['readFromTextTransform', 'combineTransform', 'mapToFieldsSplitConfig']
for key in required_keys:
    assert key in params, f"Parameter data must include '{key}'"

print("PASS")
""")
    assert r.returncode == 0, f"Input data check failed: {r.stderr}"
    assert "PASS" in r.stdout

# === CI-mined test (scoped to YAML examples, uses real test runner) ===
def test_ci_jinja_yaml_template_validation():
    """CI-scoped: run pytest on Jinja YAML template validation (pass_to_pass)."""
    import shutil
    sdk_python = str(Path(REPO) / "sdks" / "python")
    test_file = Path("/tmp") / "test_jinja_validation_ci.py"
    test_file.write_text(r'''
import os, sys
import yaml
import pytest
from jinja2 import Environment, FileSystemLoader

SDK = r"""''' + sdk_python + r'''"""

TEMPLATE_VARS = {
    "readFromTextTransform": {"path": "/tmp/test.txt"},
    "mapToFieldsSplitConfig": {"language": "python", "fields": {"value": "1"}},
    "explodeTransform": {"fields": "word"},
    "combineTransform": {"group_by": "word", "combine": {"value": "sum"}},
    "mapToFieldsCountConfig": {"language": "python", "fields": {"output": "str(word)"}},
    "writeToTextTransform": {"path": "/tmp/out.txt"},
}

def test_include_template_renders():
    """Include template renders to valid YAML with core transforms."""
    env = Environment(loader=FileSystemLoader(SDK))
    template = env.get_template(
        "apache_beam/yaml/examples/transforms/jinja/include/wordCountInclude.yaml")
    rendered = template.render(**TEMPLATE_VARS)
    data = yaml.safe_load(rendered)
    assert data is not None, "Rendered YAML must not be None"
    types = [t.get("type") for t in data["pipeline"]["transforms"]]
    for expected in ["ReadFromText", "MapToFields", "Explode", "Combine",
                       "WriteToText"]:
        assert expected in types, f"Missing {expected} transform, got: {types}"

def test_import_template_renders():
    """Import template renders to valid YAML with core transforms."""
    env = Environment(loader=FileSystemLoader(SDK))
    template = env.get_template(
        "apache_beam/yaml/examples/transforms/jinja/import/wordCountImport.yaml")
    rendered = template.render(**TEMPLATE_VARS)
    data = yaml.safe_load(rendered)
    assert data is not None, "Rendered YAML must not be None"
    types = [t.get("type") for t in data["pipeline"]["transforms"]]
    for expected in ["ReadFromText", "MapToFields", "Explode", "Combine",
                       "WriteToText"]:
        assert expected in types, f"Missing {expected} transform, got: {types}"

def test_inheritance_template_if_present():
    """If inheritance example exists, it must render to valid YAML with Combine."""
    child = os.path.join(
        SDK,
        "apache_beam/yaml/examples/transforms/jinja/inheritance/"
        "wordCountInheritance.yaml")
    if not os.path.exists(child):
        pytest.skip("Inheritance example not yet created")
    env = Environment(loader=FileSystemLoader(SDK))
    template = env.get_template(
        "apache_beam/yaml/examples/transforms/jinja/inheritance/"
        "wordCountInheritance.yaml")
    rendered = template.render(**TEMPLATE_VARS)
    data = yaml.safe_load(rendered)
    assert data is not None, "Rendered YAML must not be None"
    types = [t.get("type") for t in data["pipeline"]["transforms"]]
    for expected in ["ReadFromText", "MapToFields", "Explode", "WriteToText"]:
        assert expected in types, f"Missing base {expected}, got: {types}"
    assert "Combine" in types, (
        f"Combine must be injected by inheritance, got: {types}")
''')
    r = subprocess.run(
        ["bash", "-lc",
         f"cd {REPO} && python3 -m pytest {test_file} -xvs --tb=short 2>&1"],
        capture_output=True, text=True, timeout=120,
    )
    try:
        test_file.unlink()
    except OSError:
        pass
    if r.returncode != 0:
        raise AssertionError(
            f"CI Jinja validation failed (rc={r.returncode}):\n"
            f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
        )