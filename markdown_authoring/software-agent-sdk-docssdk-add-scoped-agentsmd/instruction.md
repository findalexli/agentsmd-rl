# docs(sdk): add scoped AGENTS.md

Source: [OpenHands/software-agent-sdk#2081](https://github.com/OpenHands/software-agent-sdk/pull/2081)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `openhands-sdk/openhands/sdk/AGENTS.md`

## What to add / change

Adds `openhands-sdk/openhands/sdk/AGENTS.md` following the structure suggested by the Codex `/init` prompt (concise repo-specific guidelines for structure, commands, style, testing, and PRs).
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
docker pull ghcr.io/openhands/agent-server:a3f1586-python
```

**Run**
```bash
docker run -it --rm \
  -p 8000:8000 \
  --name agent-server-a3f1586-python \
  ghcr.io/openhands/agent-server:a3f1586-python
```

**All tags pushed for this build**
```
ghcr.io/openhands/agent-server:a3f1586-golang-amd64
ghcr.io/openhands/agent-server:a3f1586-golang_tag_1.21-bookworm-amd64
ghcr.io/openhands/agent-server:a3f1586-golang-arm64
ghcr.io/openhands/agent-server:a3f1586-golang_tag_1.21-bookworm-arm64
ghcr.io/openhands/agent-server:a3f1586-java-amd64
ghcr.io/openhands/age

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
