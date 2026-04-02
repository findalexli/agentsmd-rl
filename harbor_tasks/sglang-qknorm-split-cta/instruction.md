# Optimize qknorm_across_heads CUDA kernel by splitting Q and K into separate CTAs

## Context

The file `python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh` contains a CUDA kernel `qknorm_across_heads_reg_kernel` that applies RMSNorm to both the Q (query) and K (key) tensors in a single CTA (Cooperative Thread Array). This means each thread block simultaneously manages:

- Loading and accumulating squares for both `q` and `k`
- Maintaining separate weight vectors for both
- Keeping dual reduction buffers in shared memory (64 floats — 32 for Q, 32 for K)
- Writing back separate normalized outputs

This design keeps too much state live at the same time per thread, resulting in high register pressure and large shared memory usage, which limits occupancy.

## Problem

The current kernel processes both Q and K in a single CTA, leading to:

1. **High register pressure** — each thread must hold `v_q`, `v_k`, `v_q_weight`, `v_k_weight`, `v_q_out`, `v_k_out`, plus two separate accumulators (`acc_square_q`, `acc_square_k`)
2. **Large shared memory** — `shared_memory[64]` is used for two separate reduction buffers (`buffer_q` at `[0..31]` and `buffer_k` at `[32..63]`)
3. **Poor occupancy** — the combination of high register and shared memory usage limits how many blocks can run concurrently per SM

The kernel launch currently uses a 1D grid: `LaunchKernel(static_cast<uint>(N.unwrap()), threads, device.unwrap())`.

## Task

Refactor the kernel so that Q and K normalization are split across a second grid dimension instead of being interleaved in the same CTA. Each block should handle only one of Q or K, which will:

- Halve the number of register-resident vectors per thread
- Cut the shared memory reduction buffer in half
- Significantly improve occupancy

The `rms` helper function's parameters should also be updated for const-correctness since the values are only read, not modified.

## Relevant files

- `python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh` — the kernel definition and its launcher struct `QKNormAcrossHeadsKernel`

## Constraints

- The kernel must produce identical numerical results (same RMSNorm computation)
- The launcher struct's `LaunchKernel` call must be updated to use a 2D grid
- Keep the single-launch design (do not split into two separate kernel launches)
