FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 99040b94e43d7e4b26d71c6f37edf7ce6781dc56 && \
    git checkout FETCH_HEAD

# Install deps needed for tests (PIL for image serialization tests)
RUN pip install --no-cache-dir numpy pydantic Pillow 2>/dev/null || true

ENV PYTHONPATH="/workspace/AReaL"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/AReaL