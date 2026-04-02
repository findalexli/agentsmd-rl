"""
Task: transformers-autoprocessor-hub-kwargs
Repo: huggingface/transformers @ c17877c2ad39f8f736d5ea8a34f98e562843fc83
PR:   44710

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/models/auto/processing_auto.py"


def _exec_kwargs_filter(test_kwargs: dict) -> dict:
    """Extract the cached_file_kwargs filtering logic from from_pretrained and exec it.

    On the base commit, inspect.signature(cached_file) only returns
    {path_or_repo_id, filename, kwargs} — hub kwargs like force_download
    are silently dropped.  After the fix, an explicit tuple of hub kwargs
    is used instead, so they survive the filter.

    This helper extracts the real filtering code, runs it with *test_kwargs*
    against a mock cached_file(path_or_repo_id, filename, **kwargs), and
    returns the resulting cached_file_kwargs dict.
    """
    import inspect as inspect_mod

    source = Path(TARGET).read_text()
    lines = source.splitlines()

    # Step 1: find  cached_file_kwargs = { ... }  (the initial dict build, not .update)
    assign_start = None
    for i, line in enumerate(lines):
        s = line.strip()
        if "cached_file_kwargs" in s and "=" in s and ("{" in s or "dict(" in s):
            if ".update" in s or "+=" in s or "==" in s:
                continue
            assign_start = i
            break

    assert assign_start is not None, (
        "cached_file_kwargs dict-build not found in processing_auto.py"
    )

    # Step 2: capture lines until braces / parens balance
    j = assign_start
    block = lines[j]
    while j < len(lines) - 1:
        opens = block.count("{") + block.count("(")
        closes = block.count("}") + block.count(")")
        if opens <= closes:
            break
        j += 1
        block += "\n" + lines[j]
    assign_end = j + 1

    # Step 3: find variables referenced in the assignment that are defined above
    assign_text = "\n".join(lines[assign_start:assign_end])
    ref_names = set(re.findall(r"\b([_a-zA-Z]\w*)\b", assign_text))
    skip = {
        "cached_file_kwargs", "kwargs", "cached_file", "inspect",
        "key", "k", "v", "for", "in", "if", "not",
        "True", "False", "None",
    }
    to_find = ref_names - skip

    block_start = assign_start
    for var in to_find:
        for k in range(assign_start - 1, max(assign_start - 40, -1), -1):
            if re.match(rf"\s*{re.escape(var)}\s*=", lines[k]):
                block_start = min(block_start, k)
                break

    # Step 4: capture full block, extending forward if delimiters are unbalanced
    full_text = "\n".join(lines[block_start:assign_end])
    idx = assign_end
    while idx < len(lines) and (
        full_text.count("(") > full_text.count(")")
        or full_text.count("{") > full_text.count("}")
    ):
        full_text += "\n" + lines[idx]
        idx += 1

    code = textwrap.dedent(full_text)

    # Mock cached_file with the SAME signature as the real one (**kwargs)
    def cached_file(path_or_repo_id, filename, **kwargs):
        pass

    ns = {"kwargs": dict(test_kwargs), "cached_file": cached_file, "inspect": inspect_mod}
    exec(code, ns)

    result = ns.get("cached_file_kwargs")
    assert result is not None, "cached_file_kwargs was not assigned"
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """processing_auto.py must parse without syntax errors."""
    import ast

    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hub_kwargs_forwarded():
    """force_download, cache_dir, and token must survive the cached_file filter."""
    test_kwargs = {
        "force_download": True,
        "cache_dir": "/tmp/hf_cache",
        "token": "hf_test_token_123",
        "_from_auto": True,
        "processor_class": "SomeProcessor",
    }
    result = _exec_kwargs_filter(test_kwargs)

    for key in ("force_download", "cache_dir", "token"):
        assert key in result, f"{key} was dropped by the cached_file kwargs filter"
    assert "_from_auto" not in result, "_from_auto should not be forwarded to cached_file"


# [pr_diff] fail_to_pass
def test_revision_and_subfolder_forwarded():
    """revision, subfolder, local_files_only, user_agent must survive the filter."""
    test_kwargs = {
        "revision": "refs/pr/42",
        "subfolder": "models/processor",
        "local_files_only": True,
        "user_agent": "test-agent/1.0",
        "task": "image-classification",
    }
    result = _exec_kwargs_filter(test_kwargs)

    for key in ("revision", "subfolder", "local_files_only", "user_agent"):
        assert key in result, f"{key} was dropped by the cached_file kwargs filter"
    assert "task" not in result, "task should not be forwarded to cached_file"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + cleanup
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """from_pretrained must have a substantial implementation, not a stub."""
    import ast

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AutoProcessor":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "from_pretrained":
                    body = [s for s in item.body if not isinstance(s, (ast.Pass, ast.Expr))]
                    assert len(body) >= 10, (
                        f"from_pretrained has only {len(body)} statements — likely a stub"
                    )
                    return
    assert False, "AutoProcessor.from_pretrained not found"


# [pr_diff] fail_to_pass
def test_all_nine_hub_kwargs():
    """All 9 hub kwargs must be forwarded; non-hub kwargs must be excluded."""
    hub_kwargs = {
        "cache_dir": "/data/cache",
        "force_download": False,
        "proxies": {"https": "http://proxy:8080"},
        "token": "hf_abc",
        "revision": "v2.0",
        "local_files_only": False,
        "subfolder": "checkpoints",
        "repo_type": "model",
        "user_agent": "my-app/2.0",
    }
    non_hub_kwargs = {
        "_from_auto": True,
        "processor_class": "WhisperProcessor",
        "task": "automatic-speech-recognition",
        "trust_remote_code": True,
        "torch_dtype": "float16",
    }
    result = _exec_kwargs_filter({**hub_kwargs, **non_hub_kwargs})

    for key in hub_kwargs:
        assert key in result, f"hub kwarg '{key}' was dropped"
        assert result[key] == hub_kwargs[key], f"hub kwarg '{key}' has wrong value"
    for key in non_hub_kwargs:
        assert key not in result, f"non-hub kwarg '{key}' should not be forwarded"


# [pr_diff] pass_to_pass
def test_no_unused_inspect_import():
    """If inspect is imported it must be used; otherwise it should be removed."""
    import ast

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    has_inspect_import = any(
        (isinstance(n, ast.Import) and any(a.name == "inspect" for a in n.names))
        or (isinstance(n, ast.ImportFrom) and n.module == "inspect")
        for n in ast.walk(tree)
    )

    if has_inspect_import:
        usages = sum(
            1
            for line in source.splitlines()
            if "inspect." in line
            and not line.strip().startswith("#")
            and "import" not in line
        )
        assert usages > 0, "inspect is imported but never used — remove the import"
