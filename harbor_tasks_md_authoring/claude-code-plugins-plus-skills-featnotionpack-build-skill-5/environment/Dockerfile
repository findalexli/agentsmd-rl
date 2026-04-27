FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-plugins-plus-skills && \
    cd /workspace/claude-code-plugins-plus-skills && \
    git remote add origin https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git && \
    git fetch --depth=1 origin 0c0895165a62344fd45db49581c282a174c3df75 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-plugins-plus-skills
