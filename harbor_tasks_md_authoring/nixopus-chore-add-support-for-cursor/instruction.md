# chore: add support for cursor rules

Source: [nixopus/nixopus#782](https://github.com/nixopus/nixopus/pull/782)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/backend.mdc`
- `.cursor/rules/frontend.mdc`
- `.cursor/rules/installer_cli.mdc`

## What to add / change

### **User description**
#### Issue
_Link to related issue(s):_  

---

#### Description
_Short summary of what this PR changes or introduces._

---

#### Scope of Change
_Select all applicable areas impacted by this PR:_

- [ ] View (UI/UX)
- [ ] API
- [ ] CLI
- [ ] Infra / Deployment
- [ ] Docs
- [ ] Other (specify): ________

---

#### Screenshot / Video / GIF (if applicable)
_Attach or embed screenshots, screen recordings, or GIFs demonstrating the feature or fix._

---

#### Related PRs (if any)
_Link any related or dependent PRs across repos._

---

#### Additional Notes for Reviewers (optional)
_Anything reviewers should know before testing or merging (e.g., environment variables, setup steps)._

---

#### Developer Checklist
_To be completed by the developer who raised the PR._

- [ ] Add valid/relevant title for the PR
- [ ] Self-review done  
- [ ] Manual dev testing done  
- [ ] No secrets exposed  
- [ ] No merge conflicts  
- [ ] Docs added/updated (if applicable)  
- [ ] Removed debug prints / secrets / sensitive data  
- [ ] Unit / Integration tests passing  
- [ ] Follows all standards defined in **Nixopus Docs**

---

#### Reviewer Checklist
_To be completed by the reviewer before merge._

- [ ] Peer review done  
- [ ] No console.logs / fmt.prints left  
- [ ] No secrets exposed  
- [ ] If any DB migrations, migration changes are verified
- [ ] Verified release changes are production-ready


___

###

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
