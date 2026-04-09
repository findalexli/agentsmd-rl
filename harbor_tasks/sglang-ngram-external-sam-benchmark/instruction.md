# [Spec][Ngram] Add output-as-corpus accept length benchmark for external SAM

## Problem

The ngram speculative decoding test file needs refactoring to improve the external SAM (Speculative Accept Model) test coverage:

1. **Redundant test class**: `TestNgramExternalSamSmoke` provides basic smoke tests but doesn't validate that external SAM actually improves accept length
2. **Missing benchmark test**: There's no end-to-end test proving that using generated outputs as a corpus boosts speculative decoding accept length
3. **Unused code**: The file contains unused imports (`json`, `os`, `tempfile`) and helper functions (`_safe_remove`, `_safe_kill_process`) that are no longer needed

## Expected Behavior

Refactor `test/registered/spec/test_ngram_speculative_decoding.py` to:

1. **Remove the redundant `TestNgramExternalSamSmoke` class** - it tests basic functionality that's now covered elsewhere
2. **Add `test_output_as_corpus_boosts_accept_length` method** to `TestNgramSpeculativeDecodingFlashinfer` that:
   - Generates outputs with temperature=0 (baseline, trie only)
   - Calls `/add_external_corpus` HTTP endpoint with generated outputs
   - Regenerates same prompts and asserts SAM accept length >= 2x baseline
3. **Update server args** in `TestNgramSpeculativeDecodingFlashinfer.get_server_args()` to include `--speculative-ngram-external-sam-budget 8`
4. **Clean up unused imports and helpers** - remove `json`, `os`, `tempfile`, `_safe_remove`, `_safe_kill_process`, and `EXTERNAL_SAM_CORPUS_RECORDS`

## Files to Look At

- `test/registered/spec/test_ngram_speculative_decoding.py` — Main test file containing the ngram speculative decoding test classes
