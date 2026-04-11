#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already applied (look for the specific pattern in length calculation)
if grep -q "size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;" src/Functions/sparseGramsImpl.h; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using sed
sed -i 's/right_symbol_index - possible_left_symbol_index + 2;/right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;/g' src/Functions/sparseGramsImpl.h

echo "Patch applied successfully"
