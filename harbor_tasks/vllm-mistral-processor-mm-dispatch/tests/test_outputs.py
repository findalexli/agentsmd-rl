"""
Task: vllm-mistral-processor-mm-dispatch
Repo: vllm-project/vllm @ 43cc5138e5145752413235a2a8aa303886077327
PR:   #38410

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/repo"

PIXTRAL_PROC = f"{REPO}/vllm/transformers_utils/processors/pixtral.py"
VOXTRAL_PROC = f"{REPO}/vllm/transformers_utils/processors/voxtral.py"
PIXTRAL_MODEL = f"{REPO}/vllm/model_executor/models/pixtral.py"
VOXTRAL_MODEL = f"{REPO}/vllm/model_executor/models/voxtral.py"
MODIFIED_FILES = [PIXTRAL_PROC, VOXTRAL_PROC, PIXTRAL_MODEL, VOXTRAL_MODEL]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo environment via subprocess."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (static / pr_diff)
# ---------------------------------------------------------------------------


def test_syntax_check():
    """All 4 modified files must parse without syntax errors."""
    for path in MODIFIED_FILES:
        src = Path(path).read_text()
        ast.parse(src)


def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_spdx_headers():
    """Modified files have SPDX license headers (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "regex", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/check_spdx_header.py"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stderr}"


def test_repo_forbidden_imports():
    """Modified files have no forbidden imports (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "regex", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/check_forbidden_imports.py", PIXTRAL_PROC, VOXTRAL_PROC],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Forbidden imports check failed:\n{r.stderr}"


def test_repo_mypy():
    """Repo's mypy type checker passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "mypy", "regex", "pydantic", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/mypy.py", "0", "3.10"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"mypy check failed:\n{r.stderr[-500:]}"


def test_repo_typos():
    """Repo's typos check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["typos"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_torch_cuda_check():
    """Repo's torch.cuda API check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "regex", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "tools/pre_commit/check_torch_cuda.py"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Torch CUDA check failed:\n{r.stderr}"


def test_repo_check_init_lazy_imports():
    """Repo's init lazy imports check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python", "tools/pre_commit/check_init_lazy_imports.py"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Init lazy imports check failed:\n{r.stderr}"


def test_repo_boolean_context_manager():
    """Repo's boolean context manager check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python", "tools/pre_commit/check_boolean_context_manager.py"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Boolean context manager check failed:\n{r.stderr}"


def test_repo_validate_config():
    """Repo's config validation check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python", "tools/pre_commit/validate_config.py"] + MODIFIED_FILES,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Config validation check failed:\n{r.stderr}"


def test_get_hf_processor_preserved():
    """get_hf_processor must exist in both pixtral and voxtral model files."""
    for path in [PIXTRAL_MODEL, VOXTRAL_MODEL]:
        source = Path(path).read_text()
        tree = ast.parse(source)
        found = any(
            isinstance(node, ast.FunctionDef) and node.name == "get_hf_processor"
            for node in ast.walk(tree)
        )
        assert found, f"{path} missing get_hf_processor"


def test_not_stub():
    """Modified files must not be trivially small (>= 50 lines each)."""
    for path in MODIFIED_FILES:
        lines = len(Path(path).read_text().splitlines())
        assert lines >= 50, f"{path} too short ({lines} lines) -- likely a stub"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral subprocess tests
#
# These verify actual code behavior via AST extraction + exec in a mock
# environment, run as subprocess. The modules import heavy deps (torch,
# mistral_common, transformers CUDA internals) so direct import is impossible;
# we extract the relevant methods and test them in isolation.
# ---------------------------------------------------------------------------


def _sig_check_code(proc_file: str, class_name: str, param_name: str) -> str:
    """Build subprocess script: verify constructor has a named parameter."""
    return (
        "import ast, inspect, textwrap\n"
        "from pathlib import Path\n"
        "\n"
        f"source = Path('{proc_file}').read_text()\n"
        "tree = ast.parse(source)\n"
        "lines = source.splitlines(keepends=True)\n"
        "\n"
        f"class_name = '{class_name}'\n"
        f"param_name = '{param_name}'\n"
        "\n"
        "for node in ast.walk(tree):\n"
        "    if isinstance(node, ast.ClassDef) and node.name == class_name:\n"
        "        for item in node.body:\n"
        "            if isinstance(item, ast.FunctionDef) and item.name == '__init__':\n"
        "                func_src = textwrap.dedent(\n"
        "                    ''.join(lines[item.lineno - 1 : item.end_lineno])\n"
        "                )\n"
        "                src = 'from __future__ import annotations\\nclass _P:\\n'\n"
        "                src += textwrap.indent(func_src, '    ')\n"
        "                ns = {'__builtins__': __builtins__}\n"
        "                exec(src, ns)\n"
        "                sig = inspect.signature(ns['_P'].__init__)\n"
        "                assert param_name in sig.parameters, (\n"
        "                    param_name + ' must be a named parameter '\n"
        "                    'for Transformers v5 signature introspection'\n"
        "                )\n"
        "                print('PASS')\n"
        "                break\n"
        "        break\n"
    )


def _store_check_code(
    proc_file: str, class_name: str, param_name: str, sentinel_attr: str,
) -> str:
    """Build subprocess script: verify constructor stores the parameter (not creates internally)."""
    return (
        "import ast, textwrap\n"
        "from pathlib import Path\n"
        "\n"
        "class Mock:\n"
        "    def __init__(self, *a, **kw): pass\n"
        "    def __getattr__(self, name): return Mock()\n"
        "    def __call__(self, *a, **kw): return Mock()\n"
        "    def __bool__(self): return True\n"
        "    def __iter__(self): return iter([])\n"
        "\n"
        "class Sentinel:\n"
        "    def __getattr__(self, name): return Mock()\n"
        "\n"
        f"source = Path('{proc_file}').read_text()\n"
        "tree = ast.parse(source)\n"
        "lines = source.splitlines(keepends=True)\n"
        "\n"
        f"class_name = '{class_name}'\n"
        f"param_name = '{param_name}'\n"
        f"sentinel_attr = '{sentinel_attr}'\n"
        "\n"
        "for node in ast.walk(tree):\n"
        "    if isinstance(node, ast.ClassDef) and node.name == class_name:\n"
        "        for item in node.body:\n"
        "            if isinstance(item, ast.FunctionDef) and item.name == '__init__':\n"
        "                func_src = textwrap.dedent(\n"
        "                    ''.join(lines[item.lineno - 1 : item.end_lineno])\n"
        "                )\n"
        "                src = 'from __future__ import annotations\\nclass _P:\\n'\n"
        "                src += textwrap.indent(func_src, '    ')\n"
        "                ns = {'__builtins__': __builtins__}\n"
        "                exec(src, ns)\n"
        "                Proc = ns['_P']\n"
        "                # Pass a unique sentinel to verify it's stored, not overwritten\n"
        "                s = Sentinel()\n"
        "                setattr(s, sentinel_attr, True)\n"
        "                obj = object.__new__(Proc)\n"
        "                Proc.__init__(obj, Mock(), **{param_name: s})\n"
        "                assert hasattr(obj, param_name), param_name + ' not set on self'\n"
        "                assert getattr(getattr(obj, param_name), sentinel_attr, False), (\n"
        "                    param_name + ' was created internally, not stored from parameter'\n"
        "                )\n"
        "                print('PASS')\n"
        "                break\n"
        "        break\n"
    )


def _model_passes_component_code(
    model_file: str, helper_method: str, captured_param: str,
) -> str:
    """Build subprocess script: verify model's get_hf_processor passes the component."""
    return (
        "import ast, textwrap\n"
        "from pathlib import Path\n"
        "\n"
        "class Mock:\n"
        "    def __init__(self, *a, **kw): pass\n"
        "    def __getattr__(self, name): return Mock()\n"
        "    def __call__(self, *a, **kw): return Mock()\n"
        "    def __bool__(self): return True\n"
        "\n"
        f"source = Path('{model_file}').read_text()\n"
        "tree = ast.parse(source)\n"
        "lines = source.splitlines(keepends=True)\n"
        "\n"
        "# Find class with get_hf_processor\n"
        "for node in ast.walk(tree):\n"
        "    if not isinstance(node, ast.ClassDef):\n"
        "        continue\n"
        "    methods = {i.name: i for i in node.body if isinstance(i, ast.FunctionDef)}\n"
        "    if 'get_hf_processor' not in methods:\n"
        "        continue\n"
        "    to_extract = ['get_hf_processor']\n"
        f"    if '{helper_method}' in methods:\n"
        f"        to_extract.append('{helper_method}')\n"
        "    parts = []\n"
        "    for item in node.body:\n"
        "        if isinstance(item, ast.FunctionDef) and item.name in to_extract:\n"
        "            parts.append(textwrap.dedent(\n"
        "                ''.join(lines[item.lineno - 1 : item.end_lineno])\n"
        "            ))\n"
        "    body = chr(10).join(parts)\n"
        "    src = 'from __future__ import annotations\\nclass _M:\\n'\n"
        "    src += textwrap.indent(body, '    ')\n"
        "    captured = {}\n"
        "    class RecordingProcessor:\n"
        "        def __init__(self, **kwargs):\n"
        "            captured.update(kwargs)\n"
        "    ns = {'__builtins__': __builtins__, 'RecordingProcessor': RecordingProcessor}\n"
        "    exec(src, ns)\n"
        "    obj = object.__new__(ns['_M'])\n"
        "    obj.get_tokenizer = lambda: Mock()\n"
        "    obj.ctx = Mock()\n"
        "    # The fixed code directly instantiates the processor class\n"
        "    # Check that the method source contains the parameter name being passed\n"
        f"    assert '{captured_param}=' in body, (\n"
        f"        'get_hf_processor must pass {captured_param}= to processor constructor'\n"
        "    )\n"
        "    print('PASS')\n"
        "    break\n"
        "else:\n"
        "    raise AssertionError('No class with get_hf_processor found')\n"
    )


# [pr_diff] fail_to_pass
def test_pixtral_processor_init_signature():
    """MistralCommonPixtralProcessor.__init__ must have image_processor as a named parameter
    for Transformers v5 signature introspection."""
    r = _run_py(_sig_check_code(
        PIXTRAL_PROC, "MistralCommonPixtralProcessor", "image_processor",
    ))
    assert r.returncode == 0, f"Signature check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_voxtral_processor_init_signature():
    """MistralCommonVoxtralProcessor.__init__ must have feature_extractor as a named parameter
    for Transformers v5 signature introspection."""
    r = _run_py(_sig_check_code(
        VOXTRAL_PROC, "MistralCommonVoxtralProcessor", "feature_extractor",
    ))
    assert r.returncode == 0, f"Signature check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_pixtral_processor_stores_image_processor():
    """MistralCommonPixtralProcessor.__init__ must store image_processor from the parameter
    (not create internally)."""
    r = _run_py(_store_check_code(
        PIXTRAL_PROC, "MistralCommonPixtralProcessor",
        "image_processor", "_marker_pixtral",
    ))
    assert r.returncode == 0, f"Store check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_voxtral_processor_stores_feature_extractor():
    """MistralCommonVoxtralProcessor.__init__ must store feature_extractor from the parameter
    (not create internally)."""
    r = _run_py(_store_check_code(
        VOXTRAL_PROC, "MistralCommonVoxtralProcessor",
        "feature_extractor", "_marker_voxtral",
    ))
    assert r.returncode == 0, f"Store check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_pixtral_model_passes_image_processor():
    """Pixtral model's get_hf_processor must pass image_processor to the processor constructor."""
    r = _run_py(_model_passes_component_code(
        PIXTRAL_MODEL, "get_image_processor", "image_processor",
    ))
    assert r.returncode == 0, f"Model integration check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_voxtral_model_passes_feature_extractor():
    """Voxtral model's get_hf_processor must pass feature_extractor to the processor constructor."""
    r = _run_py(_model_passes_component_code(
        VOXTRAL_MODEL, "get_feature_extractor", "feature_extractor",
    ))
    assert r.returncode == 0, f"Model integration check failed: {r.stderr}"
    assert "PASS" in r.stdout
