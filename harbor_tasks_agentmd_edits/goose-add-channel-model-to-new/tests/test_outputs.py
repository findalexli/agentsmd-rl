"""
Task: goose-add-channel-model-to-new
Repo: goose-lang/goose @ 3be88bbb4982f58e5813b6f0344302d5582c8e8a
PR:   94

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/goose"


def _run(cmd: list, timeout: int = 60, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_go_mod_deps_added():
    """go.mod must include goose-lang/primitive and goose-lang/std dependencies."""
    r = _run(["python3", "-c", f"""
import sys

with open("{REPO}/go.mod") as f:
    content = f.read()

if "github.com/goose-lang/primitive" not in content:
    print("FAIL: go.mod missing goose-lang/primitive dependency")
    sys.exit(1)

if "github.com/goose-lang/std" not in content:
    print("FAIL: go.mod missing goose-lang/std dependency")
    sys.exit(1)

print("PASS: go.mod has required dependencies")
"""])
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_go_sum_deps_added():
    """go.sum must include checksums for goose-lang/primitive and goose-lang/std."""
    r = _run(["python3", "-c", f"""
import sys

with open("{REPO}/go.sum") as f:
    content = f.read()

if "github.com/goose-lang/primitive" not in content:
    print("FAIL: go.sum missing goose-lang/primitive checksums")
    sys.exit(1)

if "github.com/goose-lang/std" not in content:
    print("FAIL: go.sum missing goose-lang/std checksums")
    sys.exit(1)

print("PASS: go.sum has required checksums")
"""])
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_channel_model_created():
    """model/channel/channel.go must exist with Channel struct and methods."""
    r = _run(["python3", "-c", f"""
import sys
from pathlib import Path

channel_file = Path("{REPO}/model/channel/channel.go")
if not channel_file.exists():
    print("FAIL: model/channel/channel.go does not exist")
    sys.exit(1)

content = channel_file.read_text()

# Check for Channel struct
if "type Channel[T any] struct" not in content:
    print("FAIL: Channel struct not found")
    sys.exit(1)

# Check for key methods
required = [
    "func (c *Channel[T]) Send(",
    "func (c *Channel[T]) Receive(",
    "func (c *Channel[T]) Close(",
    "func (c *Channel[T]) TrySend(",
    "func (c *Channel[T]) TryReceive(",
    "func (c *Channel[T]) Len(",
    "func (c *Channel[T]) Cap(",
    "func NewChannelRef[T any](",
    "func Select1[",
    "func Select2[",
    "func Select3[",
    "func Select4[",
    "func Select5[",
]

for method in required:
    if method not in content:
        print(f"FAIL: Missing method: {{method}}")
        sys.exit(1)

print("PASS: channel.go exists with required structs and methods")
"""])
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_channel_readme_created():
    """model/channel/README.md must exist with documentation and state diagram."""
    r = _run(["python3", "-c", f"""
import sys
from pathlib import Path

readme_file = Path("{REPO}/model/channel/README.md")
if not readme_file.exists():
    print("FAIL: model/channel/README.md does not exist")
    sys.exit(1)

content = readme_file.read_text()

# Check for key documentation sections
required = [
    "channel",
    "generic",
    "buffer",
    "stateDiagram",
]

for text in required:
    if text not in content:
        print(f"FAIL: README missing: {{text}}")
        sys.exit(1)

print("PASS: README.md exists with documentation and state diagram")
"""])
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_go_build_succeeds():
    """Go code must compile without errors after adding channel model."""
    # First ensure dependencies are downloaded
    r = _run(["go", "mod", "tidy"], timeout=120)
    assert r.returncode == 0, f"go mod tidy failed: {r.stderr}"

    # Try to build the channel package
    r = _run(["go", "build", "./model/channel/..."], timeout=120)
    assert r.returncode == 0, f"Build failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + syntax checks
# ---------------------------------------------------------------------------


def test_go_syntax_valid():
    """Go files must have valid syntax."""
    r = _run(["go", "vet", "./..."], timeout=120)
    # Allow vet warnings but not syntax errors
    # A non-zero exit could be from vet warnings, not syntax errors
    # So we just check that gofmt doesn't report syntax errors
    r2 = _run(["gofmt", "-l", "."], timeout=60)
    assert r2.returncode == 0, f"gofmt failed: {r2.stderr}"


def test_not_stub():
    """channel.go must have substantial implementation, not just stubs."""
    r = _run(["python3", "-c", f"""
import sys
from pathlib import Path

channel_file = Path("{REPO}/model/channel/channel.go")
if not channel_file.exists():
    # If file doesn't exist, this test passes (it's a regression check)
    print("PASS: File doesn't exist yet, skipping content check")
    sys.exit(0)

content = channel_file.read_text()
lines = content.split("\\n")

# Check for substantial content
if len(lines) < 100:
    print(f"FAIL: channel.go too short ({{len(lines)}} lines), likely a stub")
    sys.exit(1)

# Check for function implementations (not just signatures)
if content.count("func ") < 10:
    print("FAIL: Too few functions, likely a stub")
    sys.exit(1)

# Check for actual logic (not just pass/panic)
non_trivial = ["for ", "if ", "switch ", "select"]
found_logic = any(kw in content for kw in non_trivial)
if not found_logic:
    print("FAIL: No control flow found, likely a stub")
    sys.exit(1)

print("PASS: channel.go has substantial implementation")
"""])
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
