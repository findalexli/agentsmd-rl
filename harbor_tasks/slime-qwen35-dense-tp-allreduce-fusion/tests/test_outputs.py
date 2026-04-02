"""
Task: slime-qwen35-dense-tp-allreduce-fusion
Repo: THUDM/slime @ 2640e6cd98c864231b570425e0877dcff295984c

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only because: target code lives inside a unified-diff patch file and
# requires torch/sglang to import — we reconstruct code from patch hunks
# and verify structure via AST.

import ast
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/slime"
TARGET = f"{REPO}/docker/patch/latest/sglang.patch"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_patch():
    return Path(TARGET).read_text()


def _get_qwen_section(patch_text):
    """Extract the qwen3_5.py diff section from the patch file."""
    sections = re.split(r"(?=^diff --git )", patch_text, flags=re.MULTILINE)
    for s in sections:
        if "qwen3_5.py" in s.split("\n", 1)[0]:
            return s
    return ""


def _extract_hunks(section):
    """Split a diff section into (header, lines) tuples based on @@ markers."""
    hunks = []
    header = ""
    lines = []
    for line in section.splitlines():
        if line.startswith("@@"):
            if lines:
                hunks.append((header, lines))
            header = line
            lines = []
        elif header:
            lines.append(line)
    if lines:
        hunks.append((header, lines))
    return hunks


def _hunk_after_code(hunk_lines):
    """Reconstruct the 'after' code from a hunk (context + added, skip removed)."""
    code = []
    for line in hunk_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            continue
        if line.startswith("+"):
            code.append(line[1:])
        elif line.startswith(" "):
            code.append(line[1:])
    return "\n".join(code)


def _hunks_for_class(hunks, class_name, content_hint=None):
    """Find hunks whose @@ header mentions class_name, optionally with content_hint."""
    results = []
    for header, lines in hunks:
        if class_name in header:
            if content_hint is None or any(content_hint in l for l in lines):
                results.append((header, lines))
    return results


def _try_parse(code_fragment):
    """Dedent a code fragment, wrap in a function, and try ast.parse."""
    lines = code_fragment.splitlines()
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return None
    min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
    dedented = "\n".join(l[min_indent:] for l in lines)
    wrapped = "def _f(self):\n" + textwrap.indent(dedented, "    ")
    try:
        return ast.parse(wrapped)
    except SyntaxError:
        return None


def _ast_has_isinstance_if(tree, type_name):
    """Check if tree has an if-statement whose test is isinstance(..., <type_name>)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Name):
            if test.func.id == "isinstance" and type_name in ast.dump(test):
                return True
    return False


def _ast_has_attr_assign(tree, attr_name):
    """Check if tree assigns to an attribute named attr_name (e.g. x.attr = ...)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == attr_name:
                    return True
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Attribute) and node.target.attr == attr_name:
                return True
    return False


def _ast_else_has_call(tree, func_name):
    """Check if an if-statement's else branch contains a call to func_name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and node.orelse:
            for child in ast.walk(ast.Module(body=node.orelse, type_ignores=[])):
                if isinstance(child, ast.Call):
                    if func_name in ast.dump(child):
                        return True
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_patch_is_valid_diff():
    """Patch file must exist, be non-empty, and contain a qwen3_5.py section."""
    content = _read_patch()
    assert len(content) > 100, "Patch file is too small or empty"
    qwen = _get_qwen_section(content)
    assert qwen, "No qwen3_5.py diff section found in patch file"
    hunks = _extract_hunks(qwen)
    assert len(hunks) >= 2, f"Expected >=2 hunks in qwen3_5.py section, got {len(hunks)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_linear_init_allreduce_fusion():
    """LinearDecoderLayer.__init__ must pass allow_allreduce_fusion=True."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    linear_hunks = _hunks_for_class(hunks, "LinearDecoderLayer")
    assert linear_hunks, "No hunks found for LinearDecoderLayer"

    found = False
    for _, lines in linear_hunks:
        after = _hunk_after_code(lines)
        if re.search(r"allow_allreduce_fusion\s*=\s*True", after):
            found = True
            break

    assert found, (
        "LinearDecoderLayer.__init__ must pass allow_allreduce_fusion=True "
        "to LayerCommunicator"
    )


# [pr_diff] fail_to_pass
def test_attn_init_allreduce_fusion():
    """AttentionDecoderLayer.__init__ must pass allow_allreduce_fusion=True."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    attn_hunks = _hunks_for_class(hunks, "AttentionDecoderLayer")
    assert attn_hunks, "No hunks found for AttentionDecoderLayer"

    found = False
    for _, lines in attn_hunks:
        after = _hunk_after_code(lines)
        if re.search(r"allow_allreduce_fusion\s*=\s*True", after):
            found = True
            break

    assert found, (
        "AttentionDecoderLayer.__init__ must pass allow_allreduce_fusion=True "
        "to LayerCommunicator"
    )


# [pr_diff] fail_to_pass
def test_linear_forward_isinstance_dispatch():
    """LinearDecoderLayer.forward must branch on isinstance(self.mlp, Qwen2MoeSparseMoeBlock)."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    fwd_hunks = _hunks_for_class(hunks, "LinearDecoderLayer", "hidden_states")
    assert fwd_hunks, "No forward-method hunks for LinearDecoderLayer"

    found = False
    for _, lines in fwd_hunks:
        after = _hunk_after_code(lines)
        tree = _try_parse(after)
        if tree and _ast_has_isinstance_if(tree, "Qwen2MoeSparseMoeBlock"):
            found = True
            break
        # Regex fallback
        if re.search(r"isinstance\s*\(\s*self\.mlp\s*,\s*Qwen2MoeSparseMoeBlock\s*\)", after):
            found = True
            break

    assert found, (
        "LinearDecoderLayer.forward must have "
        "if isinstance(self.mlp, Qwen2MoeSparseMoeBlock) dispatch"
    )


# [pr_diff] fail_to_pass
def test_attn_forward_isinstance_dispatch():
    """AttentionDecoderLayer.forward must branch on isinstance(self.mlp, Qwen2MoeSparseMoeBlock)."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    fwd_hunks = _hunks_for_class(hunks, "AttentionDecoderLayer", "hidden_states")
    assert fwd_hunks, "No forward-method hunks for AttentionDecoderLayer"

    found = False
    for _, lines in fwd_hunks:
        after = _hunk_after_code(lines)
        tree = _try_parse(after)
        if tree and _ast_has_isinstance_if(tree, "Qwen2MoeSparseMoeBlock"):
            found = True
            break
        if re.search(r"isinstance\s*\(\s*self\.mlp\s*,\s*Qwen2MoeSparseMoeBlock\s*\)", after):
            found = True
            break

    assert found, (
        "AttentionDecoderLayer.forward must have "
        "if isinstance(self.mlp, Qwen2MoeSparseMoeBlock) dispatch"
    )


# [pr_diff] fail_to_pass
def test_fusion_query_both_classes():
    """Both forward methods must call should_fuse_mlp_allreduce_with_next_layer."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    for cls in ["LinearDecoderLayer", "AttentionDecoderLayer"]:
        fwd_hunks = _hunks_for_class(hunks, cls, "hidden_states")
        assert fwd_hunks, f"No forward hunks for {cls}"

        found = False
        for _, lines in fwd_hunks:
            after = _hunk_after_code(lines)
            if "should_fuse_mlp_allreduce_with_next_layer" in after:
                found = True
                break

        assert found, (
            f"{cls}.forward must call "
            f"self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer()"
        )


# [pr_diff] fail_to_pass
def test_fusion_attr_and_conditional_postprocess():
    """Both forwards set _sglang_needs_allreduce_fusion and conditionally call postprocess."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    for cls in ["LinearDecoderLayer", "AttentionDecoderLayer"]:
        fwd_hunks = _hunks_for_class(hunks, cls, "hidden_states")
        assert fwd_hunks, f"No forward hunks for {cls}"

        found_attr = False
        found_cond_postprocess = False

        for _, lines in fwd_hunks:
            after = _hunk_after_code(lines)
            tree = _try_parse(after)

            if tree:
                if _ast_has_attr_assign(tree, "_sglang_needs_allreduce_fusion"):
                    found_attr = True
                if _ast_else_has_call(tree, "postprocess_layer"):
                    found_cond_postprocess = True
            else:
                # Regex fallback
                if re.search(r"\._sglang_needs_allreduce_fusion\s*=\s*True", after):
                    found_attr = True
                if re.search(r"else:\s*\n[^@]*?postprocess_layer", after, re.DOTALL):
                    found_cond_postprocess = True

        assert found_attr, (
            f"{cls}.forward must set _sglang_needs_allreduce_fusion = True "
            f"on hidden_states when fusion is active"
        )
        assert found_cond_postprocess, (
            f"{cls}.forward must call postprocess_layer conditionally "
            f"(in else branch, skipped when fusion is active)"
        )


# [pr_diff] fail_to_pass
def test_dense_mlp_gets_fusion_flag():
    """Dense MLP path must receive the fusion flag, not forward_batch."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    for cls in ["LinearDecoderLayer", "AttentionDecoderLayer"]:
        fwd_hunks = _hunks_for_class(hunks, cls, "hidden_states")
        assert fwd_hunks, f"No forward hunks for {cls}"

        found = False
        for _, lines in fwd_hunks:
            after = _hunk_after_code(lines)
            tree = _try_parse(after)
            if tree:
                # In an if-isinstance block, the else branch should call self.mlp
                # WITHOUT forward_batch as the second argument
                for node in ast.walk(tree):
                    if not isinstance(node, ast.If):
                        continue
                    if not node.orelse:
                        continue
                    # Check else body for self.mlp(...) call
                    for child in ast.walk(ast.Module(body=node.orelse, type_ignores=[])):
                        if not isinstance(child, ast.Call):
                            continue
                        call_dump = ast.dump(child)
                        if "mlp" in call_dump:
                            # The dense path should NOT pass forward_batch
                            if "forward_batch" not in call_dump:
                                found = True
            if not found:
                # Regex fallback: after else:, self.mlp() without forward_batch
                m = re.search(
                    r"else:\s*\n(\s+.*self\.mlp\([^)]+\))",
                    after, re.DOTALL,
                )
                if m and "forward_batch" not in m.group(1):
                    found = True

        assert found, (
            f"{cls}: dense MLP path (else branch) must call self.mlp "
            f"with fusion flag, not forward_batch"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_other_patch_sections_preserved():
    """Other patch sections (qwen3_vl.py, model_config.py) must remain intact."""
    content = _read_patch()
    for required in ["qwen3_vl.py", "model_config.py"]:
        assert re.search(
            rf"diff --git.*{re.escape(required)}", content
        ), f"Patch section for {required} is missing"


# [static] pass_to_pass
def test_not_stub():
    """Both decoder layer sections must have substantive added code."""
    content = _read_patch()
    qwen = _get_qwen_section(content)
    hunks = _extract_hunks(qwen)

    trivial = {"pass", "return", "else:", ")", "}", "(", ""}
    for cls in ["LinearDecoderLayer", "AttentionDecoderLayer"]:
        cls_hunks = _hunks_for_class(hunks, cls)
        assert cls_hunks, f"No hunks for {cls}"

        substantive = 0
        for _, lines in cls_hunks:
            for line in lines:
                if line.startswith("+") and not line.startswith("+++"):
                    stripped = line[1:].strip()
                    if stripped and stripped not in trivial and len(stripped) > 8:
                        substantive += 1

        assert substantive >= 4, (
            f"{cls} has only {substantive} substantive added lines, expected >= 4"
        )


# [static] pass_to_pass
def test_changes_contained():
    """Changes should be contained to the patch file (<=3 files modified)."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    changed = [f for f in r.stdout.strip().split("\n") if f]
    assert len(changed) <= 3, (
        f"Too many files changed ({len(changed)}): {changed[:10]}"
    )
