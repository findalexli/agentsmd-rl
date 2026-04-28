# docs: align AGENTS.md guidance across repo

Source: [OpenHands/software-agent-sdk#2087](https://github.com/OpenHands/software-agent-sdk/pull/2087)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `openhands-sdk/openhands/sdk/AGENTS.md`
- `openhands-tools/openhands/tools/AGENTS.md`
- `openhands-workspace/openhands/workspace/AGENTS.md`

## What to add / change

Aligns AGENTS.md guidance across the monorepo and package scopes:\n\n- Root AGENTS.md: clarify uv-managed monorepo structure + correct test path example\n- Package AGENTS.md (sdk/tools/workspace): rename to 'Package Guidelines' for clarity\n\nCo-authored-by: openhands <openhands@all-hands.dev>
<!-- AGENT_SERVER_IMAGES_START -->
---
**Agent Server images for this PR**

• **GHCR package:** https://github.com/OpenHands/agent-sdk/pkgs/container/agent-server

**Variants & Base Images**
| Variant | Architectures | Base Image | Docs / Tags |
|---|---|---|---|
| java | amd64, arm64 | `eclipse-temurin:17-jdk` | [Link](https://hub.docker.com/_/eclipse-temurin:17-jdk) |
| python | amd64, arm64 | `nikolaik/python-nodejs:python3.12-nodejs22` | [Link](https://hub.docker.com/_/nikolaik/python-nodejs:python3.12-nodejs22) |
| golang | amd64, arm64 | `golang:1.21-bookworm` | [Link](https://hub.docker.com/_/golang:1.21-bookworm) |


**Pull (multi-arch manifest)**
```bash
# Each variant is a multi-arch manifest supporting both amd64 and arm64
docker pull ghcr.io/openhands/agent-server:a7f4858-python
```

**Run**
```bash
docker run -it --rm \
  -p 8000:8000 \
  --name agent-server-a7f4858-python \
  ghcr.io/openhands/agent-server:a7f4858-python
```

**All tags pushed for this build**
```
ghcr.io/openhands/agent-server:a7f4858-golang-amd64
ghcr.io/openhands/agent-server:a7f4858-golang_tag_1.21-bookworm-amd64
ghcr.io/openhands/agent-server:a7f4858-golang-arm64
ghcr.io/openhands/agent-server:a7f4858

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
