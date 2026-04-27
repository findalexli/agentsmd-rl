# fix(interview): add marketplace refresh step

Source: [Q00/ouroboros#138](https://github.com/Q00/ouroboros/pull/138)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/interview/SKILL.md`

## What to add / change

### Summary
- Add marketplace index refresh step (`claude plugin marketplace update ouroboros`) before plugin update in interview skill's update flow
- Fix plugin update command to `claude plugin update ouroboros@ouroboros`

### Testing
- `uv run pytest tests/unit/bigbang/test_interview.py tests/unit/mcp/tools/test_definitions.py`
  ```
  ❯ uv run pytest tests/unit/bigbang/test_interview.py 
        Built ouroboros-ai @ file:///home/jleem/projects/ouroboros
  Installed 103 packages in 64ms
  ============================================== test session starts ==============================================
  platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
  rootdir: /home/jleem/projects/ouroboros
  configfile: pyproject.toml
  plugins: asyncio-1.3.0, anyio-4.12.1, cov-7.0.0
  asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
  collected 43 items                                                                                              
  
  tests/unit/bigbang/test_interview.py ...........................................                          [100%]
  
  ============================================== 43 passed in 3.70s ===============================================
  ```
- Manual skill run
  
  <img width="926" height="514" alt="image" src="https://github.com/user-attachments/assets/a3ca8094-98a2-4895-8619-631b3ec4d954" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
