#!/bin/bash
set -e

cd /workspace/prometheus

# Check if already patched (idempotency check)
if grep -q "Keywords returns all keyword strings" promql/parser/lex.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Add Keywords() function to promql/parser/lex.go after the init() function
cat > /tmp/keywords_func.txt << 'EOF'

// Keywords returns all keyword strings recognised by the PromQL lexer,
// including aggregation operators, modifier keywords, histogram descriptor
// keys, and counter-reset hint values.
func Keywords() []string {
	seen := make(map[string]struct{})
	for s := range key {
		seen[s] = struct{}{}
	}
	for s := range histogramDesc {
		seen[s] = struct{}{}
	}
	for s := range counterResetHints {
		seen[s] = struct{}{}
	}
	result := make([]string, 0, len(seen))
	for s := range seen {
		result = append(result, s)
	}
	return result
}
EOF

# Insert Keywords() after the init() function in lex.go
awk '
/^func init\(\)/ { in_init=1 }
in_init && /^}$/ {
    print
    while ((getline line < "/tmp/keywords_func.txt") > 0) {
        print line
    }
    close("/tmp/keywords_func.txt")
    in_init=0
    next
}
{ print }
' promql/parser/lex.go > /tmp/lex.go.new && mv /tmp/lex.go.new promql/parser/lex.go

# Add import to util/fuzzing/corpus.go if not present
if ! grep -q '"github.com/prometheus/prometheus/promql/parser"' util/fuzzing/corpus.go; then
    sed -i 's|import (|import (\n\t"github.com/prometheus/prometheus/promql/parser"|' util/fuzzing/corpus.go
fi

# Add GetDictForFuzzParseExpr() function to util/fuzzing/corpus.go
cat > /tmp/dict_func.txt << 'EOF'

// GetDictForFuzzParseExpr returns the libFuzzer dictionary tokens for
// FuzzParseExpr. Tokens are derived from the exported PromQL keyword list,
// function names, and operator symbols so that the dictionary stays in sync
// with the grammar automatically.
func GetDictForFuzzParseExpr() []string {
	seen := make(map[string]struct{})

	// All PromQL keywords (aggregators, modifiers, histogram descriptors, etc.).
	for _, kw := range parser.Keywords() {
		seen[kw] = struct{}{}
	}

	// All built-in function names.
	for name := range parser.Functions {
		seen[name] = struct{}{}
	}

	// Operator and syntax tokens from ItemTypeStr. The SPACE entry is a
	// display-only placeholder ("<space>"), not an actual token, so remove it.
	for _, s := range parser.ItemTypeStr {
		seen[s] = struct{}{}
	}
	delete(seen, parser.ItemTypeStr[parser.SPACE])

	// Special numeric literals not covered by the keyword map.
	for _, s := range []string{"+Inf", "-Inf", "NaN"} {
		seen[s] = struct{}{}
	}

	result := make([]string, 0, len(seen))
	for s := range seen {
		result = append(result, s)
	}
	return result
}
EOF

# Insert GetDictForFuzzParseExpr() before GetCorpusForFuzzXOR2Chunk in corpus.go
awk '
/^func GetCorpusForFuzzXOR2Chunk/ {
    while ((getline line < "/tmp/dict_func.txt") > 0) {
        print line
    }
    close("/tmp/dict_func.txt")
}
{ print }
' util/fuzzing/corpus.go > /tmp/corpus.go.new && mv /tmp/corpus.go.new util/fuzzing/corpus.go

# Update corpus_gen/main.go - change the message
sed -i 's|Successfully generated all seed corpus ZIP files\.|Successfully generated all seed corpus ZIP files and dictionary files.|' util/fuzzing/corpus_gen/main.go

# Add generateDictFile() and the call to it in corpus_gen/main.go
cat > /tmp/dict_gen.txt << 'EOF'

// generateDictFile writes a libFuzzer dictionary file to the parent directory.
// Each token is written as a quoted string on its own line, sorted
// deterministically so the output is stable across runs.
func generateDictFile(fuzzName string, tokens []string) error {
	sorted := make([]string, len(tokens))
	copy(sorted, tokens)
	sort.Strings(sorted)

	dictPath := filepath.Join("..", fuzzName+".dict")
	f, err := os.Create(dictPath)
	if err != nil {
		return fmt.Errorf("failed to create dict file: %w", err)
	}
	defer f.Close()

	for _, token := range sorted {
		if _, err := fmt.Fprintf(f, "%q\n", token); err != nil {
			return fmt.Errorf("failed to write dict entry %q: %w", token, err)
		}
	}
	return nil
}
EOF

# Insert generateDictFile() at the end of corpus_gen/main.go (before the last closing brace if needed)
# Actually append it to the file
cat /tmp/dict_gen.txt >> util/fuzzing/corpus_gen/main.go

# Add the call to generateDictFile in run() function - after generating fuzzParseExpr corpus
# Find the line with "Generated fuzzParseExpr_seed_corpus.zip" and add after it
awk '
/Generated fuzzParseExpr_seed_corpus\.zip/ {
    print
    print ""
    print "\t// Generate FuzzParseExpr dictionary."
    print "\tdict := fuzzing.GetDictForFuzzParseExpr()"
    print "\tif err := generateDictFile(\"fuzzParseExpr\", dict); err != nil {"
    print "\t\treturn fmt.Errorf(\"failed to generate fuzzParseExpr.dict: %w\", err)"
    print "\t}"
    print "\tfmt.Printf(\"Generated fuzzParseExpr.dict with %d entries.\\n\", len(dict))"
    next
}
{ print }
' util/fuzzing/corpus_gen/main.go > /tmp/main.go.new && mv /tmp/main.go.new util/fuzzing/corpus_gen/main.go

echo "Patch applied successfully"
