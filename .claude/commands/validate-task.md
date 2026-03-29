# Validate Task

Check instruction.md ↔ test.sh alignment and environment correctness for a PR-mined task.

Run AFTER `/write-tests` and `/audit-tests`.

## Inputs

`harbor_tasks/$ARGUMENTS/` must have: instruction.md, tests/test.sh, environment/Dockerfile, task.toml

## Steps

1. **Read instruction.md** -- what does it tell the agent to do?
2. **Read tests/test.sh** -- what does it actually verify? List every check and its weight.
3. **Read the source PR** (if noted in instruction.md or task.toml) -- what did the actual fix do?
4. **Compare** and answer these questions:

## Questions to Answer

### Q1: Does the instruction clearly describe a code modification task?
- Should describe a bug or feature request with enough context to act on
- Should point to the right file(s) or area of the codebase
- Should NOT reveal the exact fix (that would be leakage)

### Q2: Instruction ↔ Test reasonableness
The test should verify the FIX, not specific implementation details:
- Flag if the test requires a specific variable name not in the instruction
- Flag if the test requires a specific API (e.g., `setdefault` vs `if not in`) when alternatives are valid
- Flag if the test expects changes to files not mentioned or discoverable from the instruction
- Flag narrow tests that reject functionally correct alternatives (the OpenAI SWE-bench Verified problem)

### Q3: Fail-to-pass coverage
- Does the test include at least one BEHAVIORAL test that fails on buggy code and passes on correct fixes?
- Or is it purely structural (AST/text checks)?
- What % of tests are behavioral vs structural?

### Q4: Environment issues
- Does the Dockerfile clone the correct pre-fix commit?
- Are all Python deps needed by the test.sh installed?
- Does `allow_internet = true` in task.toml? (needed for agent installation)
- Can the test.sh run without importing modules that need torch/GPU?

### Q5: Verdict
- **PASS**: instruction is clear, tests are behavioral + implementation-agnostic, environment works
- **NARROW TESTS**: tests enforce specific implementation details -- rewrite with behavioral checks
- **NEEDS ENV FIX**: missing deps, wrong commit, or broken imports
- **LEAKS FIX**: instruction reveals too much about the expected solution

## Output Format

```markdown
## Task Validation: $ARGUMENTS

### Q1: Instruction Quality
Clear task? Sufficient context? No leakage?

### Q2: Test Narrowness Audit
| Check | Weight | Behavioral? | Accepts alternatives? |
|-------|--------|-------------|----------------------|
| ... | ... | yes/no | yes/no |

Behavioral %: X% (target: >=60%)

### Q3: Fail-to-Pass Coverage
- Buggy baseline score: X.XX (should be > 0 but < 1.0)
- Does buggy code fail behavioral tests? yes/no

### Q4: Environment Issues
- [ ] Correct base commit
- [ ] Deps installed for test.sh
- [ ] allow_internet = true
- [ ] No torch/GPU import chains in tests

### Q5: Verdict: PASS / NARROW TESTS / NEEDS ENV FIX / LEAKS FIX
Reason: ...
```

## Rules

- Do NOT read the Dockerfile for hints about the fix -- the agent won't see it
- Focus on what an agent reading ONLY instruction.md would understand
- The instruction being somewhat vague is OK -- the agent should explore the codebase
- Apply the OpenAI SWE-bench critique: would a functionally correct but differently-structured fix pass all tests?
