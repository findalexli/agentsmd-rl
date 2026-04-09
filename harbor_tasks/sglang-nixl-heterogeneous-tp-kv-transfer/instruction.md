# NIXL Disaggregation: Fix Heterogeneous TP KV Transfer for Non-MLA Models

## Problem

NIXL disaggregated serving with **heterogeneous TP** (prefill TP ≠ decode TP) on non-MLA models hangs indefinitely during KV cache transfer.

### Observed Behavior
- Decode workers show zero activity after startup
- Prefill workers drain all requests but they stay permanently in-flight (`#inflight-req` never drops to 0)
- The system hangs indefinitely with no completions
- Manual cancellation required after extended wait time

### Root Cause Analysis

Two related bugs in the NIXL connection handling cause this hang:

**Bug 1: Notification Key Collision**
When processing KV cache transfers, the notification mechanism uses pipeline parallel rank (`pp_rank`) in RDMA notification tags. With PP=1 (no pipeline parallelism), all prefill ranks share `pp_rank=0`, causing notification key collisions. The `TransferStatus.received_kvs_per_pp` tracking only records one key while `num_pp_ranks_expected > 1`, so `is_done()` never returns `True`.

**Bug 2: Incorrect Head Distribution with GQA**
The KV head distribution calculation uses per-rank `kv_head_num` instead of the total KV head count. This loses precision when using Grouped Query Attention (GQA) where `total_kv_heads < tp_size`. The `send_kvcache_slice()` function also lacks proper handling for GQA replication scenarios where multiple prefill ranks share the same KV heads, causing incorrect `dst_head_start_offset` calculations.

## Expected Behavior

- KV cache transfers should complete successfully with heterogeneous TP configurations
- Transfer status tracking should correctly identify when all prefill ranks have sent their data
- Head distribution should handle GQA models correctly when `total_kv_heads < tp_size`

## Files to Look At

- `python/sglang/srt/disaggregation/nixl/conn.py` — Contains the `send_kvcache_slice()` and `add_transfer_request()` methods that handle KV cache transfer coordination

  Key areas to examine:
  - The notification string construction for KV and state transfers
  - The head distribution calculation logic in `send_kvcache_slice()`
  - How `total_kv_head_num` vs `kv_head_num` is used for GQA scenarios

## Context

- **Heterogeneous TP**: Different tensor parallelism sizes between prefill (e.g., TP=4) and decode (e.g., TP=1×4) workers
- **GQA (Grouped Query Attention)**: Attention mechanism where number of KV heads is less than number of query heads
- **NIXL**: NVIDIA Inference Transfer Library for RDMA-based KV cache transfer
- **Disaggregation**: Separating prefill and decode phases onto different GPU workers

## Reference Configuration

Example setup that triggers this bug:
- Model: Qwen3-32B (or any non-MLA model with GQA)
- Topology: 1P4D (1 prefill worker @ TP4 → 4 decode workers @ TP1)
- Backend: NIXL
- Pipeline Parallelism: PP=1
