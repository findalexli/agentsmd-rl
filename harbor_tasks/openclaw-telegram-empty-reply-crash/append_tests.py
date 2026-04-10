import os

with open("/workspace/task/tests/test_outputs.py", "a") as f:
    f.write("""
# [repo_tests] pass_to_pass
def test_repo_delivery_resolve_media_retry():
    \"\"\"Repo's delivery resolve-media-retry tests pass (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/bot/delivery.resolve-media-retry.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Delivery resolve-media-retry tests failed:\\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_helpers():
    \"\"\"Repo's helpers tests pass (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/bot/helpers.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Helpers tests failed:\\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_lane_delivery():
    \"\"\"Repo's lane delivery tests pass (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/lane-delivery.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lane delivery tests failed:\\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_send():
    \"\"\"Repo's send tests pass (pass_to_pass).\"\"\"
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/send.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Send tests failed:\\n{r.stdout[-1000:]}{r.stderr[-500:]}"
""")
