# Audit Tests

Review `harbor_tasks/$ARGUMENTS/tests/test.sh` for gaming resistance AND narrow-test problems.

## Steps

1. **Read** test.sh, instruction.md
2. **Parse** every check: what it tests, points awarded, structural vs behavioral
3. **Answer 7 questions** with specific exploit code (not descriptions)
4. **Output** the report below (print, don't write files)

## The 7 Questions

1. **False Positive (0-10)**: Can agent score 1.0 without solving? Show exact exploit files.
2. **False Negative (0-10)**: Can a CORRECT but differently-structured solution score 0.0? Show the failing check. (This is the OpenAI "narrow test" problem.)
3. **Gaming (0-10)**: Max score with stubs? Walk each check with `def f(): pass`.
4. **Specificity (0-10)**: Tested vs untested requirements table.
5. **Missing Coverage**: Top 3 untested functional requirements.
6. **Narrow Test Audit**: For each structural check, list 2 valid alternative implementations that would FAIL the check. If >30% of weighted score comes from narrow checks, flag as CRITICAL.
7. **Fail-to-Pass Coverage**: Does the test have at least one behavioral test that FAILS on the buggy code and PASSES on a correct fix? If not, flag as CRITICAL.

## Output Format

```markdown
## Test Audit: $ARGUMENTS
### Reliability Score: X/10
### Narrow Test Score: X/10 (10 = accepts all valid implementations, 0 = only gold patch passes)

### Gaming Analysis
- Max stub score: X.XX
- Max comment-injection score: X.XX

### Narrow Test Analysis (per OpenAI SWE-bench Verified critique)
| Check | Weight | Type | Narrow? | Alternative that would fail |
|-------|--------|------|---------|---------------------------|
| ... | ... | behavioral/structural | yes/no | ... |
Narrow-weighted score: X% (target: <=30%)

### Fail-to-Pass Coverage
- Has fail-to-pass behavioral test: yes/no
- Buggy baseline score: X.XX (should be >0 and <1.0)

### Question-by-Question
#### 1. False Positive: X/10  [exploit code]
#### 2. False Negative: X/10  [valid alternative that fails]
#### 3. Gaming: X/10  [stubs + walk-through]
#### 4. Specificity: X/10  [tested | not tested]
#### 5. Missing Coverage  [top 3]
#### 6. Narrow Tests  [per-check analysis]
#### 7. Fail-to-Pass  [coverage assessment]

### Recommendations  [top 3 fixes]
### Weight: X% behavioral, Y% structural (target: >=60% behavioral)
```

## Rules

- Show specific exploit code, not just risk descriptions
- Calculate exact gaming scores by walking each check
- Flag pure regex/string checks as always gameable
- Flag "warn but pass" patterns as critical bugs
- For EVERY structural check, think of 2 valid alternative implementations and check if they'd pass
- A test that only passes the gold patch is a BAD test, even if it catches the bug
