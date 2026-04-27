FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/claude-code-statusline && \
    cd /workspace/claude-code-statusline && \
    git remote add origin https://github.com/rz1989s/claude-code-statusline.git && \
    git fetch --depth=1 origin ab9d83010ff365453b90cac68590de40ed889eeb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/claude-code-statusline
