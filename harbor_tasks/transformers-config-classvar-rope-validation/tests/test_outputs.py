"""
Task: transformers-config-classvar-rope-validation
Repo: huggingface/transformers @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
PR:   #44943

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"
sys.path.insert(0, f"{REPO}/src")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_rope_empty_dict_no_crash():
    """validate_rope must handle empty rope_parameters dict without crashing or mutating."""
    from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

    validate_rope = RotaryEmbeddingConfigMixin.validate_rope

    class Config:
        def __init__(self):
            self.rope_parameters = {}
            self.layer_types = None

    config = Config()
    validate_rope(config)
    assert config.rope_parameters == {}, (
        f"rope_parameters mutated from {{}} to {dict(config.rope_parameters)}"
    )


# [pr_diff] fail_to_pass
def test_validate_rope_empty_dict_multiple_configs():
    """validate_rope handles empty dict on multiple sequential configs."""
    from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

    validate_rope = RotaryEmbeddingConfigMixin.validate_rope

    # Test with multiple independent configs to catch state leaks
    for i in range(5):
        class Cfg:
            def __init__(self):
                self.rope_parameters = {}
                self.layer_types = None

        c = Cfg()
        validate_rope(c)
        assert c.rope_parameters == {}, f"Iteration {i}: empty rope_parameters should remain empty"


# [pr_diff] fail_to_pass
def test_transformers_version_not_classvar():
    """transformers_version must be an instance field, not ClassVar."""
    import dataclasses
    from transformers.configuration_utils import PreTrainedConfig

    field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
    assert "transformers_version" in field_names, (
        "transformers_version not in dataclasses.fields() — still ClassVar?"
    )
    # Verify per-instance isolation: two configs can hold different values
    c1 = PreTrainedConfig()
    c2 = PreTrainedConfig()
    c1.transformers_version = "1.0.0"
    c2.transformers_version = "2.0.0"
    assert c1.transformers_version == "1.0.0", "transformers_version leaked across instances"
    assert c2.transformers_version == "2.0.0", "transformers_version leaked across instances"


# [pr_diff] fail_to_pass
def test_architectures_not_classvar():
    """architectures must be an instance field, not ClassVar."""
    import dataclasses
    from transformers.configuration_utils import PreTrainedConfig

    field_names = [f.name for f in dataclasses.fields(PreTrainedConfig)]
    assert "architectures" in field_names, (
        "architectures not in dataclasses.fields() — still ClassVar?"
    )
    # Verify per-instance isolation with diverse values
    c1 = PreTrainedConfig()
    c2 = PreTrainedConfig()
    c1.architectures = ["BertForMaskedLM"]
    c2.architectures = ["GPT2LMHeadModel", "GPT2ForSequenceClassification"]
    assert c1.architectures == ["BertForMaskedLM"], "architectures leaked across instances"
    assert c2.architectures == ["GPT2LMHeadModel", "GPT2ForSequenceClassification"], (
        "architectures leaked across instances"
    )


# [pr_diff] fail_to_pass
def test_auto_docstring_parameter_filtering():
    """_process_regular_parameters, _process_parameters_section, and auto_method_docstring accept allowed_params."""
    import inspect
    from transformers.utils.auto_docstring import (
        _process_regular_parameters,
        _process_parameters_section,
        auto_method_docstring,
    )

    for fn in [_process_regular_parameters, _process_parameters_section, auto_method_docstring]:
        assert "allowed_params" in inspect.signature(fn).parameters, (
            f"{fn.__name__} missing 'allowed_params' parameter"
        )


# [pr_diff] fail_to_pass
def test_auto_docstring_filtering_behavior():
    """allowed_params actually filters out parameters not in the set."""
    import inspect
    from transformers.utils.auto_docstring import _process_regular_parameters

    # Create a function with three named params
    def mock_init(self, alpha: int = 0, beta: str = "x", gamma: float = 1.0):
        pass

    sig = inspect.signature(mock_init)

    # _process_regular_parameters returns undocumented params as missing_args
    # when documented_params is empty. With allowed_params filtering, 'beta'
    # should NOT appear in the missing_args dict.
    _, missing_filtered = _process_regular_parameters(
        sig, mock_init, "MockConfig", {}, 2, [], {}, None,
        allowed_params={"alpha", "gamma"},
    )

    assert "beta" not in missing_filtered, (
        f"'beta' should be filtered out but found in missing_args: {list(missing_filtered.keys())}"
    )
    assert "alpha" in missing_filtered, (
        f"'alpha' should be in missing_args but not found: {list(missing_filtered.keys())}"
    )
    assert "gamma" in missing_filtered, (
        f"'gamma' should be in missing_args but not found: {list(missing_filtered.keys())}"
    )

    # Without allowed_params, all three should appear
    _, missing_all = _process_regular_parameters(
        sig, mock_init, "MockConfig", {}, 2, [], {}, None,
    )
    assert "alpha" in missing_all and "beta" in missing_all and "gamma" in missing_all, (
        f"Without allowed_params, all params should appear. Got: {list(missing_all.keys())}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_validate_rope_none_still_works():
    """validate_rope must still return cleanly when rope_parameters is None."""
    from transformers.modeling_rope_utils import RotaryEmbeddingConfigMixin

    validate_rope = RotaryEmbeddingConfigMixin.validate_rope

    class Config:
        def __init__(self):
            self.rope_parameters = None

    # Should not raise for None
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
        "Validation function was never dispatched — validate_rope may be stubbed"
    )


# [repo_tests] pass_to_pass
def test_upstream_config_kwargs_complete():
    """Upstream test_config_common_kwargs_is_complete logic must pass."""
    import ast as _ast
    from transformers import PreTrainedConfig

    # config_common_kwargs is defined as a dict literal in tests/utils/test_configuration_utils.py.
    # Extract it via AST to avoid import side-effects and relative-import issues.
    source = Path(f"{REPO}/tests/utils/test_configuration_utils.py").read_text()
    tree = _ast.parse(source)
    config_common_kwargs = None
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            for target in node.targets:
                if isinstance(target, _ast.Name) and target.id == "config_common_kwargs":
                    config_common_kwargs = _ast.literal_eval(node.value)
                    break
    assert config_common_kwargs is not None, "config_common_kwargs not found"

    base_config = PreTrainedConfig()
    missing_keys = [key for key in base_config.__dict__ if key not in config_common_kwargs]

    # After the fix, transformers_version is an instance field and appears
    # in __dict__, so the expected list must include it.
    expected = [
        "transformers_version",
        "is_encoder_decoder",
        "tokenizer_class",
        "_name_or_path",
        "_commit_hash",
        "_output_attentions",
        "_attn_implementation_internal",
        "_experts_implementation_internal",
    ]
    assert missing_keys == expected, (
        f"config_common_kwargs completeness check failed.\n"
        f"  Expected missing: {expected}\n"
        f"  Got missing:      {missing_keys}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / .ai/skills/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:5 @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
def test_check_config_attributes_allowlist():
    """ATTRIBUTES_TO_ALLOW must include transformers_version and architectures."""
    # AST-only because: check_config_attributes.py is a standalone lint script with heavy imports
    import ast

    src = Path(f"{REPO}/utils/check_config_attributes.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ATTRIBUTES_TO_ALLOW":
                    vals = [
                        elt.value for elt in node.value.elts
                        if isinstance(elt, ast.Constant)
                    ]
                    assert "transformers_version" in vals, (
                        "transformers_version missing from ATTRIBUTES_TO_ALLOW"
                    )
                    assert "architectures" in vals, (
                        "architectures missing from ATTRIBUTES_TO_ALLOW"
                    )
                    return
    raise AssertionError("ATTRIBUTES_TO_ALLOW not found in check_config_attributes.py")


# [agent_config] pass_to_pass — CLAUDE.md:2 @ eb3d67aaafe368863afc77e4b60fa60c2077c8b5
def test_ruff_lint_clean():
    """Changed files must pass ruff lint (make style)."""
    # All changed files have pre-existing E501 violations. Check E/W rules
    # except E501 (line length) which is not enforced in this repo's ruff config.
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


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:180-186
def test_no_bare_type_ignore():
    """# type: ignore comments must include specific error codes, not bare."""
    import re

    changed_files = [
        "src/transformers/configuration_utils.py",
        "src/transformers/modeling_rope_utils.py",
        "src/transformers/utils/auto_docstring.py",
    ]
    bare_pattern = re.compile(r"#\s*type:\s*ignore\s*$", re.MULTILINE)
    for f in changed_files:
        content = Path(f"{REPO}/{f}").read_text()
        matches = bare_pattern.findall(content)
        assert not matches, (
            f"{f} has bare '# type: ignore' without error code — use '# type: ignore[code]'"
        )
