import tempfile, subprocess, sys, os

# This is the exact code pattern from test_outputs.py
code = """
import re
from pathlib import Path
from dataclasses import fields

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r'(@dataclass[^\n]*\nclass TrackioConfig:.*?)(?=\n@dataclass|\nclass \w)'
match = re.search(pattern, src, re.DOTALL)

if not match:
    print("FAIL: Could not find TrackioConfig class in cli_args.py")
    exit(1)

ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\n" + match.group(1), ns)
TrackioConfig = ns["TrackioConfig"]

field_names = {f.name for f in fields(TrackioConfig)}
required = {"mode", "project", "name", "space_id"}
missing = required - field_names
if missing:
    print(f"FAIL: Missing fields: {missing}")
    exit(1)
print("PASS: All required fields present")
"""

with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write(code)
    tmp_path = f.name

print("Written code to:", tmp_path)
with open(tmp_path, 'r') as f:
    print("Actual file content:")
    print(repr(f.read()[:500]))

try:
    result = subprocess.run(
        [sys.executable, tmp_path],
        capture_output=True,
        text=True,
        timeout=30,
        cwd="/workspace/AReaL",
        env={**os.environ, "PYTHONPATH": "/workspace/AReaL"}
    )
    print("RC:", result.returncode)
    print("STDOUT:", result.stdout[:500])
    print("STDERR:", result.stderr[:500])
finally:
    os.unlink(tmp_path)