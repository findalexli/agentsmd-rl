# Gold Examples (Reference)

Study these validated tasks — match their structure exactly.

## Example 1: react-flight-blob-type-validation (12/12 quality score)

**Why it's perfect:** Every test executes real code (Jest via subprocess, JSON parsing), proper agent_config with verified source ref to `.claude/skills/extract-errors/SKILL.md`, no orphaned code, clean manifest.

- Full test file: [references/gold-test-react-flight.py](references/gold-test-react-flight.py)
- Full manifest: [references/gold-manifest-react-flight.yaml](references/gold-manifest-react-flight.yaml)

Key patterns to copy:
- `subprocess.run(["yarn", "test", ...])` — runs the repo's actual test runner
- `subprocess.run(["node", "--check", file])` — syntax gate
- `json.loads(codes_path.read_text())` — parses real data, asserts on content
- `origin: agent_config` with `source.path` pointing to SKILL.md at **base commit**

## Example 2: remix-routepattern-consistency-with-urlsearchparams (agentmd task)

**Why it's good:** Behavioral TypeScript execution via `node --experimental-strip-types`, imports real modules, checks JSON output, multiple input values.

- Full test file: [references/gold-test-remix-urlsearch.py](references/gold-test-remix-urlsearch.py)
- Full manifest: [references/gold-manifest-remix-urlsearch.yaml](references/gold-manifest-remix-urlsearch.yaml)

Key patterns to copy:
- `_run_ts(script)` helper — writes temp .ts file, executes with node, returns CompletedProcess
- `json.loads(result.stdout.strip())` — parses structured output
- Tests 3 different behaviors (key-only match, plus decoding, serialization)

## When grep is acceptable

Grep-only tests are acceptable ONLY when the language genuinely cannot be executed from Python:
- Svelte components (need a browser runtime)
- CUDA kernels (need GPU)
- Config files that need a running server

Even then, prefer compilation checks (`npx tsc --noEmit`, `cargo check`) over pure string matching.

## Common subprocess patterns by language

```python
# TypeScript/Node
def _run_ts(script, timeout=30):
    path = Path(REPO) / "_eval_tmp.ts"
    path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(path)],
            capture_output=True, text=True, timeout=timeout)
    finally:
        path.unlink(missing_ok=True)

# Rust
r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=120)

# Go
r = subprocess.run(["go", "build", "./..."], cwd=REPO, capture_output=True, timeout=120)

# Python (direct import)
from mymodule import my_function
result = my_function(input)
assert result == expected

# Jest/Vitest
r = subprocess.run(["yarn", "test", "--testPathPattern", "MyTest"], cwd=REPO, ...)

# Pytest (upstream)
r = subprocess.run(["python3", "-m", "pytest", "tests/test_foo.py", "-x"], cwd=REPO, ...)
```
