#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q "let indent = indent.trim_start_matches.*x0C" crates/ruff_python_trivia/src/textwrap.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix 1: textwrap.rs - add the form feed stripping at start of dedent_to
cat > /tmp/fix_textwrap.py << 'PYEOF'
import re

with open('crates/ruff_python_trivia/src/textwrap.rs', 'r') as f:
    content = f.read()

# Add the fix after the function signature
old_text = """pub fn dedent_to(text: &str, indent: &str) -> Option<String> {
    // Look at the indentation of the first non-empty line, to determine the \"baseline\" indentation."""

new_text = """pub fn dedent_to(text: &str, indent: &str) -> Option<String> {
    // The caller may provide an `indent` from source code by taking
    // a range of text beginning with the start of a line. In Python,
    // while a line may begin with form feeds, these do not contribute
    // to the indentation. So we strip those here.
    let indent = indent.trim_start_matches('\\x0C');
    // Look at the indentation of the first non-empty line, to determine the \"baseline\" indentation."""

if "let indent = indent.trim_start_matches" not in content:
    content = content.replace(old_text, new_text)
    print("Fixed textwrap.rs")
else:
    print("textwrap.rs already fixed")

# Add the unit test at the very end of the file, inside the tests module
# Find the last function and add after its closing brace
test_code = '''

    #[test]
    #[rustfmt::skip]
    fn dedent_to_ignores_leading_form_feeds_in_provided_indentation() {
        let x = [
            "  1",
            "  2",
        ].join("\\n");
        let y = [
            "1",
            "2",
        ].join("\\n");
        assert_eq!(dedent_to(&x, "\\x0c\\x0c"), Some(y));
    }
'''

if 'dedent_to_ignores_leading_form_feeds_in_provided_indentation' not in content:
    # Find the last test function closing and add before the final module close
    # The file ends with "}\n}" (closing function then closing mod tests)
    # We need to find where to insert our test

    # Strategy: find the last non-empty line that is just "    }" (4 spaces + })
    # which closes the last test function
    lines = content.split('\n')

    # Find the last line that is exactly "    }" (4 spaces closing brace)
    # which closes a test function
    insert_pos = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i] == '    }':
            insert_pos = i + 1
            break

    if insert_pos:
        lines.insert(insert_pos, test_code.rstrip())
        content = '\n'.join(lines)
        with open('crates/ruff_python_trivia/src/textwrap.rs', 'w') as f:
            f.write(content)
        print("Added unit test to textwrap.rs")
    else:
        print("Could not find insertion point for test")
else:
    print("Unit test already exists")

PYEOF

python3 /tmp/fix_textwrap.py

# Run cargo fmt to ensure formatting is correct
cargo fmt -- crates/ruff_python_trivia/src/textwrap.rs

# Fix 2: Add regression test fixture
fixture_file='crates/ruff_linter/resources/test/fixtures/ruff/RUF072.py'
if ! grep -q 'try is preceded by a form feed below' "$fixture_file" 2>/dev/null; then
    # Need to add a form feed character before try
    printf '\n\n# Regression test for https://github.com/astral-sh/ruff/issues/24373\n# (`try` is preceded by a form feed below)\n\x0ctry:\n    1\nfinally:\n    pass\n' >> "$fixture_file"
    echo "Added regression test fixture"
else
    echo "Regression test fixture already present"
fi

echo "Patch applied successfully."
