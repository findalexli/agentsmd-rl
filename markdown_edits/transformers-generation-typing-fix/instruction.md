# Add Type Checking Support to Transformers Generation Module

The transformers library is extending type checking coverage to the `src/transformers/generation` module. You need to implement the necessary changes to support this effort.

## Code Changes Required

1. **Create a type checking wrapper script** at `utils/check_types.py` that:
   - Accepts directory paths as arguments
   - Runs the `ty` type checker on those directories with appropriate exclusions
   - Returns the proper exit code

2. **Reorganize the typing module**:
   - Move `src/transformers/utils/_typing.py` to `src/transformers/_typing.py` (root level)
   - Update the import in `src/transformers/utils/logging.py` to reflect the new location
   - Add new protocol classes to the typing module:
     - `GenerativePreTrainedModel` - Protocol documenting the interface that GenerationMixin expects from its host class
     - `WhisperGenerationConfigLike` - Protocol for Whisper-specific generation config fields

3. **Add type annotations to generation module**:
   - Update `src/transformers/generation/utils.py` with proper `self: GenerativePreTrainedModel` annotations on methods
   - Add type annotations to `candidate_generator.py`, `streamers.py`, `configuration_utils.py`, `logits_process.py`, `stopping_criteria.py`, and `watermarking.py`
   - Use `typing.cast()` where type narrowing is needed
   - Fix `torch.tensor` → `torch.Tensor` type annotations where applicable

4. **Align model signatures** in:
   - `src/transformers/models/clvp/modeling_clvp.py`
   - `src/transformers/models/musicgen/modeling_musicgen.py`
   - `src/transformers/models/musicgen_melody/modeling_musicgen_melody.py`

5. **Update the Makefile**:
   - Replace direct `ty check` invocations with calls to `utils/check_types.py`
   - Define a `ty_check_dirs` variable listing directories to type-check
   - Update both `style` and `check-repo` targets

## Documentation Update Required

**Update `AGENTS.md`** to reflect the new type checking workflow:
- The `make style` command description should be updated to mention that it now runs the type checker in addition to formatters and linters

## Notes

- The `GenerativePreTrainedModel` protocol is for type checking only (not runtime) and should document attributes like `config`, `device`, `dtype`, and methods like `forward`, `can_generate`, etc.
- The type checking infrastructure uses the `ty` tool, but your wrapper script should handle its invocation
- When updating imports, be careful about relative import paths (e.g., `.._typing` vs `._typing`)
- The copyright year in the moved _typing.py should be updated to 2026

Run your changes with `python -m pytest` to verify the type annotations and structural changes are correct.
