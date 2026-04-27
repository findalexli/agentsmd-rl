FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    GIT_TERMINAL_PROMPT=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1 PyYAML==6.0.2

WORKDIR /workspace

ARG REPO_URL=https://github.com/ant-design/ant-design.git
ARG BASE_COMMIT=fc13ea35e8245637a071f525484c9ffdedcdd4b7

RUN git init ant-design \
    && cd ant-design \
    && git remote add origin "$REPO_URL" \
    && git -c protocol.version=2 fetch --depth 1 --filter=blob:none origin "$BASE_COMMIT" \
    && git checkout "$BASE_COMMIT" \
    && git config user.email "task@example.com" \
    && git config user.name "Task Runner"

WORKDIR /workspace/ant-design

RUN mkdir -p /logs/verifier
