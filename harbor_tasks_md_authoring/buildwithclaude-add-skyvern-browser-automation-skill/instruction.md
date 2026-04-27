# Add Skyvern browser automation skill

Source: [davepoon/buildwithclaude#129](https://github.com/davepoon/buildwithclaude/pull/129)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/skyvern/SKILL.md`

## What to add / change

## Summary
            
  Add **Skyvern** — AI-powered browser automation skill for navigating sites, filling forms, extracting structured data, logging in with stored credentials, and building reusable multi-step workflows using natural language.                              
                                                                                        
  ## Component Details                                                               
                      
  - **Name**: skyvern
  - **Type**: Skill  
  - **Category**: browser-automation
                                    
  ## Testing
            
  - [x] Ran validation (`npm test`) — all passed
  - [x] No overlap with existing components     
                                           
  ## Examples                                                                           
             
  "Navigate to example.com and extract all product prices"                              
  "Log into my account and download the latest invoice"                                 
  "Build a workflow that runs this every Monday"                                        
                                                                                        
  ## Links                                                                              
                                                                                     
  - **Homepage**: https://www.skyvern.com                                        

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
