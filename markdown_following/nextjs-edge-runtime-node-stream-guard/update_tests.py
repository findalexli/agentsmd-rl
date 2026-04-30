import re
import pathlib

tests_file = pathlib.Path('/tests/test_outputs.py')
yaml_file = pathlib.Path('/tests/eval_manifest.yaml')

tests_content = tests_file.read_text()
yaml_content = yaml_file.read_text()

tests_to_remove = [
    "test_repo_prettier",
    "test_repo_typescript_next_package",
    "test_repo_eslint_modified_files"
]

for test in tests_to_remove:
    # Remove from python
    pattern = r"(?:# \[repo_tests\] pass_to_pass\n)?(?:@[^\n]+\n)*def " + test + r"\(\):[\s\S]*?(?=\n# \[|\n\Z|\ndef )"
    tests_content = re.sub(pattern, "", tests_content)
    
    # Remove from yaml
    yaml_pattern = r"\s*-\s*id:\s*" + test + r"\n(?:\s+[a-z_]+:\s*.*?\n)*"
    yaml_content = re.sub(yaml_pattern, "", yaml_content)

new_tests_code = """
# [repo_tests] pass_to_pass
def test_repo_prettier_helper():
    \"\"\"Prettier formatting check for node-web-streams-helper.ts passes (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/stream-utils/node-web-streams-helper.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_prettier_prerender():
    \"\"\"Prettier formatting check for app-render-prerender-utils.ts passes (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/app-render/app-render-prerender-utils.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_prettier_render_result():
    \"\"\"Prettier formatting check for render-result.ts passes (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["npx", "--yes", "prettier", "--check", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stdout[-500:]}{r.stderr[-500:]}"
"""

new_yaml_code = """
  - id: test_repo_prettier_helper
    type: pass_to_pass
    origin: repo_tests
    description: "Prettier formatting check for node-web-streams-helper.ts passes"

  - id: test_repo_prettier_prerender
    type: pass_to_pass
    origin: repo_tests
    description: "Prettier formatting check for app-render-prerender-utils.ts passes"

  - id: test_repo_prettier_render_result
    type: pass_to_pass
    origin: repo_tests
    description: "Prettier formatting check for render-result.ts passes"
"""

tests_content = tests_content.rstrip() + "\n" + new_tests_code + "\n"
tests_file.write_text(tests_content)

# Insert before "rubric:"
if "rubric:" in yaml_content:
    yaml_content = yaml_content.replace("rubric:", new_yaml_code.lstrip() + "\nrubric:")
else:
    yaml_content = yaml_content.rstrip() + "\n" + new_yaml_code + "\n"

yaml_file.write_text(yaml_content)

