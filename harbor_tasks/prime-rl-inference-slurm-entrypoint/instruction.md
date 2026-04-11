# Add SLURM inference entrypoint with documentation update

## Problem

The inference server currently only supports local execution. We need to add SLURM support similar to the existing `rl` and `sft` entrypoints. The current setup in `pyproject.toml` points the `inference` command directly to `prime_rl.inference.server:main`, which doesn't support SLURM job submission.

Additionally, the project follows a convention where skills in `skills/` document how to use various components. When adding new entrypoint functionality, the relevant skill documentation must be updated to stay accurate.

## Expected Behavior

1. Create a new `src/prime_rl/entrypoints/inference.py` file with:
   - `main()` function as the CLI entrypoint
   - `inference()` function that routes between local and SLURM execution
   - `inference_slurm()` function for SLURM job submission
   - `inference_local()` function for local execution
   - Config writing and SLURM script generation utilities

2. Update `src/prime_rl/configs/inference.py` to add:
   - `deployment` config with `single_node` and `multi_node` variants
   - `slurm` configuration section
   - `output_dir` and `dry_run` fields
   - Validators ensuring multi-node deployment requires SLURM
   - Auto-setup of SLURM template path

3. Create `src/prime_rl/templates/inference.sbatch.j2` for the SLURM batch script template

4. Update `pyproject.toml` to point the `inference` command to the new entrypoint

5. Update `skills/inference-server/SKILL.md` to document:
   - SLURM scheduling support with examples
   - Single-node and multi-node SLURM configurations
   - Dry run mode for testing configs
   - Updated key files section listing the new entrypoint and template

## Files to Look At

- `src/prime_rl/configs/inference.py` — Add deployment, slurm, output_dir, dry_run config fields
- `pyproject.toml` — Update the inference console script entrypoint
- `skills/inference-server/SKILL.md` — Document SLURM inference capabilities
- `src/prime_rl/entrypoints/` — Create new inference.py entrypoint here
- `src/prime_rl/templates/` — Create inference.sbatch.j2 template here

## Notes

- Follow the same patterns used by the existing `rl` and `sft` entrypoints in `src/prime_rl/entrypoints/`
- The `skills/inference-server/SKILL.md` file is a key agent instruction file that must be kept accurate when changing inference-related code
- Multi-node inference should run independent vLLM replicas on each node (no cross-node parallelism)
- The project uses `pydantic_config` with TOML configs and `@` syntax for config loading
