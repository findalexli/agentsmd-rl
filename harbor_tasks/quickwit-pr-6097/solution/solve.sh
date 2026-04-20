#!/bin/bash
set -e

cd /workspace/quickwit/quickwit

# Apply the fix using Python
python3 << 'PYTHON_SCRIPT'
with open('quickwit-query/src/elastic_query_dsl/terms_query.rs', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Insert TermValue enum before line 40 (#[derive(Deserialize)] for OneOrMany)
    if line.strip() == '#[derive(Deserialize)]' and i + 1 < len(lines) and lines[i+1].strip() == '#[serde(untagged)]':
        # Check if this is the OneOrMany enum (not TermsQueryForSerialization which comes before it)
        # TermsQueryForSerialization ends at line ~38, OneOrMany starts at line 40
        # We look ahead to see if 'enum OneOrMany' follows
        if i + 2 < len(lines) and 'enum OneOrMany' in lines[i+2]:
            # Insert TermValue enum
            new_lines.append('#[derive(Deserialize)]\n')
            new_lines.append('#[serde(untagged)]\n')
            new_lines.append('enum TermValue {\n')
            new_lines.append('    I64(i64),\n')
            new_lines.append('    U64(u64),\n')
            new_lines.append('    Str(String),\n')
            new_lines.append('}\n')
            new_lines.append('\n')
            new_lines.append('impl From<TermValue> for String {\n')
            new_lines.append('    fn from(term_value: TermValue) -> String {\n')
            new_lines.append('        match term_value {\n')
            new_lines.append('            TermValue::I64(val) => val.to_string(),\n')
            new_lines.append('            TermValue::U64(val) => val.to_string(),\n')
            new_lines.append('            TermValue::Str(val) => val,\n')
            new_lines.append('        }\n')
            new_lines.append('    }\n')
            new_lines.append('}\n')
            new_lines.append('\n')

    # Change One(String) to One(TermValue)
    if 'One(String)' in line:
        line = line.replace('One(String)', 'One(TermValue)')

    # Change Many(Vec<String>) to Many(Vec<TermValue>)
    if 'Many(Vec<String>)' in line:
        line = line.replace('Many(Vec<String>)', 'Many(Vec<TermValue>)')

    # Update vec![one_value] to vec![String::from(one_value)]
    if 'vec![one_value]' in line:
        line = line.replace('vec![one_value]', 'vec![String::from(one_value)]')

    # Update values (in the Many case)
    if 'OneOrMany::Many(values) => values,' in line:
        line = line.replace('OneOrMany::Many(values) => values,', 'OneOrMany::Many(values) => values.into_iter().map(String::from).collect(),')

    # Insert the new test after the test_terms_query_simple closing brace
    if '        assert_eq!(&terms_query.values[..], &["hello".to_string()]);' in line:
        new_lines.append(line)
        new_lines.append('    }\n')
        new_lines.append('\n')
        new_lines.append('    #[test]\n')
        new_lines.append('    fn test_terms_query_not_string() {\n')
        new_lines.append('        let terms_query_json = r#"{ "user.id": [1, 2] }"#;\n')
        new_lines.append('        let terms_query: TermsQuery = serde_json::from_str(terms_query_json).unwrap();\n')
        new_lines.append('        assert_eq!(&terms_query.field, "user.id");\n')
        new_lines.append('        assert_eq!(&terms_query.values[..], &["1".to_string(), "2".to_string()]);\n')
        new_lines.append('    }\n')
        # Skip the original closing brace since we just added it
        i += 1
        if i < len(lines) and lines[i].strip() == '}':
            i += 1  # Skip the closing brace - we added it above
            continue
    elif line.strip() == '}' and i > 0 and 'test_terms_query_simple' in lines[i-1]:
        # Skip - we already handled this
        pass
    elif line.strip() == '}' and i > 0 and 'fn test_terms_query_simple' in lines[i-1]:
        # Skip - we already handled this
        pass

    new_lines.append(line)
    i += 1

with open('quickwit-query/src/elastic_query_dsl/terms_query.rs', 'w') as f:
    f.writelines(new_lines)

print("Patch applied successfully")
PYTHON_SCRIPT

# Verify idempotency - check for distinctive line from patch
grep -q "TermValue::I64(val)" quickwit-query/src/elastic_query_dsl/terms_query.rs