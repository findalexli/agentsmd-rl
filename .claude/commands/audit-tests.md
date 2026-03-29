# Audit Tests

Review `harbor_tasks/$ARGUMENTS/tests/test.sh` for gaming resistance.

## Steps

1. **Read** test.sh, instruction.md, user_simulation_prompt.md
2. **Parse** every check: what it tests, points awarded, structural vs behavioral
3. **Answer 5 questions** with specific exploit code (not descriptions)
4. **Output** the report below (print, don't write files)

## The 5 Questions

1. **False Positive (0-10)**: Can agent score 1.0 without solving? Show exact exploit files.
2. **False Negative (0-10)**: Can correct solution score 0.0? Show the failing check.
3. **Gaming (0-10)**: Max score with stubs? Walk each check with `def f(): pass`.
4. **Specificity (0-10)**: Tested vs untested requirements table.
5. **Missing Coverage**: Top 3 untested functional requirements.

## Output Format

```markdown
## Test Audit: $ARGUMENTS
### Reliability Score: X/10
### Gaming Analysis
- Max stub score: X.XX
- Max comment-injection score: X.XX
### Question-by-Question
#### 1. False Positive: X/10  [exploit code]
#### 2. False Negative: X/10  [scenario]
#### 3. Gaming: X/10  [stubs + walk-through]
#### 4. Specificity: X/10  [tested | not tested]
#### 5. Missing Coverage  [top 3]
### Recommendations  [top 3 fixes]
### Weight: X% behavioral, Y% structural (target: ≥60% behavioral)
```

## Rules

- Show specific exploit code, not just risk descriptions
- Calculate exact gaming scores by walking each check
- Flag pure regex/string checks as always gameable
- Flag "warn but pass" patterns as critical bugs
