"""
Task: transformers-config-classvar-rope-validation
Repo: huggingface/transformers @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
PR:   #44943

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/transformers"
sys.path.insert(0, f"{REPO}/src")


def _run_python(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_python_file(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python code from a temp file (needed when inspect.getsource is required)."""
    fd, path = tempfile.mkstemp(suffix=".py", dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["python3", path],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/modeling_rope_utils.py",
        "src/transformers/utils/auto_docstring.py",
        "utils/check_config_attributes.py",
    ]
    for f in files:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests (subprocess-based)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_rope_empty_dict_no_crash():
    """validate_rope must handle empty rope_parameters dict without crashing or mutating."""
    r = _run_python("""
import sys
sys.path.insert(0, "/workspace/transformers/src")
from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

validate_rope = RotaryEmbeddingConfigMixin.validate_rope

class Config:
    def __init__(self):
        self.rope_parameters = {}
        self.layer_types = None

config = Config()
validate_rope(config)
assert config.rope_parameters == {}, f"rope_parameters mutated from {{}} to {dict(config.rope_parameters)}"
print("PASS")
""")
    assert r.returncode == 0, f"validate_rope crashed on empty dict: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_validate_rope_empty_dict_multiple_configs():
    """validate_rope handles empty dict on multiple sequential configs."""
    r = _run_python("""
import sys
sys.path.insert(0, "/workspace/transformers/src")
from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

validate_rope = RotaryEmbeddingConfigMixin.validate_rope

for i in range(5):
    class Cfg:
        def __init__(self):
            self.rope_parameters = {}
            self.layer_types = None

    c = Cfg()
    validate_rope(c)
    assert c.rope_parameters == {}, f"Iteration {i}: empty rope_parameters should remain empty"

print("PASS")
""")
    assert r.returncode == 0, f"validate_rope failed on multiple configs: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_transformers_version_not_classvar():
    """transformers_version must be an instance field, not ClassVar, with per-instance isolation."""
    r = _run_python("""
import sys, dataclasses
sys.path.insert(0, "/workspace/transformers/src")
from transformers.configuration_utils import PreTrainedConfig

field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
assert "transformers_version" in field_names, (
    "transformers_version not in dataclasses.fields() -- still ClassVar?"
)

c1 = PreTrainedConfig()
c2 = PreTrainedConfig()
c1.transformers_version = "1.0.0"
c2.transformers_version = "2.0.0"
assert c1.transformers_version == "1.0.0", "transformers_version leaked across instances"
assert c2.transformers_version == "2.0.0", "transformers_version leaked across instances"
print("PASS")
""")
    assert r.returncode == 0, f"transformers_version ClassVar check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_architectures_not_classvar():
    """architectures must be an instance field, not ClassVar, with per-instance isolation."""
    r = _run_python("""
import sys, dataclasses
sys.path.insert(0, "/workspace/transformers/src")
from transformers.configuration_utils import PreTrainedConfig

field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
assert "architectures" in field_names, (
    "architectures not in dataclasses.fields() -- still ClassVar?"
)

c1 = PreTrainedConfig()
c2 = PreTrainedConfig()
c1.architectures = ["BertForMaskedLM"]
c2.architectures = ["GPT2LMHeadModel", "GPT2ForSequenceClassification"]
assert c1.architectures == ["BertForMaskedLM"], "architectures leaked across instances"
assert c2.architectures == ["GPT2LMHeadModel", "GPT2ForSequenceClassification"], (
    "architectures leaked across instances"
)
print("PASS")
""")
    assert r.returncode == 0, f"architectures ClassVar check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_auto_docstring_parameter_filtering():
    """Docstring generation must support filtering to exclude specific parameters."""
    r = _run_python_file("""
import sys, inspect, io
sys.path.insert(0, "/workspace/transformers/src")
from transformers.utils.auto_docstring import auto_method_docstring

# Dynamically discover any filtering parameter on auto_method_docstring
sig = inspect.signature(auto_method_docstring)
known_params = {'func', 'parent_class', 'custom_intro', 'custom_args', 'checkpoint', 'source_args_dict'}
filter_param = None
for name in sig.parameters:
    if name not in known_params:
        filter_param = name
        break

assert filter_param is not None, (
    "auto_method_docstring should accept a filtering parameter beyond standard args"
)

# Create a mock class with a method having multiple parameters
class MockConfig:
    def __init__(self, alpha: int = 0, beta: str = "x", gamma: float = 1.0):
        pass

# Capture stdout where undocumented-parameter warnings are printed
old_stdout = sys.stdout
sys.stdout = captured = io.StringIO()
auto_method_docstring(
    MockConfig.__init__,
    parent_class=MockConfig,
    **{filter_param: {"alpha", "gamma"}},
)
output = captured.getvalue()
sys.stdout = old_stdout

# With filter={alpha, gamma}, only those params should be processed
# (producing warnings about being undocumented); beta must be filtered out
assert "alpha" in output, "alpha must be processed when in filter set"
assert "gamma" in output, "gamma must be processed when in filter set"
assert "beta" not in output, "beta must be excluded when not in filter set"
print("PASS")
""")
    assert r.returncode == 0, f"auto_docstring parameter filtering failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_auto_docstring_filtering_behavior():
    """Parameter filtering correctly includes/excludes based on filter set."""
    r = _run_python_file("""
import sys, inspect, io
sys.path.insert(0, "/workspace/transformers/src")
from transformers.utils.auto_docstring import auto_method_docstring

# Dynamically discover the filtering parameter
sig = inspect.signature(auto_method_docstring)
known_params = {'func', 'parent_class', 'custom_intro', 'custom_args', 'checkpoint', 'source_args_dict'}
filter_param = None
for name in sig.parameters:
    if name not in known_params:
        filter_param = name
        break

assert filter_param is not None, (
    "auto_method_docstring should accept a filtering parameter"
)

class MockConfig:
    def __init__(self, alpha: int = 0, beta: str = "x", gamma: float = 1.0):
        pass

# Test 1: With filter = {alpha, gamma}, beta should be excluded
old_stdout = sys.stdout
sys.stdout = cap1 = io.StringIO()
auto_method_docstring(
    MockConfig.__init__, parent_class=MockConfig,
    **{filter_param: {"alpha", "gamma"}},
)
out1 = cap1.getvalue()
sys.stdout = old_stdout
assert "alpha" in out1, "alpha must be processed when in filter"
assert "gamma" in out1, "gamma must be processed when in filter"
assert "beta" not in out1, "beta must be excluded when not in filter"

# Test 2: Without filter, all params should be processed
sys.stdout = cap2 = io.StringIO()
auto_method_docstring(
    MockConfig.__init__, parent_class=MockConfig,
)
out2 = cap2.getvalue()
sys.stdout = old_stdout
assert "alpha" in out2, "alpha must be processed without filter"
assert "beta" in out2, "beta must be processed without filter"
assert "gamma" in out2, "gamma must be processed without filter"

# Test 3: With empty filter set, no params should be processed
sys.stdout = cap3 = io.StringIO()
auto_method_docstring(
    MockConfig.__init__, parent_class=MockConfig,
    **{filter_param: set()},
)
out3 = cap3.getvalue()
sys.stdout = old_stdout
assert "alpha" not in out3, "alpha should not be processed with empty filter"
assert "beta" not in out3, "beta should not be processed with empty filter"
assert "gamma" not in out3, "gamma should not be processed with empty filter"

print("PASS")
""")
    assert r.returncode == 0, f"auto_docstring filtering behavior test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_validate_rope_none_still_works():
    """validate_rope must still return cleanly when rope_parameters is None."""
    from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

    validate_rope = RotaryEmbeddingConfigMixin.validate_rope

    class Config:
        def __init__(self):
            self.rope_parameters = None

    validate_rope(Config())


# [pr_diff] pass_to_pass
def test_validate_rope_dispatches_for_real_config():
    """validate_rope must still validate non-empty rope configs (anti-stub)."""
    from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

    validate_rope = RotaryEmbeddingConfigMixin.validate_rope

    class Config:
        dispatch_count = 0

        def __init__(self):
            self.rope_parameters = {"rope_type": "test_dispatch", "factor": 1.0}
            self.layer_types = None
            self.ignore_keys_at_rope_validation = set()

        def _validate_test_dispatch_rope_parameters(self, params, ignore_keys=None):
            Config.dispatch_count += 1

    config = Config()
    validate_rope(config)
    assert Config.dispatch_count > 0, (
        "Validation function was never dispatched -- validate_rope may be stubbed"
    )


# [repo_tests] fail_to_pass
def test_upstream_config_kwargs_complete():
    """After fix, transformers_version is instance-level and appears in missing keys."""
    r = _run_python("""
import sys, ast
from pathlib import Path
sys.path.insert(0, "/workspace/transformers/src")
from transformers import PreTrainedConfig

# Behavioral check 1: transformers_version must be an instance attribute
config = PreTrainedConfig()
assert "transformers_version" in config.__dict__, (
    "transformers_version must be an instance attribute (present in __dict__)"
)

# Behavioral check 2: compute what the repo test checks -- keys in __dict__
# but not in config_common_kwargs. transformers_version must appear in missing
# keys because it's now an instance-level field that was previously ClassVar.
source = Path("/workspace/transformers/tests/utils/test_configuration_utils.py").read_text()
tree = ast.parse(source)
config_common_kwargs = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "config_common_kwargs":
                config_common_kwargs = ast.literal_eval(node.value)
                break
assert config_common_kwargs is not None, "config_common_kwargs not found in test file"

# transformers_version must be in __dict__ but NOT in config_common_kwargs
# (it's a per-instance field, not a common kwarg)
assert "transformers_version" not in config_common_kwargs, (
    "transformers_version should not be in config_common_kwargs"
)

# Therefore it must appear in the computed missing keys
missing_keys = set(config.__dict__.keys()) - set(config_common_kwargs.keys())
assert "transformers_version" in missing_keys, (
    "transformers_version must be in missing keys (present in __dict__ but absent from config_common_kwargs)"
)
print("PASS")
""")
    assert r.returncode == 0, f"config kwargs complete check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass -- repo CI ruff format check
def test_ruff_format_clean():
    """Changed files must be properly formatted (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-m", "ruff", "format",
            "src/transformers/configuration_utils.py",
            "src/transformers/modeling_rope_utils.py",
            "src/transformers/utils/auto_docstring.py",
            "utils/check_config_attributes.py",
            "--check",
            "--quiet",
        ],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff format issues:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass -- repo CI import checks
def test_transformers_imports():
    """Core transformers modules must import without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import sys; sys.path.insert(0, '/workspace/transformers/src'); "
         "from transformers.configuration_utils import PreTrainedConfig; "
         "from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin; "
         "from transformers.utils.auto_docstring import auto_method_docstring; "
         "print('All imports successful')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "All imports successful" in r.stdout


# [repo_tests] pass_to_pass -- all modified files pass ruff format check
def test_ruff_format_all_modified():
    """All modified Python files must pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-m", "ruff", "format",
            "src/transformers/configuration_utils.py",
            "src/transformers/modeling_rope_utils.py",
            "src/transformers/utils/auto_docstring.py",
            "tests/utils/test_configuration_utils.py",
            "utils/check_config_attributes.py",
            "--check",
            "--quiet",
        ],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass -- all modified files pass ruff lint check
def test_ruff_lint_all_modified():
    """All modified Python files must pass ruff lint check (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-m", "ruff", "check",
            "src/transformers/configuration_utils.py",
            "src/transformers/modeling_rope_utils.py",
            "src/transformers/utils/auto_docstring.py",
            "tests/utils/test_configuration_utils.py",
            "utils/check_config_attributes.py",
            "--select", "E,W,F",
            "--ignore", "E501",
            "--quiet",
        ],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff lint check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass -- syntax check on all modified files
def test_syntax_all_modified():
    """All modified Python files must have valid syntax (pass_to_pass)."""
    import py_compile

    files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/modeling_rope_utils.py",
        "src/transformers/utils/auto_docstring.py",
        "tests/utils/test_configuration_utils.py",
        "utils/check_config_attributes.py",
    ]
    for f in files:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from CLAUDE.md / .ai/skills/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass -- CLAUDE.md:5 @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
def test_check_config_attributes_allowlist():
    """ATTRIBUTES_TO_ALLOW must include transformers_version and architectures."""
    r = _run_python("""
import sys, runpy
sys.path.insert(0, "/workspace/transformers/src")

# Execute the module and inspect the runtime value of ATTRIBUTES_TO_ALLOW
mod = runpy.run_path("/workspace/transformers/utils/check_config_attributes.py")
allowlist = mod["ATTRIBUTES_TO_ALLOW"]

assert "transformers_version" in allowlist, (
    "transformers_version missing from ATTRIBUTES_TO_ALLOW"
)
assert "architectures" in allowlist, (
    "architectures missing from ATTRIBUTES_TO_ALLOW"
)
print("PASS")
""")
    assert r.returncode == 0, f"check_config_attributes allowlist test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] pass_to_pass -- CLAUDE.md:2 @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
def test_ruff_lint_clean():
    """Changed files must pass ruff lint."""
    r = subprocess.run(
        [
            "python3", "-m", "ruff", "check",
            "src/transformers/configuration_utils.py",
            "src/transformers/modeling_rope_utils.py",
            "src/transformers/utils/auto_docstring.py",
            "utils/check_config_attributes.py",
            "--select", "E,W",
            "--ignore", "E501",
            "--quiet",
        ],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff issues:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [agent_config] pass_to_pass -- .ai/skills/add-or-fix-type-checking/SKILL.md:180-186
def test_no_bare_type_ignore():
    """# type: ignore comments must include specific error codes, not bare."""
    import re

    changed_files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/modeling_rope_utils.py",
        "src/transformers/utils/auto_docstring.py",
    ]
    bare_pattern = re.compile(r"#\s*type:\s*ignore\s*$", re.MULTILINE)


# [repo_tests] pass_to_pass -- rope module basic functionality
def test_repo_rope_basic_functionality():
    """RotaryEmbeddingConfigMixin module loads and basic operations work (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")
from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin
assert hasattr(RotaryEmbeddingConfigMixin, "validate_rope"), "validate_rope method missing"
class TestCfg:
    rope_parameters = None
    layer_types = None
RotaryEmbeddingConfigMixin.validate_rope(TestCfg())
print("RoPE basic functionality: OK")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"RoPE basic functionality test failed:\n{r.stderr}"
    assert "RoPE basic functionality: OK" in r.stdout


# [repo_tests] pass_to_pass -- validate rope with None (baseline behavior)
def test_repo_rope_validate_none():
    """RoPE validation handles None rope_parameters gracefully (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, "/workspace/transformers/src")
from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin
class TestCfg:
    rope_parameters = None
    layer_types = None
RotaryEmbeddingConfigMixin.validate_rope(TestCfg())
print("RoPE None validation: OK")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"RoPE None validation failed:\n{r.stderr}"
    assert "RoPE None validation: OK" in r.stdout
