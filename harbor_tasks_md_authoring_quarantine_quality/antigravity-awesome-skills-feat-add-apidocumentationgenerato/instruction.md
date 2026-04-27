# feat: add api-documentation-generator skill

Source: [sickn33/antigravity-awesome-skills#13](https://github.com/sickn33/antigravity-awesome-skills/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/api-documentation-generator/SKILL.md`

## What to add / change

This PR adds a new skill for generating comprehensive API documentation.

## What's Added

**New Skill:** `api-documentation-generator`

**Files:**
- `skills/api-documentation-generator/SKILL.md` - Main skill definition
- `skills/api-documentation-generator/README.md` - Additional documentation

## What This Skill Does

Helps developers create professional API documentation including:
- REST, GraphQL, and WebSocket API documentation
- Request/response examples in multiple languages (cURL, JavaScript, Python)
- Authentication and error handling documentation
- OpenAPI/Swagger specification generation
- Postman collection creation

## Why This Skill Is Useful

- Saves time writing API documentation manually
- Ensures consistent documentation format across endpoints
- Provides code examples in multiple programming languages
- Documents authentication, errors, and edge cases comprehensively
- Helps keep documentation in sync with code

## Skill Structure

- ✅ Proper frontmatter with name and description
- ✅ Clear overview and "When to Use" section
- ✅ Step-by-step "How It Works" guide
- ✅ 3 detailed examples (REST API, GraphQL, Authentication)
- ✅ Best practices (Do's and Don'ts)
- ✅ Common pitfalls with solutions
- ✅ Related skills and additional resources
- ✅ Passed validation script

## Testing

```bash
python3 scripts/validate_skills.py
```

Result: ✅ All validation checks passed

## Target Users

- Backend developers documentin

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
