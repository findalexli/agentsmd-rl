#!/bin/bash
set -e

cd /workspace/ClickHouse

# Idempotency check: verify if fix is already applied
if grep -q "Renumber part_index_in_query to be contiguous" src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp 2>/dev/null; then
    echo "Fix already applied, skipping patch"
    exit 0
fi

# Apply the fix using Python
python3 << 'PYTHON_EOF'
import re

TARGET_FILE = "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"

with open(TARGET_FILE, 'r') as f:
    content = f.read()

# The buggy pattern to replace:
#         size_t added_parts = all_parts.size();
#         for (const auto & part : analysis_result->parts_with_ranges)
#         {
#             all_parts.push_back(part);
#             all_parts.back().part_index_in_query += added_parts;
#         }

old_pattern = r'''(size_t added_parts = all_parts\.size\(\);)
        for \(const auto & part : analysis_result->parts_with_ranges\)
        \{
            all_parts\.push_back\(part\);
            all_parts\.back\(\)\.part_index_in_query \+= added_parts;'''

new_code = '''size_t added_parts = all_parts.size();
        /// Renumber part_index_in_query to be contiguous starting from added_parts.
        /// filterPartsByQueryConditionCache may drop parts from selectRangesToRead(),
        /// leaving non-contiguous part_index_in_query values. The distribution logic
        /// below assumes contiguous indices to assign parts back to their sources.
        for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
        {
            all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);
            all_parts.back().part_index_in_query = added_parts + local_idx;'''

# Use re.DOTALL to make . match newlines
new_content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

if new_content == content:
    print("WARNING: Pattern not found, trying alternative approach")
    # Try a simpler line-by-line replacement
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'size_t added_parts = all_parts.size();' in line and i + 4 < len(lines):
            # Found the anchor line, check if next lines match the buggy pattern
            if ('for (const auto & part : analysis_result->parts_with_ranges)' in lines[i+1] and
                'all_parts.push_back(part);' in lines[i+3] and
                'all_parts.back().part_index_in_query += added_parts;' in lines[i+4]):
                # Insert the fixed code
                new_lines.append(line)  # size_t added_parts = all_parts.size();
                new_lines.append('        /// Renumber part_index_in_query to be contiguous starting from added_parts.')
                new_lines.append('        /// filterPartsByQueryConditionCache may drop parts from selectRangesToRead(),')
                new_lines.append('        /// leaving non-contiguous part_index_in_query values. The distribution logic')
                new_lines.append('        /// below assumes contiguous indices to assign parts back to their sources.')
                new_lines.append('        for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)')
                new_lines.append(lines[i+2])  # {
                new_lines.append('            all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);')
                new_lines.append('            all_parts.back().part_index_in_query = added_parts + local_idx;')
                i += 5  # Skip the original 5 lines
                continue
        new_lines.append(line)
        i += 1
    new_content = '\n'.join(new_lines)

with open(TARGET_FILE, 'w') as f:
    f.write(new_content)

print("Fix applied successfully")
PYTHON_EOF

echo "Fix applied successfully"
