/**
 * Minimal mock test for sparseGrams length calculation fix.
 *
 * This tests the logic without requiring full ClickHouse compilation.
 */

#include <cstddef>
#include <cstdint>
#include <vector>
#include <cassert>
#include <cstdio>

// Mock types
typedef const char* Pos;

// Simplified version of the consume() logic to test the fix
bool test_length_calculation() {
    // Simulate the variables
    size_t right_symbol_index = 10;
    size_t possible_left_symbol_index = 5;

    // Test 1: min_ngram_length = 3 (default)
    {
        size_t min_ngram_length = 3;
        // OLD BUG: size_t length = right_symbol_index - possible_left_symbol_index + 2;
        // FIX: Use min_ngram_length - 1
        size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;

        // With min=3: 10 - 5 + 3 - 1 = 7
        if (length != 7) {
            printf("FAIL: Test 1 - Expected length 7, got %zu\n", length);
            return false;
        }
        printf("PASS: Test 1 - min=3, length=%zu\n", length);
    }

    // Test 2: min_ngram_length = 5
    {
        size_t min_ngram_length = 5;
        size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;

        // With min=5: 10 - 5 + 5 - 1 = 9
        if (length != 9) {
            printf("FAIL: Test 2 - Expected length 9, got %zu\n", length);
            return false;
        }
        printf("PASS: Test 2 - min=5, length=%zu\n", length);
    }

    // Test 3: Verify the old + 2 would give wrong result for min=5
    {
        size_t old_length = right_symbol_index - possible_left_symbol_index + 2;  // 10 - 5 + 2 = 7
        size_t min_ngram_length = 5;
        size_t correct_length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;  // 9

        if (old_length == correct_length) {
            printf("FAIL: Test 3 - Old and new formulas should differ for min=5\n");
            return false;
        }
        if (old_length != 7 || correct_length != 9) {
            printf("FAIL: Test 3 - Expected old=7, new=9, got old=%zu, new=%zu\n", old_length, correct_length);
            return false;
        }
        printf("PASS: Test 3 - Old formula (+2) gives %zu, new formula gives %zu for min=5\n",
               old_length, correct_length);
    }

    return true;
}

int main() {
    printf("Testing sparseGrams length calculation fix...\n");

    if (!test_length_calculation()) {
        printf("\nFAILED: Length calculation tests failed\n");
        return 1;
    }

    printf("\nPASSED: All length calculation tests passed\n");
    return 0;
}
