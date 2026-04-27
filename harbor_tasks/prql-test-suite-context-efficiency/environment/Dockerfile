FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pinned version of go-task (the `task` binary used by the Taskfile).
RUN curl -fsSL https://github.com/go-task/task/releases/download/v3.40.0/task_linux_amd64.tar.gz \
        -o /tmp/task.tar.gz \
    && tar -xzf /tmp/task.tar.gz -C /usr/local/bin task \
    && rm /tmp/task.tar.gz \
    && task --version

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-report==1.5.0 \
    pyyaml==6.0.2

# Clone PRQL/prql at the exact base commit (parent of the merge commit).
RUN mkdir -p /workspace/prql \
    && cd /workspace/prql \
    && git init -q \
    && git remote add origin https://github.com/PRQL/prql.git \
    && git fetch --depth=1 origin c3853a866993b199f92f6bd6bd0060a4f187e4e8 \
    && git checkout -q FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prql
