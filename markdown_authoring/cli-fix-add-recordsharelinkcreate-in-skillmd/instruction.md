# fix: add record-share-link-create in SKILL.md

Source: [larksuite/cli#597](https://github.com/larksuite/cli/pull/597)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-base/SKILL.md`

## What to add / change

Change-Id: Ie8dc96521ee692804b734b030f7c143171193eb9

## Summary                                                                                                                                                                
                                                                                                                                                                            
Add +record-share-link-create shortcut entry to lark-base SKILL.md so that AI agents can discover and use the record sharing capability.                                  
                                                                                                                                                                          
## Changes                                                                                                                                                                
                                                                                                                                                                          
• Added "记录分享" (record sharing) to the skill description                                                                                                              
• Added +record-share-link-create row in the Record sub-module table with usage notes                                                                                     
                                                                      

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
