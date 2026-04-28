FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ordinary-claude-skills && \
    cd /workspace/ordinary-claude-skills && \
    git remote add origin https://github.com/Microck/ordinary-claude-skills.git && \
    git fetch --depth=1 origin 3501f1db3a639b6608ac9e7a14c6c6683059596c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ordinary-claude-skills
