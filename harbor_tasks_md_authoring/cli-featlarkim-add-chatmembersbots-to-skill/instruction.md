# feat(lark-im): add chat.members.bots to skill

Source: [larksuite/cli#616](https://github.com/larksuite/cli/pull/616)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-im/SKILL.md`

## What to add / change

- Add chat.members.bots entry under chat.members API resources
  - Add chat.members.bots -> im:chat.members:read scope mapping

Change-Id: I57039a9a8649d794bbda84a1e41fae9cc31d570a

## Summary                                                                                                                                                                                                          
                                                                                                                                                                                                                      
  The `chat.members.bots` API is already registered in lark-cli but was missing                                                                                                                                       
  from the `lark-im` skill docs, so agents could not discover it when asked to
  list bots in a chat. This PR adds the entry and its required scope mapping so                                                                                                                                       
  the skill stays in sync with the registered API surface.
                                                                                                                                                                                                                      
  ## Changes      

  - Add `chat.members.bots` entry under the `chat.members` API resources 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
