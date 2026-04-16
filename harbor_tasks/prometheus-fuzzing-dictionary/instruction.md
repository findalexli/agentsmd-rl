# Add libFuzzer dictionary generation for FuzzParseExpr

The Prometheus project needs to improve fuzzing coverage for the PromQL expression parser. Currently, the `FuzzParseExpr` fuzzer produces limited interesting output because it lacks a structured dictionary of PromQL tokens.

## Your Task

Implement functionality that:

1. **Exports PromQL keywords**: Add a `Keywords()` function in `promql/parser/lex.go` that returns all keyword strings recognized by the PromQL lexer. This should include aggregation operators (sum, avg, count, etc.), modifier keywords (by, without, etc.), histogram descriptor keys, and counter-reset hint values.

2. **Generates dictionary tokens**: Add a `GetDictForFuzzParseExpr()` function in `util/fuzzing/corpus.go` that returns a slice of strings containing:
   - All PromQL keywords (via the new `Keywords()` function)
   - All built-in function names from `parser.Functions`
   - Operator and syntax tokens from `parser.ItemTypeStr` (excluding display-only placeholders like `<space>`)
   - Special numeric literals: +Inf, -Inf, NaN

3. **Generates dictionary files**: Add a `generateDictFile()` function in `util/fuzzing/corpus_gen/main.go` that:
   - Takes a fuzz name and slice of tokens
   - Sorts tokens deterministically
   - Writes each token as a quoted string on its own line to a `.dict` file in the parent directory
   - Returns any errors encountered

4. **Integrates into corpus generation**: Update the main function in `util/fuzzing/corpus_gen/main.go` to call `GetDictForFuzzParseExpr()` and generate the dictionary file alongside the existing seed corpus generation.

## Requirements

- All exported functions must have proper Go doc comments starting with the function name and ending with a period
- The solution must compile and integrate with the existing corpus generation infrastructure
- The dictionary should be comprehensive, covering all PromQL keywords, functions, operators, and special literals

## Relevant Files

- `promql/parser/lex.go` - PromQL lexer with keyword maps
- `util/fuzzing/corpus.go` - fuzzing utilities and corpus generation
- `util/fuzzing/corpus_gen/main.go` - corpus generator tool
