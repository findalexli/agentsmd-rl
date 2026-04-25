import os
import shutil

# Change eval_manifest.yaml ownership
manifest_path = '/workspace/task/eval_manifest.yaml'
backup_path = '/workspace/task/eval_manifest_old.yaml'

if os.path.exists(manifest_path):
    shutil.copy2(manifest_path, backup_path)
    os.remove(manifest_path)
    shutil.copy2(backup_path, manifest_path)
    print("Changed ownership of eval_manifest.yaml")

# Read test_outputs.py
test_outputs_path = '/workspace/task/tests/test_outputs.py'
with open(test_outputs_path, 'r') as f:
    content = f.read()

# Replace test_repo_cascader_tests with the three new tests
old_func = '''def test_repo_cascader_tests():
    """Repo's Cascader component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=cascader", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader tests failed:\\n{r.stderr[-500:]}"'''

new_funcs = '''def test_repo_cascader_index_tests():
    """Repo's Cascader index component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/index.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader index tests failed:\\n{r.stderr[-500:]}"


def test_repo_cascader_demo_tests():
    """Repo's Cascader demo tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/demo.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader demo tests failed:\\n{r.stderr[-500:]}"


def test_repo_cascader_a11y_tests():
    """Repo's Cascader a11y tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/a11y.test.ts", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader a11y tests failed:\\n{r.stderr[-500:]}"'''

content = content.replace(old_func, new_funcs)

# Update the calculate_reward list
old_list_item = "test_repo_cascader_tests,"
new_list_items = """test_repo_cascader_index_tests,
        test_repo_cascader_demo_tests,
        test_repo_cascader_a11y_tests,"""

content = content.replace(old_list_item, new_list_items)

with open(test_outputs_path, 'w') as f:
    f.write(content)
print("Updated test_outputs.py")

# Update eval_manifest.yaml
with open(manifest_path, 'r') as f:
    manifest_content = f.read()

old_manifest = """  - id: "repo_cascader_tests"
    description: "Repo Cascader component tests pass (npm test -- --testPathPatterns=cascader --maxWorkers=1 --testTimeout=60000)"
    test: "test_repo_cascader_tests"
    type: pass_to_pass
    origin: repo_tests
    weight: 0.1"""

new_manifest = """  - id: "repo_cascader_index_tests"
    description: "Repo Cascader index component tests pass"
    test: "test_repo_cascader_index_tests"
    type: pass_to_pass
    origin: repo_tests
    weight: 0.04

  - id: "repo_cascader_demo_tests"
    description: "Repo Cascader demo tests pass"
    test: "test_repo_cascader_demo_tests"
    type: pass_to_pass
    origin: repo_tests
    weight: 0.04

  - id: "repo_cascader_a11y_tests"
    description: "Repo Cascader a11y tests pass"
    test: "test_repo_cascader_a11y_tests"
    type: pass_to_pass
    origin: repo_tests
    weight: 0.02"""

manifest_content = manifest_content.replace(old_manifest, new_manifest)

with open(manifest_path, 'w') as f:
    f.write(manifest_content)
print("Updated eval_manifest.yaml")
