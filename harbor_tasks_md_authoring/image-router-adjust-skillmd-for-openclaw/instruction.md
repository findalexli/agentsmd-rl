# Adjust SKILL.md for OpenClaw

Source: [DaWe35/image-router#57](https://github.com/DaWe35/image-router/pull/57)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

There are 2 things changed here:

1. The name of the skill. 
In the SKILL.md header it was `imagerouter` but skill was published as `image-router` to clawhub, that gives issues with env var mapping and some ambiguity. 
I decided to change the header to make it `image-router` with dash. Rationale is that search queries like `image` will (probably) better match dashed skill name.

2. Security hardening.
The api key env var was mentioned to be used directly in curl, so the model should know the api key to call the api. That's a huge issue primarily for you as nobody knows where those keys will leak later. This can impact your business as clients would see extra usage when (not if, but when) keys leak.

    I changed the api key to be used from env var which is properly provisioned to the OpenClaw gateway settings. Added a clause how to set it up - this includes skill name with dash, that is the reason for the change in point 1.

Of course I had tested on my OpenClaw installation until it worked.
It returns URLs to the chat, not images, but that's the limitation of OpenClaw at the moment.

Hope this will be helpful, contributing this PR as a gratitude for ImageRouter n8n node.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
