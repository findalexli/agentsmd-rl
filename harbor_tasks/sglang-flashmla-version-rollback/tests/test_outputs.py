"""
Task: sglang-flashmla-version-rollback
Repo: sgl-project/sglang @ 7c7b2a8c97816b84c6c90ebe28e7e1a9ea334888
PR:   #21430

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
CMAKE_FILE = Path(REPO) / "sgl-kernel/cmake/flashmla.cmake"
PY_FILE = Path(REPO) / "sgl-kernel/python/sgl_kernel/flash_mla.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both target files exist and Python file parses without errors."""
    import ast

    assert CMAKE_FILE.exists(), f"{CMAKE_FILE} not found"
    assert PY_FILE.exists(), f"{PY_FILE} not found"
    source = PY_FILE.read_text()
    ast.parse(source)  # raises SyntaxError if broken


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_git_tag_rolled_back():
    """cmake must pin the older stable FlashMLA commit via FetchContent GIT_TAG."""
    r = subprocess.run(
        ["python3", "-c", """
cmake = open('/workspace/sglang/sgl-kernel/cmake/flashmla.cmake').read()
stable = 'be055fb7df0090fde45f08e9cb5b8b4c0272da73'
found = False
for line in cmake.splitlines():
    s = line.strip()
    if s.startswith('GIT_TAG '):
        tag = s.split()[-1]
        assert tag == stable, f'GIT_TAG is {tag}, expected {stable}'
        found = True
        break
assert found, 'GIT_TAG directive not found in cmake'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_source_files_flat_layout():
    """cmake FlashMLA_SOURCES must use flat source paths, not nested instantiation dirs."""
    r = subprocess.run(
        ["python3", "-c", """
cmake = open('/workspace/sglang/sgl-kernel/cmake/flashmla.cmake').read()

# Extract FlashMLA_SOURCES block
start = cmake.index('set(FlashMLA_SOURCES')
depth, end = 0, start
for i, ch in enumerate(cmake[start:], start):
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
sources_block = cmake[start:end]

# Collect all .cu/.cpp source paths from the block
sources = []
for line in sources_block.splitlines():
    s = line.strip().strip('"')
    if s.endswith(('.cu', '.cpp', '.cc')):
        sources.append(s)

# Older version flat paths must be present
required = [
    'csrc/smxx/get_mla_metadata.cu',
    'csrc/smxx/mla_combine.cu',
    'csrc/sm90/decode/dense/splitkv_mla.cu',
    'csrc/sm90/decode/sparse_fp8/splitkv_mla.cu',
    'csrc/sm100/decode/sparse_fp8/splitkv_mla.cu',
    'csrc/sm100/prefill/sparse/fwd.cu',
]
for req in required:
    assert any(req in s for s in sources), f'Missing flat source: {req}'

# Newer version nested instantiation paths must NOT be present
for s in sources:
    assert 'instantiations/' not in s, f'Nested instantiation source found: {s}'
    assert 'get_decoding_sched_meta/' not in s, f'Nested decode meta source found: {s}'
    assert 'decode/combine/' not in s, f'Nested combine source found: {s}'

print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sm103a_patch_targets_flashmla_utils():
    """SM103a patch must target csrc/flashmla_utils.h, not the renamed csrc/utils.h."""
    r = subprocess.run(
        ["python3", "-c", """
cmake = open('/workspace/sglang/sgl-kernel/cmake/flashmla.cmake').read()

# Find the FLASHMLA_UTILS_FILE variable to determine the patch target
found = False
for line in cmake.splitlines():
    s = line.strip()
    if 'FLASHMLA_UTILS_FILE' in s and 'set(' in s:
        assert 'flashmla_utils.h' in s, f'Patch target should be flashmla_utils.h, got: {s}'
        assert 'csrc/utils.h' not in s.replace('flashmla_utils.h', ''), \\
            f'Should not reference csrc/utils.h as patch target: {s}'
        found = True
        break
assert found, 'FLASHMLA_UTILS_FILE variable not found'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_import_error_guards_removed():
    """_flashmla_import_error guard must not appear in any of the 3 public functions."""
    r = subprocess.run(
        ["python3", "-c", """
import ast

with open('/workspace/sglang/sgl-kernel/python/sgl_kernel/flash_mla.py') as f:
    source = f.read()
tree = ast.parse(source)

target_funcs = ['get_mla_metadata', 'flash_mla_with_kvcache', 'flash_mla_sparse_fwd']
guarded = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in target_funcs:
        func_lines = source.splitlines()[node.lineno - 1 : node.end_lineno]
        func_src = chr(10).join(func_lines)
        if '_flashmla_import_error' in func_src:
            guarded.append(node.name)

assert not guarded, f'Import error guards still present in: {guarded}'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cpp20_flags_removed():
    """target_compile_options for flashmla_ops must not include C++20 flags."""
    r = subprocess.run(
        ["python3", "-c", """
cmake = open('/workspace/sglang/sgl-kernel/cmake/flashmla.cmake').read()

# Extract the target_compile_options block for flashmla_ops
tag = 'target_compile_options(flashmla_ops'
start = cmake.index(tag)
depth, end = 0, start
for i, ch in enumerate(cmake[start:], start):
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
opts_block = cmake[start:end]

assert '-std=c++20' not in opts_block, f'C++20 flags still in compile options: {opts_block}'
assert 'COMPILE_LANGUAGE:CXX' not in opts_block, f'CXX-specific options still present: {opts_block}'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kerutils_include_removed():
    """target_include_directories for flashmla_ops must not reference kerutils."""
    r = subprocess.run(
        ["python3", "-c", """
cmake = open('/workspace/sglang/sgl-kernel/cmake/flashmla.cmake').read()

# Extract the target_include_directories block for flashmla_ops
tag = 'target_include_directories(flashmla_ops'
start = cmake.index(tag)
depth, end = 0, start
for i, ch in enumerate(cmake[start:], start):
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
inc_block = cmake[start:end]

assert 'kerutils' not in inc_block, f'kerutils still in include dirs: {inc_block}'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cutlass_sm103a_patch_preserved():
    """The cutlass SM103a patching section must survive the rollback."""
    content = CMAKE_FILE.read_text()
    required = [
        "CUTLASS_ARCH_MMA_SM103_SUPPORTED",
        "CUTLASS_ARCH_MMA_SM103_ENABLED",
        "CUTLASS_ARCH_MMA_SM100A_ENABLED",
        "cutlass/arch/config.h",
        "SM103_FOUND",
        "compute_103a",
    ]
    for r in required:
        assert r in content, f"Missing cutlass SM103a element: {r}"


# [pr_diff] pass_to_pass
def test_cmake_core_structure_preserved():
    """FetchContent, CUDA flags, extension sources, link/install targets must remain."""
    content = CMAKE_FILE.read_text()
    checks = [
        "FetchContent_Declare",
        "FetchContent_Populate(repo-flashmla)",
        "FLASHMLA_CUDA_FLAGS",
        "--expt-relaxed-constexpr",
        "--expt-extended-lambda",
        "flashmla_ops",
        "csrc/flashmla_extension.cc",
        "csrc/extension/sm90/dense_fp8/",
        "target_link_libraries(flashmla_ops",
        "install(TARGETS flashmla_ops",
        "SKBUILD_SABI_VERSION",
        "compute_90a",
        "compute_100a",
    ]
    for c in checks:
        assert c in content, f"Missing cmake element: {c}"


# [pr_diff] pass_to_pass
def test_python_function_signatures_and_dispatch():
    """Public functions must keep their parameter signatures and dispatch to torch.ops."""
    import ast

    source = PY_FILE.read_text()
    tree = ast.parse(source)

    expected_sigs = {
        "get_mla_metadata": {"cache_seqlens", "num_heads_k"},
        "flash_mla_with_kvcache": {"q", "k_cache", "block_table", "head_dim_v", "tile_scheduler_metadata"},
        "flash_mla_sparse_fwd": {"q", "kv", "indices", "sm_scale"},
    }
    expected_ops = {
        "get_mla_metadata": "get_mla_decoding_metadata",
        "flash_mla_with_kvcache": "fwd_kvcache_mla",
        "flash_mla_sparse_fwd": "sparse_prefill_fwd",
    }

    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in expected_sigs:
            found.add(node.name)
            param_names = {arg.arg for arg in node.args.args}
            missing = expected_sigs[node.name] - param_names
            assert not missing, f"{node.name} missing parameters: {missing}"

            func_lines = source.splitlines()[node.lineno - 1 : node.end_lineno]
            func_src = "\n".join(func_lines)
            op_name = expected_ops[node.name]
            assert op_name in func_src, f"{node.name} does not dispatch to *{op_name}*"

    assert found == set(expected_sigs), f"Missing functions: {set(expected_sigs) - found}"


# [static] pass_to_pass
def test_not_stub():
    """Modified files are not stubs — cmake and python files have substantive content."""
    cmake_lines = len(CMAKE_FILE.read_text().splitlines())
    py_lines = len(PY_FILE.read_text().splitlines())
    cmake_size = CMAKE_FILE.stat().st_size
    py_size = PY_FILE.stat().st_size

    assert cmake_size >= 2000, f"cmake file too small ({cmake_size} bytes)"
    assert cmake_lines >= 80, f"cmake file too few lines ({cmake_lines})"
    assert py_size >= 2000, f"Python file too small ({py_size} bytes)"
    assert py_lines >= 80, f"Python file too few lines ({py_lines})"
