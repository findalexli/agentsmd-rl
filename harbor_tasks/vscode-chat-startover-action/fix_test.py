import re

with open('/workspace/task/tests_fixed/test_outputs.py', 'r') as f:
    content = f.read()

# The pattern to find test_repo_action_patterns - let's be flexible
old_pattern = r'def test_repo_action_patterns\(\):\s+r = _run_node\("""const fs=require\("fs"\);const s=fs.readFileSync\(process\.argv\[2\],"utf8"\);const a=\[\.\.\.s\.matchAll\(/class\\\\s\+\(\\\\w\+\)Action\\\\s\+extends\\\\s\+Action2/g\)\];for\(const m of a\)\{const n=m\[1\];if\(!s\.includes\("registerAction2\(class "\+n\+"Action"\)\)throw new Error\(n\);\}for\(const i of\["Action2","registerAction2","MenuId"\]\)if\(!s\.includes\(i\)\)throw new Error\(i\);console\.log\("PASS"\);""", file_path=CHAT_EDITING_ACTIONS\)'

# Read the actual content to see what's there
with open('/workspace/task/tests_fixed/test_outputs.py', 'r') as f:
    lines = f.readlines()

# Find the line with test_repo_action_patterns and print it
for i, line in enumerate(lines):
    if 'def test_repo_action_patterns' in line:
        print(f"Line {i+1}: {repr(lines[i])}")
        if i+1 < len(lines):
            print(f"Line {i+2}: {repr(lines[i+1])[:200]}")
        break
