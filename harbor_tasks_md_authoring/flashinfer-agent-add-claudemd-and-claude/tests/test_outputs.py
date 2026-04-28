"""Behavioral checks for flashinfer-agent-add-claudemd-and-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flashinfer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/skill.md')
    assert '- **Destination passing style**: Output tensor(s) are passed as optional parameters (`out: Optional[torch.Tensor] = None`). This allows users to provide pre-allocated buffers to avoid allocation overh' in text, "expected to find: " + '- **Destination passing style**: Output tensor(s) are passed as optional parameters (`out: Optional[torch.Tensor] = None`). This allows users to provide pre-allocated buffers to avoid allocation overh'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/skill.md')
    assert 'FlashInfer uses `CompilationContext` to manage CUDA architecture targets. This is critical because some kernels only work on specific GPU architectures (e.g., Hopper SM90, Blackwell SM100).' in text, "expected to find: " + 'FlashInfer uses `CompilationContext` to manage CUDA architecture targets. This is critical because some kernels only work on specific GPU architectures (e.g., Hopper SM90, Blackwell SM100).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/skill.md')
    assert "This tutorial walks through adding a simple element-wise scale operation to FlashInfer. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow." in text, "expected to find: " + "This tutorial walks through adding a simple element-wise scale operation to FlashInfer. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/benchmark-kernel/skill.md')
    assert '--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 32 --s_kv 2048 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128' in text, "expected to find: " + '--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 32 --s_kv 2048 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/benchmark-kernel/skill.md')
    assert '--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 64 --s_kv 4096 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128' in text, "expected to find: " + '--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 64 --s_kv 4096 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/benchmark-kernel/skill.md')
    assert '- **Attention**: `BatchDecodeWithPagedKVCacheWrapper`, `BatchPrefillWithPagedKVCacheWrapper`, `BatchPrefillWithRaggedKVCacheWrapper`, `BatchMLAPagedAttentionWrapper`' in text, "expected to find: " + '- **Attention**: `BatchDecodeWithPagedKVCacheWrapper`, `BatchPrefillWithPagedKVCacheWrapper`, `BatchPrefillWithRaggedKVCacheWrapper`, `BatchMLAPagedAttentionWrapper`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-cuda-crash/skill.md')
    assert "**Solution**: FlashInfer's `@flashinfer_api` decorator logs inputs BEFORE execution, so you can see what caused the crash even after the program terminates." in text, "expected to find: " + "**Solution**: FlashInfer's `@flashinfer_api` decorator logs inputs BEFORE execution, so you can see what caused the crash even after the program terminates."[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-cuda-crash/skill.md')
    assert 'This tutorial shows you how to debug CUDA crashes and errors in FlashInfer using the `@flashinfer_api` logging decorator.' in text, "expected to find: " + 'This tutorial shows you how to debug CUDA crashes and errors in FlashInfer using the `@flashinfer_api` logging decorator.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-cuda-crash/skill.md')
    assert '**What it means**: Level 5 statistics are automatically skipped during CUDA graph capture (to avoid synchronization)' in text, "expected to find: " + '**What it means**: Level 5 statistics are automatically skipped during CUDA graph capture (to avoid synchronization)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> Because practical engineering involves the accumulated experience of trial and error, match the coding style, efficiency, complexity, verbosity, and defensiveness by learning from existing code as m' in text, "expected to find: " + '> Because practical engineering involves the accumulated experience of trial and error, match the coding style, efficiency, complexity, verbosity, and defensiveness by learning from existing code as m'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'FlashInfer is a GPU kernel library for LLM serving that uses **JIT (Just-In-Time) compilation by default**. This means kernel code changes are automatically picked up without reinstalling the package ' in text, "expected to find: " + 'FlashInfer is a GPU kernel library for LLM serving that uses **JIT (Just-In-Time) compilation by default**. This means kernel code changes are automatically picked up without reinstalling the package '[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Keep documentation in sync with code changes:** When modifying code that is referenced in this document or in `.claude/skills/`, update the corresponding documentation immediately. This includes:' in text, "expected to find: " + '**Keep documentation in sync with code changes:** When modifying code that is referenced in this document or in `.claude/skills/`, update the corresponding documentation immediately. This includes:'[:80]

