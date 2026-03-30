# Validate Task

Final sign-off for a PR-mined task. Checks instruction quality, instruction ↔ test alignment, and environment correctness.

Run AFTER `/audit-tests` (which handles deep test quality analysis) and `/write-tests` (if tests were rewritten).

## Inputs

`harbor_tasks/$ARGUMENTS/` must have: instruction.md, tests/test.sh, environment/Dockerfile, task.toml

## Steps

1. **Read instruction.md** -- what does it tell the agent to do?
2. **Read tests/test.sh** -- list every check and its weight
3. **Read the source PR** (if noted in instruction.md or task.toml) -- what did the actual fix do?
4. **Answer** the questions below

## Questions to Answer

### Q1: Instruction Quality
- Describes a bug or feature request with enough context to act on?
- Points to the right file(s) or area of the codebase?
- Does NOT reveal the exact fix (that would be leakage)?

### Q2: Instruction ↔ Test Alignment
- Does the test verify something the instruction actually asks for?
- Does the test expect changes to files not mentioned or discoverable from the instruction?
- Would an agent reading ONLY instruction.md know what to fix?

### Q3: Environment Correctness
- Does the Dockerfile clone the correct pre-fix commit?
- Are all Python deps needed by test.sh installed?
- Does `allow_internet = true` in task.toml? (needed for agent installation)
- Can test.sh run without importing modules that need torch/GPU?

### Q4: Oracle Golden Patch Test
Build the Docker image and run the oracle (apply gold patch → run tests with LLM judge):
```bash
docker build -q -t harbor-$ARGUMENTS:latest harbor_tasks/$ARGUMENTS/environment/
docker run --rm --env-file /tmp/judge_env \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/solution:/solution \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/tests:/tests \
  -v $(pwd)/harbor_tasks/$ARGUMENTS/rubric.yaml:/rubric.yaml:ro \
  harbor-$ARGUMENTS:latest \
  bash -c "chmod +x /solution/solve.sh /tests/test.sh && /solution/solve.sh 2>/dev/null && /tests/test.sh"
```
- Deterministic score must be **1.0** (gold patch passes all tests)
- If LLM judge is enabled, ICR must be **>=0.9** (rubric rules should pass on gold patch)
- If ICR < 0.9, identify which rules fail and fix the rubric — a rule that fails on the gold patch is too subjective

### Q5: Verdict
- **PASS**: instruction clear, tests aligned, environment works, oracle scores 1.0
- **NEEDS ENV FIX**: missing deps, wrong commit, or broken imports
- **LEAKS FIX**: instruction reveals too much about the expected solution
- **MISALIGNED**: tests verify something the instruction doesn't describe
- **RUBRIC FAIL**: gold patch fails rubric rules — fix rubric.yaml

## Output Format

```markdown
## Task Validation: $ARGUMENTS

### Q1: Instruction Quality
Clear task? Sufficient context? No leakage?

### Q2: Instruction ↔ Test Alignment
Does the test match what the instruction asks?

### Q3: Environment Issues
- [ ] Correct base commit
- [ ] Deps installed for test.sh
- [ ] allow_internet = true
- [ ] No torch/GPU import chains in tests

### Q4: Verdict: PASS / NEEDS ENV FIX / LEAKS FIX / MISALIGNED
Reason: ...
```

## Rules

- Do NOT redo the test narrowness/gaming analysis -- that's `/audit-tests`
- Do NOT read the Dockerfile for hints about the fix -- the agent won't see it
- Focus on what an agent reading ONLY instruction.md would understand
- The instruction being somewhat vague is OK -- the agent should explore the codebase
