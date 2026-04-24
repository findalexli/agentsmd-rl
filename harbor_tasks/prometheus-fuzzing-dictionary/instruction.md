# Add libFuzzer dictionary generation for FuzzParseExpr

The Prometheus project needs to improve fuzzing coverage for the PromQL expression parser. Currently, the `FuzzParseExpr` fuzzer produces limited interesting output because it lacks a structured dictionary of PromQL tokens.

## Your Task

The goal is to generate a libFuzzer dictionary file (`fuzzParseExpr.dict`) that the `FuzzParseExpr` fuzzer can use to produce more interesting test inputs. The dictionary should contain all valid PromQL tokens that the fuzzer can emit.

### Required Exported Functions

Implement two exported Go functions:

1. **`promql/parser.Keywords() []string`** — returns all keyword strings recognized by the PromQL lexer, including aggregation operators (`sum`, `avg`, `count`, `min`, `max`), modifier keywords (`by`, `without`), histogram descriptor keys, and counter-reset hint values.

2. **`util/fuzzing.GetDictForFuzzParseExpr() []string`** — returns all libFuzzer dictionary tokens for `FuzzParseExpr`, derived from PromQL keywords, built-in function names, operator symbols, and special numeric literals (`+Inf`, `-Inf`, `NaN`).

Both functions must have proper Go doc comments.

### Expected Dictionary Contents

The generated `fuzzParseExpr.dict` file should include:

1. **PromQL keywords** — all keyword strings recognized by the lexer (aggregation operators like `sum`, `avg`, `count`, modifier keywords like `by`, `without`, histogram descriptor keys, and counter-reset hint values)

2. **Built-in function names** — all PromQL built-in functions (e.g., `rate`, `sum`, `avg`, `increase`, `histogram_quantile`)

3. **Operators and syntax tokens** — lexer tokens for operators and syntactic elements

4. **Special numeric literals** — `+Inf`, `-Inf`, `NaN`

### Integration

The corpus generation tool (`util/fuzzing/corpus_gen/`) should generate the dictionary file alongside the existing seed corpus. The output should be a `.dict` file in libFuzzer format, with one quoted string per line, sorted alphabetically for deterministic output.

### Requirements

- All exported functions must have proper Go doc comments
- The solution must compile without errors
- The corpus generator should produce the dictionary file when run

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
