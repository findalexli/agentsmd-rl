import re
from pathlib import Path

# 1. Update test_outputs.py
test_py = Path("/workspace/task/tests/test_outputs.py")
content = test_py.read_text()

# Find where repo_tests start
start_idx = content.find("# ---------------------------------------------------------------------------\n# Pass-to-pass (repo_tests)")
if start_idx != -1:
    content = content[:start_idx]

# Append the new repo_tests
new_tests = """# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_skill_index():
    \"\"\"Syntax check skill/index.ts (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/src/skill/index.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_discovery_test():
    \"\"\"Syntax check test/skill/discovery.test.ts (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/skill/discovery.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_skill_test():
    \"\"\"Syntax check test/skill/skill.test.ts (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/skill/skill.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_tool_skill_test():
    \"\"\"Syntax check test/tool/skill.test.ts (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/tool/skill.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\\n{r.stderr}"
"""
test_py.write_text(content + new_tests)

# 2. Update eval_manifest.yaml
yaml_file = Path("/workspace/task/eval_manifest.yaml")
yaml_content = yaml_file.read_text()

# Find where repo_tests start
start_idx_yaml = yaml_content.find("  # --- Pass-to-pass: Repo CI/CD tests ---")
if start_idx_yaml != -1:
    # Also find the rubric section to keep it
    rubric_idx = yaml_content.find("rubric:")
    rubric_content = yaml_content[rubric_idx:] if rubric_idx != -1 else ""
    yaml_content = yaml_content[:start_idx_yaml]

new_yaml_tests = """  # --- Pass-to-pass: Repo CI/CD tests ---
  - id: test_repo_syntax_skill_index
    type: pass_to_pass
    origin: repo_tests
    description: "Syntax check skill/index.ts using Node.js"

  - id: test_repo_syntax_discovery_test
    type: pass_to_pass
    origin: repo_tests
    description: "Syntax check test/skill/discovery.test.ts using Node.js"

  - id: test_repo_syntax_skill_test
    type: pass_to_pass
    origin: repo_tests
    description: "Syntax check test/skill/skill.test.ts using Node.js"

  - id: test_repo_syntax_tool_skill_test
    type: pass_to_pass
    origin: repo_tests
    description: "Syntax check test/tool/skill.test.ts using Node.js"

"""
if rubric_idx != -1:
    yaml_file.write_text(yaml_content + new_yaml_tests + rubric_content)
else:
    yaml_file.write_text(yaml_content + new_yaml_tests)

print("Tests updated successfully.")
